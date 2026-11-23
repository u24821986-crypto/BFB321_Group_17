import os
import sqlite3
from datetime import datetime

from flask import Blueprint, jsonify, request

from models.harvest_model import calculate_harvest_rate
from models.transport_model import evaluate_capacity_deficit



api_bp = Blueprint('api', __name__)

# Database file lives next to your app. Override with SQLITE_PATH if you like.
DB_PATH = os.getenv(
    "SQLITE_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartharvest.db"),
)

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

try:
    from zoneinfo import ZoneInfo
    _TZ = ZoneInfo("Africa/Johannesburg")
except Exception:  # tz database missing: fall back to UTC+2
    from datetime import timezone, timedelta
    _TZ = timezone(timedelta(hours=2))

def _now():
    return datetime.now(_TZ)

def today():
    return _now().strftime("%Y-%m-%d")

def now_time():
    return _now().strftime("%H:%M")

def when(data):
    """Date/time from the form, or South African 'now' if left empty."""
    day = data.get("DateHarvested") or today()
    time = data.get("TimeHarvested") or data.get("time") or now_time()
    return day, str(time)[:5]

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, clock_in TEXT, clock_out TEXT,
            leader TEXT, block TEXT, workers INTEGER);
        CREATE TABLE IF NOT EXISTS harvests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER, date TEXT, time TEXT,
            crates INTEGER, trees INTEGER, rejected INTEGER);
        CREATE TABLE IF NOT EXISTS logistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, time TEXT, trip INTEGER, vehicle TEXT,
            registration TEXT, driver TEXT, destination TEXT, block TEXT,
            loaded INTEGER, delivered INTEGER);
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, time TEXT, block TEXT,
            end_crates INTEGER, delays TEXT, remarks TEXT);
    """)
    if conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0] == 0:
        d = today()
        conn.executemany(
            "INSERT INTO teams (date, clock_in, clock_out, leader, block, workers) VALUES (?,?,?,?,?,?)",
            [(d, "06:00", "14:00", "Thabo M.", "Block 1", 12),
             (d, "07:00", "15:00", "Lerato K.", "Block 2", 10)])
        conn.executemany(
            "INSERT INTO harvests (team_id, date, time, crates, trees, rejected) VALUES (?,?,?,?,?,?)",
            [(1, d, "08:30", 120, 60, 5), (1, d, "10:30", 140, 70, 8),
             (2, d, "09:30", 110, 55, 4), (2, d, "11:30", 130, 65, 6)])
        conn.execute(
            "INSERT INTO logistics (date, time, trip, vehicle, registration, driver, destination, block, loaded, delivered)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (d, "11:00", 1, "Truck", "ABC 123 GP", "Sipho N.", "Pack house", "Block 1", 200, 198))
        conn.execute(
            "INSERT INTO notes (date, time, block, end_crates, delays, remarks) VALUES (?,?,?,?,?,?)",
            (d, "12:00", "Block 1", 40, "None", "Sample data - replace by submitting the forms"))
        conn.commit()
    conn.close()

init_db()

def hours_between(start, end):
    try:
        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(end, "%H:%M")
        return round((e - s).seconds / 3600, 1)
    except Exception:
        return None

def to_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default

def pick(data, *keys, default=None):
    for k in keys:
        if data.get(k) not in (None, ""):
            return data[k]
    return default

def norm_block(value):
    """'Block1' -> 'Block 1'"""
    if not value:
        return None
    digits = ''.join(ch for ch in str(value) if ch.isdigit())
    return f"Block {digits}" if digits else str(value)


# --- DASHBOARD (GET) ---
@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    block_param = request.args.get('block', 'all')
    date_param = request.args.get('date') or today()
    block_name = None if block_param in (None, '', 'all') else norm_block(block_param)

    conn = None
    try:
        conn = get_db()
        bf = " AND t.block = ?" if block_name else ""
        bp = [block_name] if block_name else []

        rows = conn.execute(f"""
            SELECT t.id, t.clock_in, t.clock_out, t.leader, t.block, t.workers,
                   COALESCE(SUM(h.crates),0) crates, COALESCE(SUM(h.rejected),0) rejected,
                   COALESCE(SUM(h.trees),0) trees
            FROM teams t LEFT JOIN harvests h ON h.team_id = t.id
            WHERE t.date = ? {bf}
            GROUP BY t.id ORDER BY t.clock_in""", [date_param] + bp).fetchall()
        
        shift_overview = [{
            "start": r["clock_in"], "end": r["clock_out"] or "--:--",
            "hours": hours_between(r["clock_in"], r["clock_out"]),
            "leader": r["leader"], "block": r["block"], "workers": r["workers"],
            "crates": r["crates"], "rejected": r["rejected"], "trees": r["trees"],
        } for r in rows]

        rows = conn.execute(f"""
            SELECT h.time, t.leader, t.block, t.workers, h.crates, h.trees, h.rejected
            FROM harvests h JOIN teams t ON t.id = h.team_id
            WHERE h.date = ? {bf} ORDER BY h.time""", [date_param] + bp).fetchall()
        
        operations = [dict(r) for r in rows]

        bf2 = " AND block = ?" if block_name else ""
        rows = conn.execute(
            f"SELECT * FROM logistics WHERE date = ? {bf2} ORDER BY time", [date_param] + bp).fetchall()
        
        logistics = [{
            "time": r["time"], "trip": r["trip"], "vehicle": r["vehicle"],
            "registration": r["registration"], "driver": r["driver"],
            "destination": r["destination"], "loaded": r["loaded"], "delivered": r["delivered"],
        } for r in rows]

        rows = conn.execute(
            f"SELECT * FROM notes WHERE date = ? {bf2} ORDER BY time DESC, id DESC",
            [date_param] + bp).fetchall()
        
        notes = [{"endCrates": r["end_crates"], "delays": r["delays"], "remarks": r["remarks"]}
                 for r in rows]

        harvested = sum(r["crates"] for r in shift_overview)
        loaded = sum(r["loaded"] or 0 for r in logistics)
        awaiting = max(harvested - loaded, 0)

        # Supply Chain Model Integration
        total_labor_hours = sum(r["hours"] or 0.0 for r in shift_overview)
        
        if total_labor_hours > 0:
            harvest_rate = round(calculate_harvest_rate(float(harvested), float(total_labor_hours)), 2)
        else:
            harvest_rate = 0.0

        # 
        # TRANSPORT MODEL INTEGRATION: CAPACITY DEFICIT
        # 
        available_capacity = 200

        capacity_analysis = evaluate_capacity_deficit(
            projected_crates=int(awaiting),
            available_capacity=int(available_capacity)
        )


        

        shift_end = notes[0]["endCrates"] if notes else awaiting

        # FIXED: Using a single dictionary to track destinations
        dest_counts = {"Pack house": 0, "Farm shed": 0, "Other": 0}
        for r in logistics:
            key = r["destination"] if r["destination"] in dest_counts else "Other"
            dest_counts[key] += r["delivered"] or 0

        # 
        # FORMAT CHARTS EXPECTED BY DASHBOARD.HTML
        # 
        # Build harvestChart data
        harvest_chart_labels = [
            f"{r.get('leader') or r.get('team', 'Team')} ({r.get('start', '')})"
            for r in shift_overview
        ]
        harvest_chart_values = [r.get("crates", 0) for r in shift_overview]
    
        # Build destinationChart totals
        dest_counts = {"Pack house": 0, "Farm shed": 0, "Other": 0}
        for r in logistics:
            dest = r.get("destination", "Other")
            key = dest if dest in dest_counts else "Other"
            dest_counts[key] += r.get("delivered") or r.get("loaded") or 0
    
        # 
        # RETURN COMPLETE JSON PAYLOAD
        # 
        return jsonify({
            # Standard KPIs + Injected Step 2 Harvest Rate
            "kpis": {
                "harvestedToday": harvested,
                "awaitingTransport": awaiting,
                "shiftEnd": shift_end,
                "harvestRate": harvest_rate
            },
    
            # Step 2 Analytical Evidence (Rubric B3)
            "analytics": {
                "harvestRate": {
                    "value": harvest_rate,
                    "unit": "crates/hour",
                    "totalHoursWorked": round(total_labor_hours, 2),
                    "modelSource": "models.harvest_model.calculate_harvest_rate"
                },
                "transportCapacity": {
                    "hasDeficit": capacity_analysis["has_deficit"],
                    "capacityGap": capacity_analysis["capacity_gap"],
                    "message": capacity_analysis["message"],
                    "availableCapacity": available_capacity,
                    "modelSource": "models.transport_model.evaluate_capacity_deficit"
                }
            },

            # REQUIRED BY DASHBOARD.HTML (fixes the crash):
            "harvestChart": {
                "labels": harvest_chart_labels,
                "values": harvest_chart_values
            },
            "destinationChart": {
                "labels": list(dest_counts.keys()),
                "values": list(dest_counts.values())
            },
    
            # Retain flat keys for backwards compatibility
            "destinationLabels": list(dest_counts.keys()),
            "destinationValues": list(dest_counts.values()),
    
            # Tables
            "shiftOverview": shift_overview,
            "operations": operations,
            "logistics": logistics,
            "notes": notes
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# --- TEAM (POST): Clock In adds a team, Clock Out closes it ---
@api_bp.route('/team', methods=['POST'])
def save_team_info():
    data = request.get_json(silent=True)
    if not data or not str(data.get('teamInfo', '')).strip():
        return jsonify({"error": "Missing team leader name", "message": "Missing team leader name"}), 400
    leader = data['teamInfo'].strip()
    day, time = when(data)
    block = norm_block(data.get('operationBlock')) or "Block 1"
    conn = None
    try:
        conn = get_db()
        if data.get('shiftPeriod') == "Clockout":
            cur = conn.execute(
                "UPDATE teams SET clock_out = ? WHERE leader = ? AND block = ? AND date = ? AND clock_out IS NULL",
                (time, leader, block, day))
            conn.commit()
            if cur.rowcount == 0:
                msg = "No clocked-in team found for that leader, block and date"
                return jsonify({"error": msg, "message": msg}), 400
            return jsonify({"status": "success", "message": "Clocked out"}), 201
        conn.execute(
            "INSERT INTO teams (date, clock_in, leader, block, workers) VALUES (?,?,?,?,?)",
            (day, time, leader, block, to_int(data.get('NumOfWorkers'))))
        conn.commit()
        return jsonify({"status": "success", "message": "Team clocked in"}), 201
    except Exception as e:
        return jsonify({"error": str(e), "message": str(e)}), 500
    finally:
        if conn:
            conn.close()


# --- HARVEST (POST) ---
@api_bp.route('/harvest', methods=['POST'])
def save_harvest():
    data = request.get_json(silent=True)
    if not data or data.get('CratesHarvested') in (None, ""):
        return jsonify({"error": "Missing crates harvested", "message": "Missing crates harvested"}), 400
    day, time = when(data)
    leader = str(data.get('Team') or "Unassigned").strip()
    conn = None
    try:
        conn = get_db()
        team = conn.execute(
            "SELECT id FROM teams WHERE leader = ? AND date = ? ORDER BY id DESC LIMIT 1",
            (leader, day)).fetchone()
        if team:
            team_id = team["id"]
        else:  # leader not clocked in yet: create the team so nothing is lost
            team_id = conn.execute(
                "INSERT INTO teams (date, clock_in, leader, block, workers) VALUES (?,?,?,?,?)",
                (day, time, leader, norm_block(data.get('operationBlock')) or "Block 1", 0)).lastrowid
        conn.execute(
            "INSERT INTO harvests (team_id, date, time, crates, trees, rejected) VALUES (?,?,?,?,?,?)",
            (team_id, day, time, to_int(data.get('CratesHarvested')),
             to_int(data.get('NumOfTrees')), to_int(data.get('RejectedCrates'))))
        conn.commit()
        return jsonify({"status": "success", "message": "Harvest saved. It will now show on the dashboard."}), 201
    except Exception as e:
        return jsonify({"error": str(e), "message": str(e)}), 500
    finally:
        if conn:
            conn.close()


# --- LOGISTICS (POST) ---
@api_bp.route('/logistics', methods=['POST'])
def save_logistics():
    data = request.get_json(silent=True)
    if not data or data.get('tripNumber') in (None, ""):
        return jsonify({"error": "Missing trip number", "message": "Missing trip number"}), 400
    day, time = when(data)
    dest = {"PackHouse": "Pack house", "FarmShed": "Farm shed"}.get(
        data.get('destination'), data.get('destination') or "Other")
    conn = None
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO logistics (date, time, trip, vehicle, registration, driver, destination, block, loaded, delivered)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (day, time, to_int(data.get('tripNumber')), data.get('vehicleType'),
             data.get('vehicleInfo'), data.get('driverInfo'), dest,
             norm_block(data.get('operationBlock')) or "Block 1",
             to_int(data.get('numCrates')), to_int(data.get('numCratesDest'))))
        conn.commit()
        return jsonify({"status": "success", "message": "Trip saved. It will now show on the dashboard."}), 201
    except Exception as e:
        return jsonify({"error": str(e), "message": str(e)}), 500
    finally:
        if conn:
            conn.close()


# --- NOTES (POST) ---
@api_bp.route('/notes', methods=['POST'])
def save_notes():
    data = request.get_json(silent=True)
    if not data or data.get('endShiftCrates') in (None, ""):
        return jsonify({"error": "Missing end shift crates", "message": "Missing end shift crates"}), 400
    day, time = when(data)
    conn = None
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO notes (date, time, block, end_crates, delays, remarks) VALUES (?,?,?,?,?,?)",
            (day, time, norm_block(data.get('operationBlock')) or "Block 1",
             to_int(data.get('endShiftCrates')),
             data.get('delaysInfo', ''), data.get('remarksInfo', '')))
        conn.commit()
        return jsonify({"status": "success", "message": "Notes saved. They will now show on the dashboard."}), 201
    except Exception as e:
        return jsonify({"error": str(e), "message": str(e)}), 500
    finally:
        if conn:
            conn.close()


# --- GET ALL HARVESTS (pagination + filtering) ---
@api_bp.route('/harvests', methods=['GET'])
def get_all_harvests():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    block = request.args.get('block', default=None, type=str)
    conn = get_db()
    try:
        sql = ("SELECT h.id, t.block, h.crates FROM harvests h JOIN teams t ON t.id = h.team_id")
        params = []
        if block:
            sql += " WHERE t.block = ?"
            params.append(norm_block(block))
        rows = [dict(r) for r in conn.execute(sql + " ORDER BY h.id", params).fetchall()]
    finally:
        conn.close()
    start = (page - 1) * limit
    return jsonify({"page": page, "limit": limit, "total_results": len(rows),
                    "data": rows[start:start + limit]}), 200


# --- UPDATE HARVEST (PUT) ---
@api_bp.route('/harvest/<int:harvest_id>', methods=['PUT'])
def update_harvest(harvest_id):
    data = request.get_json(silent=True)
    if not data or 'CratesHarvested' not in data:
        return jsonify({"error": "Missing crates harvested data"}), 400
    conn = get_db()
    try:
        cur = conn.execute("UPDATE harvests SET crates = ? WHERE id = ?",
                           (to_int(data['CratesHarvested']), harvest_id))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Harvest not found"}), 404
    finally:
        conn.close()
    return jsonify({"status": "success",
                    "message": f"Harvest record {harvest_id} updated successfully"}), 200

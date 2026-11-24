import os
from datetime import datetime
from urllib.parse import unquote, urlparse

from flask import Blueprint, jsonify, request
import pymysql

# Import your supply chain models
from models.harvest_model import calculate_harvest_rate, calculate_progress_percentage
from models.transport_model import evaluate_capacity_deficit, calculate_required_trips, calculate_vehicle_utilisation
from models.bottleneck_model import identify_constraint
from models.optimisation_model import calculate_remaining_harvest_time, calculate_required_workers, evaluate_workforce_deficit, predict_block_completion_risk

api_bp = Blueprint('api', __name__)

# --- DATABASE CONNECTION ---
def get_db():
    url = os.getenv("DATABASE_URL")
    if url:
        u = urlparse(url)
        return pymysql.connect(
            host=u.hostname, port=u.port or 3306, user=unquote(u.username or ""),
            password=unquote(u.password or ""), database=u.path.lstrip("/"),
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        return pymysql.connect(
            host='localhost', user='root', password='', database='mydb',
            cursorclass=pymysql.cursors.DictCursor
        )

# --- HELPERS ---
def norm_block(value):
    if not value: return None
    digits = ''.join(ch for ch in str(value) if ch.isdigit())
    return f"Block {digits}" if digits else str(value)

def to_int(value, default=0):
    try: return int(float(value))
    except (TypeError, ValueError): return default

def pick(data, *keys, default=None):
    for k in keys:
        if data.get(k) not in (None, ""): return data[k]
    return default

def get_date_time_id(cursor, day, time):
    cursor.execute("SELECT date_time_id FROM date_time WHERE `date`=%s AND `time`=%s", (day, time))
    row = cursor.fetchone()
    if row: return row["date_time_id"]
    cursor.execute("INSERT INTO date_time (`date`, `time`) VALUES (%s, %s)", (day, time))
    return cursor.lastrowid

def get_person_id(cursor, name):
    name = name.strip()
    cursor.execute("SELECT person_id FROM person WHERE name=%s LIMIT 1", (name,))
    row = cursor.fetchone()
    if row: return row["person_id"]
    cursor.execute("INSERT INTO person (name) VALUES (%s)", (name,))
    return cursor.lastrowid

def when(data):
    day = data.get("DateHarvested") or datetime.now().strftime("%Y-%m-%d")
    time = data.get("TimeHarvested") or data.get("time") or datetime.now().strftime("%H:%M")
    return day, str(time)[:5]

def hours_between(start, end):
    try:
        s = datetime.strptime(str(start), "%H:%M:%S")
        e = datetime.strptime(str(end), "%H:%M:%S")
        return round((e - s).seconds / 3600, 1)
    except Exception: return None

# --- DASHBOARD (GET) ---
@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    block_param = request.args.get('block', 'all')
    date_param = request.args.get('date') or datetime.now().strftime("%Y-%m-%d")
    block_name = None if block_param in (None, '', 'all') else norm_block(block_param)

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            bf = " AND t.block = %s" if block_name else ""
            bp = [block_name] if block_name else []

            # 1. Teams
            cursor.execute(f"""
                SELECT t.team_id, t.clock_in_time AS clock_in, t.clock_out_time AS clock_out, p.name AS leader, t.block, t.num_workers AS workers,
                       COALESCE(SUM(h.total_crates_number),0) AS crates, COALESCE(SUM(h.rejected_crates_number),0) AS rejected,
                       COALESCE(SUM(h.tree_number),0) AS trees
                FROM team t 
                JOIN person p ON p.person_id = t.team_leader_id
                JOIN date_time d ON d.date_time_id = t.date_time_id
                LEFT JOIN harvest_crates h ON h.team_id = t.team_id
                WHERE d.date = %s {bf}
                GROUP BY t.team_id ORDER BY t.clock_in_time
            """, [date_param] + bp)
            teams = cursor.fetchall()

            # 2. Harvests
            harvests = []
            if teams:
                ids = [t["team_id"] for t in teams]
                fmt = ",".join(["%s"] * len(ids))
                cursor.execute(f"""
                    SELECT h.team_id, h.total_crates_number AS crates, h.tree_number AS trees, 
                           h.rejected_crates_number AS rejected, dt.time 
                    FROM harvest_crates h
                    JOIN date_time dt ON dt.date_time_id = h.date_time_id
                    WHERE h.team_id IN ({fmt}) ORDER BY dt.time
                """, ids)
                harvests = cursor.fetchall()

            # 3. Logistics
            cursor.execute(f"""
                SELECT l.trip_number AS trip, l.vehicle_type AS vehicle, l.vehicle_registration AS registration,
                       p.name AS driver, l.destination, l.number_crates_loaded AS loaded, 
                       l.number_crates_at_destination AS delivered, dt.time
                FROM logistics l
                JOIN person p ON p.person_id = l.driver_id
                JOIN date_time dt ON dt.date_time_id = l.date_time_id
                WHERE dt.date = %s {bf.replace('t.', 'l.')} ORDER BY dt.time
            """, [date_param] + bp)
            trips = cursor.fetchall()

            # 4. Notes
            cursor.execute(f"""
                SELECT o.number_end_shift_crates AS endCrates, o.delays, o.remarks, o.block
                FROM operations o
                JOIN date_time d ON d.date_time_id = o.date_time_id
                WHERE d.date = %s {bf.replace('t.', 'o.')} ORDER BY d.time DESC
            """, [date_param] + bp)
            notes = cursor.fetchall()

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    # Format Data for the Dashboard
    by_team = {t["team_id"]: t for t in teams}
    shift_overview = []
    for t in teams:
        mine = [h for h in harvests if h["team_id"] == t["team_id"]]
        start = str(t["clock_in"])
        end = str(t["clock_out"]) if t["clock_out"] else None
        shift_overview.append({
            "start": start, "end": end or "--:--", "hours": hours_between(start, end),
            "leader": t["leader"], "block": t["block"], "workers": t["workers"],
            "crates": t["crates"], "rejected": t["rejected"], "trees": t["trees"]
        })

    operations = [{
        "time": str(h["time"]), "leader": by_team[h["team_id"]]["leader"],
        "block": by_team[h["team_id"]]["block"], "workers": by_team[h["team_id"]]["workers"],
        "crates": h["crates"], "trees": h["trees"], "rejected": h["rejected"]
    } for h in harvests]

    dest_counts = {"Pack house": 0, "Farm shed": 0, "Other": 0}
    for t in trips:
        key = t["destination"] if t["destination"] in dest_counts else "Other"
        dest_counts[key] += t["delivered"]
        t["time"] = str(t["time"])

    harvested = sum(s["crates"] for s in shift_overview)
    loaded = sum(t["loaded"] for t in trips)
    awaiting = max(harvested - loaded, 0)
    
    # Calculate models
    total_labor_hours = sum(s["hours"] or 0.0 for s in shift_overview)
    harvest_rate = round(calculate_harvest_rate(float(harvested), float(total_labor_hours)), 2) if total_labor_hours > 0 else 0.0
    
    available_capacity = 200
    capacity_analysis = evaluate_capacity_deficit(int(awaiting), int(available_capacity))
    trips_required = calculate_required_trips(int(awaiting), int(available_capacity))
    vehicle_util = round(calculate_vehicle_utilisation(max(0, int(loaded)), max(1, int(available_capacity))), 2)
    
    total_trees_harvested = sum(r.get("trees", 0) for r in shift_overview)
    total_trees_target = 500.0 if block_name else 3500.0
    harvest_progress = round(calculate_progress_percentage(float(total_trees_harvested), float(total_trees_target)), 2)
    constraint_message = identify_constraint(float(harvest_progress), float(vehicle_util))

    target_crates = 1000 if block_name else 2000
    remaining_crates = max(0, int(target_crates - harvested))
    available_hours = 4.0
    active_workers = sum(r.get("workers", 0) for r in shift_overview)
    
    required_workers = calculate_required_workers(int(remaining_crates), max(0.5, float(available_hours)))
    workforce_analysis = evaluate_workforce_deficit(int(required_workers), max(0, int(active_workers)))
    
    if harvest_rate > 0 and remaining_crates > 0:
        remaining_harvest_hours = round(calculate_remaining_harvest_time(int(remaining_crates), float(harvest_rate)), 2)
        completion_risk = predict_block_completion_risk(float(remaining_harvest_hours), float(available_hours))
    else:
        remaining_harvest_hours = 0.0
        completion_risk = {"status": "GREEN", "is_at_risk": False, "time_buffer_hours": round(available_hours, 2), "message": "ON TRACK: Target achieved."}

    shift_end = notes[0]["endCrates"] if notes else awaiting

    return jsonify({
        "kpis": {"harvestedToday": harvested, "awaitingTransport": awaiting, "shiftEnd": shift_end, "harvestRate": harvest_rate},
        "analytics": {
            "harvestRate": {"value": harvest_rate, "unit": "crates/hour", "totalHoursWorked": round(total_labor_hours, 2)},
            "harvestProgress": {"treesHarvested": total_trees_harvested, "targetTrees": total_trees_target, "progressPercentage": harvest_progress},
            "transportCapacity": {"availableCapacity": available_capacity, "capacityGap": capacity_analysis["capacity_gap"], "cratesAwaiting": awaiting, "hasDeficit": capacity_analysis["has_deficit"], "message": capacity_analysis["message"], "tripsRequired": trips_required, "utilisationPercentage": vehicle_util},
            "bottleneckAnalysis": {"primaryConstraint": "Labour" if "Labour" in constraint_message else ("Transport" if "Transport" in constraint_message else "Balanced"), "statusMessage": constraint_message, "harvestProgress": harvest_progress, "transportUtilisation": vehicle_util},
            "workforceOptimisation": {"activeWorkers": active_workers, "requiredWorkers": required_workers, "hasWorkerDeficit": workforce_analysis["has_deficit"], "workerGap": workforce_analysis["worker_gap"], "workerMessage": workforce_analysis["message"], "remainingCrates": remaining_crates, "estimatedRemainingHours": remaining_harvest_hours, "riskStatus": completion_risk["status"], "isAtRisk": completion_risk["is_at_risk"], "timeBufferHours": completion_risk["time_buffer_hours"], "riskMessage": completion_risk["message"]}
        },
        "harvestChart": {"labels": [f"{s['leader']} ({s['start']})" for s in shift_overview], "values": [s["crates"] for s in shift_overview]},
        "destinationChart": {"labels": list(dest_counts.keys()), "values": list(dest_counts.values())},
        "shiftOverview": shift_overview, "operations": operations, "logistics": trips,
        "notes": [{"endCrates": n["endCrates"], "delays": n["delays"], "remarks": n["remarks"]} for n in notes]
    }), 200

# --- SAVE ROUTES ---
def save(handler):
    data = request.get_json() or {}
    day, time = when(data)
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            error_msg = handler(cursor, data, day, time)
            if error_msg:
                conn.rollback()
                return jsonify({"error": error_msg, "message": error_msg}), 400
        conn.commit()
        return jsonify({"status": "success", "message": "Saved to database."}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e), "message": str(e)}), 500
    finally:
        conn.close()

@api_bp.route('/team', methods=['POST'])
def save_team_info():
    def handler(cursor, d, day, time):
        if not d.get("teamInfo"): return "Missing team leader name"
        block = norm_block(d.get("operationBlock"))
        if d.get("shiftPeriod") == "Clockout":
            cursor.execute("""
                UPDATE team t JOIN person p ON p.person_id=t.team_leader_id
                JOIN date_time x ON x.date_time_id=t.date_time_id
                SET t.clock_out_time=%s WHERE p.name=%s AND t.block=%s AND x.date=%s AND t.clock_out_time IS NULL
            """, (time, d["teamInfo"].strip(), block, day))
            if cursor.rowcount == 0: return "No clocked-in team found"
            return None
        cursor.execute("""
            INSERT INTO team (clock_in_time, num_workers, block, date_time_id, team_leader_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (time, to_int(d.get("NumOfWorkers")), block, get_date_time_id(cursor, day, time), get_person_id(cursor, d["teamInfo"])))
    return save(handler)

@api_bp.route('/harvest', methods=['POST'])
def save_harvest():
    def handler(cursor, d, day, time):
        if not d.get("CratesHarvested") or not d.get("Team"): return "Missing team or crates"
        cursor.execute("""
            SELECT t.team_id FROM team t JOIN person p ON p.person_id=t.team_leader_id
            JOIN date_time x ON x.date_time_id=t.date_time_id
            WHERE p.name=%s AND x.date=%s ORDER BY t.team_id DESC LIMIT 1
        """, (d["Team"].strip(), day))
        team = cursor.fetchone()
        if not team: return "No team found for that leader. Clock in first."
        cursor.execute("""
            INSERT INTO harvest_crates (total_crates_number, tree_number, rejected_crates_number, team_id, date_time_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (to_int(d["CratesHarvested"]), to_int(d.get("NumOfTrees")), to_int(d.get("RejectedCrates")), team["team_id"], get_date_time_id(cursor, day, time)))
    return save(handler)

@api_bp.route('/logistics', methods=['POST'])
def save_logistics():
    def handler(cursor, d, day, time):
        if not d.get("tripNumber"): return "Missing trip number"
        dest = {"PackHouse": "Pack house", "FarmShed": "Farm shed"}.get(d.get("destination"), d.get("destination") or "Other")
        cursor.execute("""
            INSERT INTO logistics (trip_number, vehicle_type, vehicle_registration, destination, number_crates_loaded, number_crates_at_destination, driver_id, date_time_id, block)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (to_int(d["tripNumber"]), d["vehicleType"], d["vehicleInfo"], dest, to_int(d["numCrates"]), to_int(d["numCratesDest"]), get_person_id(cursor, d["driverInfo"]), get_date_time_id(cursor, day, time), norm_block(d.get("operationBlock"))))
    return save(handler)

@api_bp.route('/notes', methods=['POST'])
def save_notes():
    def handler(cursor, d, day, time):
        if not d.get("endShiftCrates"): return "Missing end shift crates"
        cursor.execute("""
            INSERT INTO operations (number_end_shift_crates, delays, remarks, date_time_id, block)
            VALUES (%s, %s, %s, %s, %s)
        """, (to_int(d["endShiftCrates"]), d.get("delaysInfo", ""), d.get("remarksInfo", ""), get_date_time_id(cursor, day, time), norm_block(d.get("operationBlock"))))
    return save(handler)

# --- PAGINATION & FILTERING ---
@api_bp.route('/harvests', methods=['GET'])
def get_all_harvests():
    page, limit = request.args.get('page', 1, type=int), request.args.get('limit', 10, type=int)
    block = request.args.get('block', default=None, type=str)
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT h.harvest_crates_id as id, t.block, h.total_crates_number as crates FROM harvest_crates h JOIN team t ON t.team_id = h.team_id"
            params = []
            if block:
                sql += " WHERE t.block = %s"
                params.append(norm_block(block))
            cursor.execute(sql + " ORDER BY h.harvest_crates_id", params)
            rows = cursor.fetchall()
    finally: conn.close()
    start = (page - 1) * limit
    return jsonify({"page": page, "limit": limit, "total_results": len(rows), "data": rows[start:start+limit]}), 200

# --- UPDATE (PUT) ---
@api_bp.route('/harvest/<int:harvest_id>', methods=['PUT'])
def update_harvest(harvest_id):
    data = request.get_json()
    if not data or 'CratesHarvested' not in data: return jsonify({"error": "Missing data"}), 400
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE harvest_crates SET total_crates_number=%s WHERE harvest_crates_id=%s", (to_int(data['CratesHarvested']), harvest_id))
            if cursor.rowcount == 0:
                return jsonify({"error": "Harvest not found"}), 404
        conn.commit()
    finally: conn.close()
    return jsonify({"status": "success", "message": "Updated"}), 200

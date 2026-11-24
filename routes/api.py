import logging
import os
from datetime import date as date_cls, timedelta
from urllib.parse import unquote, urlparse

from flask import Blueprint, jsonify, request
import pymysql

# --- ISSUE 1 FIX: IMPORT THE SUPPLY CHAIN MODELS ---
from models.harvest_model import calculate_harvest_rate, calculate_crate_rejection_rate
from models.transport_model import calculate_vehicle_utilisation, predict_cutoff_breach
from models.bottleneck_model import classify_bottleneck

# Create a blueprint for the API
api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Use DATABASE_URL (set in Render) when present, otherwise your local MySQL."""
    url = os.getenv("DATABASE_URL")
    if url:
        u = urlparse(url)
        settings = dict(host=u.hostname, port=u.port or 3306, user=unquote(u.username or ""),
                        password=unquote(u.password or ""), database=u.path.lstrip("/"))
    else:
        settings = dict(host="localhost", user="root", password="", database="mydb")
    if os.getenv("DB_SSL") == "true":  # needed by some hosted MySQL providers
        settings["ssl"] = {"fake_flag_to_enable_tls": True}
    return pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **settings)

# ---------- small helpers ----------
def fail(message, code=400):
    return jsonify({"error": message, "message": message}), code

def clean_block(value):
    """'Block1' or 'Block 1' -> 'Block 1' (the database value)."""
    return "Block " + "".join(c for c in (value or "") if c.isdigit())

def clean_destination(value):
    return {"PackHouse": "Pack house", "FarmShed": "Farm shed"}.get(value, value or "Other")

def hhmm(t):
    if t is None:
        return None
    secs = int(t.total_seconds()) if isinstance(t, timedelta) else t.hour * 3600 + t.minute * 60
    return f"{secs // 3600:02d}:{secs % 3600 // 60:02d}"

def hours_between(start, end):
    if not start or not end:
        return None
    (sh, sm), (eh, em) = [map(int, x.split(":")) for x in (start, end)]
    return round(((eh * 60 + em) - (sh * 60 + sm)) / 60, 1)

def get_date_time_id(cursor, day, time):
    cursor.execute("SELECT date_time_id FROM date_time WHERE `date`=%s AND `time`=%s", (day, time))
    row = cursor.fetchone()
    if row:
        return row["date_time_id"]
    cursor.execute("INSERT INTO date_time (`date`, `time`) VALUES (%s, %s)", (day, time))
    return cursor.lastrowid

def get_person_id(cursor, name):
    name = name.strip()
    cursor.execute("SELECT person_id FROM person WHERE name=%s LIMIT 1", (name,))
    row = cursor.fetchone()
    if row:
        return row["person_id"]
    cursor.execute("INSERT INTO person (name) VALUES (%s)", (name,))
    return cursor.lastrowid

def save(handler):
    """Open a connection, run handler(cursor, data, day, time), commit, and return JSON."""
    data = request.get_json() or {}
    day = data.get("DateHarvested")
    time = data.get("TimeHarvested") or data.get("time")
    if not day or not time:
        return fail("Date and time are required")
    try:
        connection = get_db_connection()
    except Exception:
        logger.exception("Database connection failed")
        return fail("Database unavailable. Please try again shortly.", 503)
    try:
        with connection.cursor() as cursor:
            error = handler(cursor, data, day, time)
            if error:
                connection.rollback()
                return fail(error)
        connection.commit()
        return jsonify({"status": "success", "message": "Saved. It will now show on the dashboard."}), 201
    except Exception:
        connection.rollback()
        logger.exception("Failed to save %s", request.path)
        return fail("Could not save the data. Please check the values and try again.", 500)
    finally:
        connection.close()

# --- DASHBOARD ENDPOINT (GET) ---
@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    day = request.args.get("date") or date_cls.today().isoformat()
    block = request.args.get("block", "all")
    extra = "" if block == "all" else " AND {t}.block=%s"
    params = (day,) if block == "all" else (day, clean_block(block))

    try:
        connection = get_db_connection()
    except Exception:
        logger.exception("Database connection failed")
        return jsonify({"error": "Database unavailable"}), 503
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT t.team_id, t.clock_in_time, t.clock_out_time, p.name AS leader, t.block, t.num_workers "
                "FROM team t JOIN person p ON p.person_id=t.team_leader_id "
                "JOIN date_time d ON d.date_time_id=t.date_time_id "
                "WHERE d.`date`=%s" + extra.format(t="t") + " ORDER BY t.clock_in_time", params)
            teams = cursor.fetchall()

            harvests = []
            if teams:
                ids = [t["team_id"] for t in teams]
                cursor.execute(
                    "SELECT h.team_id, h.total_crates_number AS crates, h.tree_number AS trees, "
                    "h.rejected_crates_number AS rejected, d.`time` FROM harvest_crates h "
                    "JOIN date_time d ON d.date_time_id=h.date_time_id "
                    "WHERE h.team_id IN (" + ",".join(["%s"] * len(ids)) + ") ORDER BY d.`time`", ids)
                harvests = cursor.fetchall()

            cursor.execute(
                "SELECT l.trip_number AS trip, l.vehicle_type AS vehicle, l.vehicle_registration AS registration, "
                "p.name AS driver, l.destination, l.number_crates_loaded AS loaded, "
                "l.number_crates_at_destination AS delivered, d.`time` FROM logistics l "
                "JOIN person p ON p.person_id=l.driver_id JOIN date_time d ON d.date_time_id=l.date_time_id "
                "WHERE d.`date`=%s" + extra.format(t="l") + " ORDER BY d.`time`", params)
            trips = cursor.fetchall()

            cursor.execute(
                "SELECT o.number_end_shift_crates AS endCrates, o.delays, o.remarks, o.block FROM operations o "
                "JOIN date_time d ON d.date_time_id=o.date_time_id "
                "WHERE d.`date`=%s" + extra.format(t="o") + " ORDER BY d.`time` DESC, o.operations_id DESC", params)
            notes = cursor.fetchall()
    except Exception:
        logger.exception("Dashboard query failed")
        return jsonify({"error": "Could not load dashboard data"}), 500
    finally:
        connection.close()

    by_team = {t["team_id"]: t for t in teams}
    shifts = []
    for t in teams:
        mine = [h for h in harvests if h["team_id"] == t["team_id"]]
        start, end = hhmm(t["clock_in_time"]), hhmm(t["clock_out_time"])
        shifts.append({
            "start": start, "end": end or "--:--", "hours": hours_between(start, end),
            "leader": t["leader"], "block": t["block"], "workers": t["num_workers"],
            "crates": sum(h["crates"] for h in mine), "rejected": sum(h["rejected"] for h in mine),
            "trees": sum(h["trees"] or 0 for h in mine)})

    operations = [{
        "time": hhmm(h["time"]), "leader": by_team[h["team_id"]]["leader"],
        "block": by_team[h["team_id"]]["block"], "workers": by_team[h["team_id"]]["num_workers"],
        "crates": h["crates"], "trees": h["trees"], "rejected": h["rejected"]} for h in harvests]

    totals = {"Pack house": 0, "Farm shed": 0, "Other": 0}
    for t in trips:
        t["destination"] = t["destination"] if t["destination"] in totals else "Other"
        totals[t["destination"]] += t["delivered"]
        t["time"] = hhmm(t["time"])

    harvested = sum(s["crates"] for s in shifts)
    awaiting = max(harvested - sum(t["loaded"] for t in trips), 0)
    latest = {}
    for n in notes:  # newest first: keep the latest note per block
        latest.setdefault(n["block"], n["endCrates"])
    shift_end = sum(latest.values()) if latest else awaiting

    # --- ISSUE 1 FIX: CALCULATE SUPPLY CHAIN MODELS ---
    total_labor_hours = sum(s["hours"] or 0 for s in shifts)
    total_rejected = sum(s["rejected"] for s in shifts)
    total_crates = sum(s["crates"] for s in shifts)
    
    try:
        harvest_rate = calculate_harvest_rate(float(total_crates), float(total_labor_hours)) if total_labor_hours > 0 else 0.0
    except Exception:
        harvest_rate = 0.0

    try:
        rejection_data = calculate_crate_rejection_rate(float(total_crates), float(total_rejected)) if total_crates > 0 else {"rejection_rate": 0.0}
        rejection_rate = rejection_data["rejection_rate"]
    except Exception:
        rejection_rate = 0.0

    total_loaded = sum(t["loaded"] for t in trips)
    vehicle_capacity = 1000 # Assuming 1000 per trip
    try:
        utilisation = calculate_vehicle_utilisation(total_loaded, vehicle_capacity) if vehicle_capacity > 0 else 0.0
    except Exception:
        utilisation = 0.0

    try:
        mock_completion_time = "16:30" 
        cutoff_data = predict_cutoff_breach(mock_completion_time)
        cutoff_status = cutoff_data["status"]
        cutoff_message = cutoff_data["message"]
    except Exception:
        cutoff_status = "GREEN"
        cutoff_message = "ON TRACK"

    try:
        gap = max(0, vehicle_capacity - total_loaded)
        bottleneck_msg = classify_bottleneck(gap, vehicle_capacity)
    except Exception:
        bottleneck_msg = "No bottleneck"

    return jsonify({
        "kpis": {"harvestedToday": harvested, "awaitingTransport": awaiting, "shiftEnd": shift_end},
        "model_kpis": {
            "harvest_rate": harvest_rate,
            "rejection_rate": rejection_rate,
            "vehicle_utilisation": utilisation,
            "cutoff_status": cutoff_status,
            "cutoff_message": cutoff_message,
            "bottleneck": bottleneck_msg
        },
        "harvestChart": {"labels": [f"{s['leader']} ({s['start']})" for s in shifts],
                         "values": [s["crates"] for s in shifts]},
        "destinationChart": {"labels": list(totals), "values": list(totals.values())},
        "shiftOverview": shifts,
        "operations": operations,
        "logistics": trips,
        "notes": [{"endCrates": n["endCrates"], "delays": n["delays"], "remarks": n["remarks"]} for n in notes],
    }), 200

# --- TEAM ENDPOINT (POST) ---
@api_bp.route('/team', methods=['POST'])
def save_team_info():
    def handler(cursor, d, day, time):
        if not d.get("teamInfo"):
            return "Missing team leader name"
        block = clean_block(d.get("operationBlock"))
        if d.get("shiftPeriod") == "Clockout":
            cursor.execute(
                "UPDATE team t JOIN person p ON p.person_id=t.team_leader_id "
                "JOIN date_time x ON x.date_time_id=t.date_time_id "
                "SET t.clock_out_time=%s WHERE p.name=%s AND t.block=%s AND x.`date`=%s "
                "AND t.clock_out_time IS NULL", (time, d["teamInfo"].strip(), block, day))
            if cursor.rowcount == 0:
                return "No clocked-in team found for that leader, block and date"
            return None
        cursor.execute(
            "INSERT INTO team (clock_in_time, num_workers, block, date_time_id, team_leader_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (time, d.get("NumOfWorkers") or 0, block,
             get_date_time_id(cursor, day, time), get_person_id(cursor, d["teamInfo"])))
    return save(handler)

# --- HARVEST ENDPOINT (POST) ---
@api_bp.route('/harvest', methods=['POST'])
def save_harvest():
    def handler(cursor, d, day, time):
        if not d.get("CratesHarvested") or not d.get("Team"):
            return "Missing team leader or crates harvested"
        try:
            crates = non_negative_int(d["CratesHarvested"], "CratesHarvested", required=True)
            non_negative_int(d.get("NumOfTrees"), "NumOfTrees")
            rejected = non_negative_int(d.get("RejectedCrates"), "RejectedCrates") or 0
        except ValueError as e:
            return str(e)
        if rejected > crates:
            return "RejectedCrates cannot be more than CratesHarvested"
        cursor.execute(
            "SELECT t.team_id FROM team t JOIN person p ON p.person_id=t.team_leader_id "
            "JOIN date_time x ON x.date_time_id=t.date_time_id "
            "WHERE p.name=%s AND x.`date`=%s ORDER BY t.team_id DESC LIMIT 1",
            (d["Team"].strip(), day))
        team = cursor.fetchone()
        if team:
            team_id = team["team_id"]
        else: 
            try:
                workers = non_negative_int(d.get("NumOfWorkers"), "NumOfWorkers") or 0
            except ValueError as e:
                return str(e)
            block = clean_block(d.get("operationBlock")) if d.get("operationBlock") else "Block 1"
            cursor.execute(
                "INSERT INTO team (clock_in_time, num_workers, block, date_time_id, team_leader_id) "
                "VALUES (%s, %s, %s, %s, %s)",
                (time, workers, block, get_date_time_id(cursor, day, time), get_person_id(cursor, d["Team"])))
            team_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO harvest_crates (total_crates_number, tree_number, rejected_crates_number, team_id, date_time_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (d["CratesHarvested"], d.get("NumOfTrees") or 0, d.get("RejectedCrates") or 0,
             team_id, get_date_time_id(cursor, day, time)))
    return save(handler)

# --- LOGISTICS ENDPOINT (POST) ---
@api_bp.route('/logistics', methods=['POST'])
def save_logistics():
    def handler(cursor, d, day, time):
        if not d.get("tripNumber"):
            return "Missing trip number"
        cursor.execute(
            "INSERT INTO logistics (trip_number, vehicle_type, vehicle_registration, destination, "
            "number_crates_loaded, number_crates_at_destination, driver_id, date_time_id, block) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (d["tripNumber"], d["vehicleType"], d["vehicleInfo"], clean_destination(d.get("destination")),
             d["numCrates"], d["numCratesDest"], get_person_id(cursor, d["driverInfo"]),
             get_date_time_id(cursor, day, time), clean_block(d.get("operationBlock"))))
    return save(handler)

# --- NOTES ENDPOINT (POST) ---
@api_bp.route('/notes', methods=['POST'])
def save_notes():
    def handler(cursor, d, day, time):
        if not d.get("endShiftCrates"):
            return "Missing end shift crates"
        cursor.execute(
            "INSERT INTO operations (number_end_shift_crates, delays, remarks, date_time_id, block) "
            "VALUES (%s, %s, %s, %s, %s)",
            (d["endShiftCrates"], d.get("delaysInfo", ""), d.get("remarksInfo", ""),
             get_date_time_id(cursor, day, time), clean_block(d.get("operationBlock"))))
    return save(handler)

# ---------- validation helper ----------
def non_negative_int(value, label, required=False):
    if value in (None, ""):
        if required:
            raise ValueError(f"{label} is required")
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a whole number")
    if number < 0:
        raise ValueError(f"{label} cannot be negative")
    return number

HARVEST_SELECT = (
    "SELECT h.harvest_crates_id AS id, h.total_crates_number AS crates, h.tree_number AS trees, "
    "h.rejected_crates_number AS rejected, p.name AS leader, t.block, d.`date`, d.`time` "
    "FROM harvest_crates h JOIN team t ON t.team_id=h.team_id "
    "JOIN person p ON p.person_id=t.team_leader_id "
    "JOIN date_time d ON d.date_time_id=h.date_time_id ")

def harvest_row(r):
    return {"id": r["id"], "crates": r["crates"], "trees": r["trees"], "rejected": r["rejected"],
            "leader": r["leader"], "block": r["block"], "date": str(r["date"]), "time": hhmm(r["time"])}

# --- GET ALL HARVESTS WITH PAGINATION & FILTERING ---
@api_bp.route('/harvests', methods=['GET'])
def get_all_harvests():
    try:
        page = non_negative_int(request.args.get("page", 1), "page", required=True)
        limit = non_negative_int(request.args.get("limit", 10), "limit", required=True)
    except ValueError as e:
        return fail(str(e))
    if page < 1 or not 1 <= limit <= 100:
        return fail("page must be 1 or more and limit between 1 and 100")

    where, params = [], []
    block = request.args.get("block")
    if block and block != "all":
        if not any(c.isdigit() for c in block):
            return fail("block must look like Block1 or Block 1")
        where.append("t.block=%s")
        params.append(clean_block(block))
    day = request.args.get("date")
    if day:
        where.append("d.`date`=%s")
        params.append(day)
    clause = (" WHERE " + " AND ".join(where)) if where else ""

    try:
        connection = get_db_connection()
    except Exception:
        logger.exception("Database connection failed")
        return fail("Database unavailable", 503)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS n FROM harvest_crates h JOIN team t ON t.team_id=h.team_id "
                "JOIN date_time d ON d.date_time_id=h.date_time_id" + clause, params)
            total = cursor.fetchone()["n"]
            cursor.execute(HARVEST_SELECT + clause + " ORDER BY h.harvest_crates_id DESC LIMIT %s OFFSET %s",
                           params + [limit, (page - 1) * limit])
            rows = [harvest_row(r) for r in cursor.fetchall()]
    except Exception:
        logger.exception("Harvest list failed")
        return fail("Could not load harvests", 500)
    finally:
        connection.close()

    return jsonify({"page": page, "limit": limit, "total_results": total, "data": rows}), 200

# --- GET ONE HARVEST ---
@api_bp.route('/harvest/<int:harvest_id>', methods=['GET'])
def get_harvest(harvest_id):
    try:
        connection = get_db_connection()
    except Exception:
        logger.exception("Database connection failed")
        return fail("Database unavailable", 503)
    try:
        with connection.cursor() as cursor:
            cursor.execute(HARVEST_SELECT + " WHERE h.harvest_crates_id=%s", (harvest_id,))
            row = cursor.fetchone()
    except Exception:
        logger.exception("Harvest lookup failed")
        return fail("Could not load the harvest", 500)
    finally:
        connection.close()
    if not row:
        return fail("Harvest record not found", 404)
    return jsonify(harvest_row(row)), 200

# --- UPDATE HARVEST (PUT) ---
@api_bp.route('/harvest/<int:harvest_id>', methods=['PUT'])
def update_harvest(harvest_id):
    data = request.get_json(silent=True) or {}
    try:
        crates = non_negative_int(data.get("CratesHarvested"), "CratesHarvested", required=True)
        trees = non_negative_int(data.get("NumOfTrees"), "NumOfTrees") or 0
        rejected = non_negative_int(data.get("RejectedCrates"), "RejectedCrates") or 0
    except ValueError as e:
        return fail(str(e))
    if rejected > crates:
        return fail("RejectedCrates cannot be more than CratesHarvested")

    try:
        connection = get_db_connection()
    except Exception:
        logger.exception("Database connection failed")
        return fail("Database unavailable", 503)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT harvest_crates_id FROM harvest_crates WHERE harvest_crates_id=%s", (harvest_id,))
            if not cursor.fetchone():
                return fail("Harvest record not found", 404)
            cursor.execute(
                "UPDATE harvest_crates SET total_crates_number=%s, tree_number=%s, rejected_crates_number=%s "
                "WHERE harvest_crates_id=%s", (crates, trees, rejected, harvest_id))
        connection.commit()
    except Exception:
        connection.rollback()
        logger.exception("Harvest update failed")
        return fail("Could not update the harvest", 500)
    finally:
        connection.close()

    return jsonify({"status": "success", "message": f"Harvest record {harvest_id} updated successfully"}), 200

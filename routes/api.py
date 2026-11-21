from datetime import date as date_cls, timedelta
from flask import Blueprint, jsonify, request
import pymysql

# Create a blueprint for the API
api_bp = Blueprint('api', __name__)


def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',      # Empty because no password was set
        database='mydb',
        cursorclass=pymysql.cursors.DictCursor
    )


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
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            error = handler(cursor, data, day, time)
            if error:
                connection.rollback()
                return fail(error)
        connection.commit()
        return jsonify({"status": "success", "message": "Saved. It will now show on the dashboard."}), 201
    except Exception as e:
        connection.rollback()
        return fail(str(e), 500)
    finally:
        connection.close()


# --- DASHBOARD ENDPOINT (GET) ---
@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    day = request.args.get("date") or date_cls.today().isoformat()
    block = request.args.get("block", "all")
    extra = "" if block == "all" else " AND {t}.block=%s"
    params = (day,) if block == "all" else (day, clean_block(block))

    connection = get_db_connection()
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500
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

    return jsonify({
        "kpis": {"harvestedToday": harvested, "awaitingTransport": awaiting, "shiftEnd": shift_end},
        "harvestChart": {"labels": [f"{s['leader']} ({s['start']})" for s in shifts],
                         "values": [s["crates"] for s in shifts]},
        "destinationChart": {"labels": list(totals), "values": list(totals.values())},
        "shiftOverview": shifts,
        "operations": operations,
        "logistics": trips,
        "notes": [{"endCrates": n["endCrates"], "delays": n["delays"], "remarks": n["remarks"]} for n in notes],
    }), 200


# --- TEAM ENDPOINT (POST): Clock In adds a team, Clock Out closes it ---
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


# --- HARVEST ENDPOINT (POST): the team leader's name is matched to today's team ---
@api_bp.route('/harvest', methods=['POST'])
def save_harvest():
    def handler(cursor, d, day, time):
        if not d.get("CratesHarvested") or not d.get("Team"):
            return "Missing team leader or crates harvested"
        cursor.execute(
            "SELECT t.team_id FROM team t JOIN person p ON p.person_id=t.team_leader_id "
            "JOIN date_time x ON x.date_time_id=t.date_time_id "
            "WHERE p.name=%s AND x.`date`=%s ORDER BY t.team_id DESC LIMIT 1",
            (d["Team"].strip(), day))
        team = cursor.fetchone()
        if not team:
            return "No team found for that leader on this date. Clock the team in first."
        cursor.execute(
            "INSERT INTO harvest_crates (total_crates_number, tree_number, rejected_crates_number, team_id, date_time_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (d["CratesHarvested"], d.get("NumOfTrees") or 0, d.get("RejectedCrates") or 0,
             team["team_id"], get_date_time_id(cursor, day, time)))
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


# --- GET ALL HARVESTS WITH PAGINATION & FILTERING ---
@api_bp.route('/harvests', methods=['GET'])
def get_all_harvests():
    """
    Demonstrates pagination and filtering.
    Example: /api/harvests?page=1&limit=5&block=Block1
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    block = request.args.get('block', default=None, type=str)

    # Mock database list (Mfanelo will replace this with a real SQL SELECT query)
    mock_db = [
        {"id": 1, "block": "Block1", "crates": 100},
        {"id": 2, "block": "Block2", "crates": 150},
        {"id": 3, "block": "Block1", "crates": 120},
    ]

    # Filtering
    if block:
        mock_db = [h for h in mock_db if h["block"] == block]

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_data = mock_db[start:end]

    return jsonify({
        "page": page,
        "limit": limit,
        "total_results": len(mock_db),
        "data": paginated_data
    }), 200


# --- UPDATE HARVEST (PUT) ---
@api_bp.route('/harvest/<int:harvest_id>', methods=['PUT'])
def update_harvest(harvest_id):
    """
    Updates an existing harvest record.
    """
    data = request.get_json()
    
    if not data or 'CratesHarvested' not in data:
        return jsonify({"error": "Missing crates harvested data"}), 400

    # TODO: Replace with real SQL UPDATE query
    # e.g., UPDATE harvests SET crates = 150 WHERE id = harvest_id
    print(f"Updating Harvest ID {harvest_id} with data: {data}")

    return jsonify({
        "status": "success", 
        "message": f"Harvest record {harvest_id} updated successfully"
    }), 200

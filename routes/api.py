from flask import Blueprint, jsonify, request
from app import db
from models import Team, HarvestCrates, Logistics, Operations, DateTime, Person
from datetime import datetime

api_bp = Blueprint("api", __name__)

def _parse_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def _save_datetime(date_str, time_str):
    # Helper to insert into date_time table and return the ID
    if not date_str: date_str = datetime.now().strftime("%Y-%m-%d")
    if not time_str: time_str = datetime.now().strftime("%H:%M:%S")
    if len(time_str) == 5: time_str += ":00" # Convert HH:MM to HH:MM:SS
    
    dt = DateTime(date=date_str, time=time_str)
    db.session.add(dt)
    db.session.flush() # Gets the ID before commit
    return dt.date_time_id

@api_bp.route("/team", methods=["POST"])
def save_team():
    data = request.get_json() or {}
    dt_id = _save_datetime(data.get("DateHarvested"), data.get("TimeHarvested"))
    
    team = Team(
        team_leader=data.get("teamInfo", ""),
        num_workers=_parse_int(data.get("NumOfWorkers")),
        block=data.get("operationBlock", ""),
        date_time_id=dt_id
    )
    db.session.add(team)
    db.session.commit()
    return jsonify(status="success", message="Team info saved"), 201

@api_bp.route("/harvest", methods=["POST"])
def save_harvest():
    data = request.get_json() or {}
    typed_name = (data.get("Team") or "").strip()
    
    # Look up the team by the name typed
    team_record = Team.query.filter(Team.team_leader == typed_name).first()
    if not team_record:
        return jsonify(status="error", message=f"Team Leader '{typed_name}' not found."), 400

    dt_id = _save_datetime(data.get("DateHarvested"), data.get("TimeHarvested"))
    
    harvest = HarvestCrates(
        team_id=team_record.team_id,
        date_time_id=dt_id,
        total_crates_number=_parse_int(data.get("CratesHarvested")),
        tree_number=_parse_int(data.get("NumOfTrees")),
        rejected_crates_number=_parse_int(data.get("RejectedCrates")),
    )
    db.session.add(harvest)
    db.session.commit()
    return jsonify(status="success", message="Harvest saved"), 201

@api_bp.route("/logistics", methods=["POST"])
def save_logistics():
    data = request.get_json() or {}
    dt_id = _save_datetime(data.get("DateHarvested"), data.get("time"))
    
    log = Logistics(
        trip_number=_parse_int(data.get("tripNumber")),
        vehicle_type=data.get("vehicleType", ""),
        vehicle_registration=data.get("vehicleInfo", ""),
        driver_id=1, # Defaulting to person_id 1 for simplicity
        destination=data.get("destination", ""),
        number_crates_loaded=_parse_int(data.get("numCrates")),
        number_crates_at_destination=_parse_int(data.get("numCratesDest")),
        date_time_id=dt_id
    )
    db.session.add(log)
    db.session.commit()
    return jsonify(status="success", message="Logistics saved"), 201

@api_bp.route("/notes", methods=["POST"])
def save_notes():
    data = request.get_json() or {}
    dt_id = _save_datetime(data.get("DateHarvested"), data.get("TimeHarvested"))
    
    note = Operations(
        block="Block 1", # Default
        date_time_id=dt_id,
        number_end_shift_crates=_parse_int(data.get("endShiftCrates")),
        delays=data.get("delaysInfo", ""),
        remarks=data.get("remarksInfo", "")
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(status="success", message="Notes saved"), 201

@api_bp.route("/dashboard", methods=["GET"])
def dashboard_data():
    # Fetch data using your ERD tables
    teams = Team.query.all()
    harvests = HarvestCrates.query.all()
    trips = Logistics.query.all()
    notes = Operations.query.all()

    shift_overview = []
    for t in teams:
        entries = [h for h in harvests if h.team_id == t.team_id]
        shift_overview.append({
            "leader": t.team_leader, "block": t.block, "workers": t.num_workers,
            "crates": sum(h.total_crates_number for h in entries),
            "rejected": sum(h.rejected_crates_number for h in entries),
            "trees": sum(h.tree_number for h in entries),
            "start": "04:30", "end": "16:00", "hours": 11.5
        })

    operations = []
    for h in harvests:
        t = next((x for x in teams if x.team_id == h.team_id), None)
        operations.append({
            "leader": t.team_leader if t else "Unknown",
            "block": t.block if t else "Unknown",
            "workers": t.num_workers if t else 0,
            "crates": h.total_crates_number,
            "trees": h.tree_number,
            "rejected": h.rejected_crates_number,
            "time": "08:30"
        })

    logistics_rows = [{
        "trip": t.trip_number, "vehicle": t.vehicle_type,
        "registration": t.vehicle_registration, "driver": t.driver_id,
        "destination": t.destination, "loaded": t.number_crates_loaded,
        "delivered": t.number_crates_at_destination, "time": "09:00"
    } for t in trips]

    total_harvested = sum(h.total_crates_number for h in harvests)
    total_loaded = sum(t.number_crates_loaded for t in trips)

    return jsonify(
        kpis={"harvestedToday": total_harvested, "awaitingTransport": max(0, total_harvested - total_loaded), "shiftEnd": notes[0].number_end_shift_crates if notes else 0},
        harvestChart={"labels": [s["leader"] for s in shift_overview], "values": [s["crates"] for s in shift_overview]},
        destinationChart={"labels": ["Pack house", "Farm shed", "Other"], "values": [total_loaded, 0, 0]},
        shiftOverview=shift_overview, operations=operations, logistics=logistics_rows, 
        notes=[{"endCrates": n.number_end_shift_crates, "delays": n.delays, "remarks": n.remarks} for n in notes]
    ), 200

from flask import Blueprint, jsonify, request

# Create a blueprint for the API
api_bp = Blueprint('api', __name__)

# --- DASHBOARD ENDPOINT (GET) ---
@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """
    Returns data for the dashboard charts.
    """
    # Mock data to prove the connection works
    mock_harvest = [82, 96, 74, 118, 105, 132, 110]
    mock_destinations = [420, 200, 60]
    
    return jsonify({
        "harvestValues": mock_harvest,
        "destinationValues": mock_destinations
    }), 200


# --- TEAM ENDPOINT (POST) ---
@api_bp.route('/team', methods=['POST'])
def save_team_info():
    data = request.get_json()
    
    # Basic validation
    if not data or 'teamInfo' not in data:
        return jsonify({"error": "Missing team leader name"}), 400
        
    print("Received Team Data:", data)
    
    return jsonify({"status": "success", "message": "Team info saved"}), 201


# --- HARVEST ENDPOINT (POST) ---
@api_bp.route('/harvest', methods=['POST'])
def save_harvest():
    data = request.get_json()
    
    if not data or 'CratesHarvested' not in data:
        return jsonify({"error": "Missing crates harvested"}), 400
        
    print("Received Harvest Data:", data)
    
    return jsonify({"status": "success", "message": "Harvest saved"}), 201


# --- LOGISTICS ENDPOINT (POST) ---
@api_bp.route('/logistics', methods=['POST'])
def save_logistics():
    data = request.get_json()
    
    if not data or 'tripNumber' not in data:
        return jsonify({"error": "Missing trip number"}), 400
        
    print("Received Logistics Data:", data)
    
    return jsonify({"status": "success", "message": "Logistics saved"}), 201


# --- NOTES ENDPOINT (POST) ---
@api_bp.route('/notes', methods=['POST'])
def save_notes():
    data = request.get_json()
    
    print("Received Notes Data:", data)
    
    return jsonify({"status": "success", "message": "Notes saved"}), 201

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

    # Mock database list (Chantel will replace this with a real SQL SELECT query)
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

from flask import Blueprint, jsonify, request
import pymysql

# Create a blueprint for the API 
api_bp = Blueprint('api', __name__)

# Add the database connection function 
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',      
        password='',      # Empty because no password was set
        database='mydb',  
        cursorclass=pymysql.cursors.DictCursor
    )

# --- DASHBOARD ENDPOINT (GET) ---
@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT SUM(total_crates_number) as total FROM harvest_crates")
            result = cursor.fetchone()
            total_harvested = result['total'] if result['total'] else 0
            
            cursor.execute("SELECT SUM(number_crates_loaded) as total FROM logistics")
            result = cursor.fetchone()
            total_dispatched = result['total'] if result['total'] else 0
            
        mock_harvest = [0, 0, 0, 0, 0, 0, total_harvested]
        mock_destinations = [total_dispatched, 0, 0]
            
        return jsonify({
            "harvestValues": mock_harvest,
            "destinationValues": mock_destinations
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

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
        
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO harvest_crates 
                (total_crates_number, tree_number, rejected_crates_number, team_id, date_time_id) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.get('CratesHarvested'), 
                data.get('NumOfTrees', 0), 
                data.get('RejectedCrates', 0), 
                1, 
                1 
            ))
            connection.commit()
            
        return jsonify({"status": "success", "message": "Harvest saved to database"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
            
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

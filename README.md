# SmartHarvest System - Rembander Agribusiness

**Module:** BFB 321 - Supply Chain Technologies and Project
**Project:** Semester 2, 2026
**Group Number:** 17

## Project Description
SmartHarvest is a web-based supply chain management solution designed for Rembander Agribusiness (Tsianda Village). The system helps track daily harvesting operations, manage transport vehicle capacity, identify operational bottlenecks (labour vs transport), and ensure deliveries meet the packhouse cut-off time (17:00).

## Group Members 
*   **Seloko Mothupi** - 24804232
*   **Mfanelo Shilubana** - 18142002
*   **Chantel Mogale** - 24821986
*   **Livhuwani Ndou** - 23549743

---

## Installation & Setup Instructions

### Prerequisites
Before running the project, ensure the following software is installed:
*   Python 3.10 or later
*   Git
*   Visual Studio Code (recommended)

### 1. Clone the Repository
git clone https://github.com/u24821986-crypto/smart-harvest.git
cd smart-harvest

### 2. Create and Activate a Virtual Environment
**Windows (PowerShell):**
python -m venv .venv
.venv\Scripts\activate

**macOS / Linux:**
python3 -m venv .venv
source .venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Setup Environment Variables
Copy the `.env.example` file to a new file named `.env`:
```bash```
cp .env.example .env
Open `.env` and add your MySQL database credentials and a secure `SECRET_KEY`.

### 5. Run the Unit Test Suite
Execute the automated test suite:
python -m pytest

**Expected Result:**
20 passed

The test suite verifies the following modules:
*   harvest_model.py
*   transport_model.py
*   optimisation_model.py
*   bottleneck_model.py

### 5. Run the Frontend Prototype
The frontend is a static web prototype built with HTML, CSS, and JavaScript. It does not require the virtual environment or a server to view.

1. Open the `templates/` folder in the project directory.
2. Double-click on `index.html` to open the Home page in your web browser.
3. Use the navigation links/buttons within the UI to explore the Login, Dashboard, and Operations pages.

---

BFB321_Project/
│
├── README.md                  # Main project documentation
├── .gitignore                 # Git ignore file
├── .env.example               # Environment variable template
├── requirements.txt           # Python dependencies
├── config.py                  # Environment-specific configurations
├── app.py                     # Flask application entry point
├── Procfile                   # Deployment run command for Render
│
├── database/                  # Database scripts
│   ├── README.md
│   ├── mydb.sql
│   └── schema.sql
│
├── models/                    # Python logic files
│   ├── bottleneck_model.py
│   ├── harvest_model.py
│   ├── optimisation_model.py
│   └── transport_model.py
│
├── routes/                    # Flask API routes
│   ├── __init__.py
│   ├── api.py
│   └── api_v2.py
│
├── tests/                     # Unit tests for models
│   ├── test_bottleneck_model.py
│   ├── test_harvest_model.py
│   ├── test_optimisation_model.py
│   └── test_transport_model.py
│
└── templates/                 # HTML files (Frontend)
    ├── index.html
    ├── login.html
    ├── dashboard.html
    └── operations.html
## Project Status
The current implementation includes:
*   Harvest Management Model
*   Transport Management Model
*   Bottleneck Detection Model
*   Optimisation Model
*   Frontend Web Prototype
*   Unit Testing Suite

All Python models have been tested and validated using `pytest`.

## Technologies Used
*   HTML5
*   CSS3
*   Bootstrap 5
*   JavaScript
*   Chart.js
*   Python
*   Pytest
*   Git & GitHub
*   GitHub Copilot

---
 ### Test Login Credentials
To access the management dashboard and daily operations pages, the system is protected by a secure login screen. Because this is a prototype demonstration, the authentication is simulated using a hard-coded test credential.

Use the following details on the login page:
*   **Username:** `admin`
*   **Password:** `password123`

---

## Deployment & Operations

### API Endpoints
The application exposes the following REST API endpoints:

| Method | Endpoint | Description | Request Body (JSON) | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/dashboard` | Fetches data for KPIs, charts, and tables | None | 200, 500 |
| `POST` | `/api/team` | Saves Team Information (Clock In/Out) | `{"teamInfo": "John", "operationBlock": "Block 1"}` | 201, 400, 500 |
| `POST` | `/api/harvest` | Saves Harvested Crates data | `{"CratesHarvested": 100, "NumOfTrees": 5}` | 201, 400, 500 |
| `POST` | `/api/logistics` | Saves Logistics data | `{"tripNumber": 1, "vehicleType": "Truck"}` | 201, 400, 500 |
| `POST` | `/api/notes` | Saves Operational Notes | `{"endShiftCrates": 40, "remarksInfo": "Good"}` | 201, 400, 500 |
| `GET` | `/api/harvests` | Lists harvests (paginated & filtered) | None | 200, 400, 500 |
| `GET` | `/api/harvest/<id>` | Fetches a single harvest record | None | 200, 404, 500 |
| `PUT` | `/api/harvest/<id>` | Updates an existing harvest record | `{"CratesHarvested": 120}` | 200, 400, 404, 500 |

### Environment Variables & Configurations
The application uses a `.env` file for configuration. A template is provided in the repository as `.env.example`. To run the app locally, create a `.env` file and add your database credentials and secret key. Do not commit the `.env` file to GitHub.
Environment configurations are handled in `config.py`:
*   `DevelopmentConfig`: Used locally (Debug on).
*   `TestingConfig`: Used by Pytest (uses a separate test database).
*   `ProductionConfig`: Used on live servers (Debug off).

### Logging & Monitoring
Basic logging has been implemented using Python's built-in `logging` module. All application errors and startup events are logged to `app.log` with timestamps. 
*   The log file rotates at 1MB (keeping 3 backups).
*   Centralised error handlers capture 400, 404, and 500 errors and return clean JSON responses.

### Database Backup & Restore
To ensure data safety, the following backup routine is recommended for production:
**Backup (Daily):**
mysqldump -u root -p smartharvest > backups/smartharvest_$(date +%F).sql
**Restore:**
mysql -u root -p smartharvest < backups/smartharvest_2026-11-20.sql
*(Retention: Keep 14 days of local backups. If hosted on Render, utilize the platform's automated database backups).*

### Live Deployment (Render)
The application is hosted on Render. 
**Live URL:** [https://smart-harvest-qhls.onrender.com](https://smart-harvest-qh1s.onrender.com)

**Render Deployment Runbook:**
1. Push changes to the `main` branch on GitHub.
2. Render automatically detects changes and triggers a build.
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT` (Configured in the `Procfile`).
5. **Environment Variables:** Set `FLASK_ENV=production`, `SECRET_KEY`, and `DATABASE_URL` in the Render dashboard.
6. **Rollback Plan:** Use the Render dashboard to redeploy a previous successful commit.


**Note:** The free tier on Render may take 30-50 seconds to spin up the app if it has been idle.

---

## Task Allocation

| Team Member | Student Number | GitHub Username | Primary Role | Tasks Completed |
| :--- | :--- | :--- | :--- | :--- |
| **Livhuwani Ndou** | 23549743 | `u23549743` | Database & Schema | Created MySQL database, wrote ERD and schema.sql, created seed data |
| **Mfanelo Shilubana** | 18142002 | `MfaneloS` | Flask API & Endpoints | Built Flask routes, ensured GET/POST/PUT requests work, formatted JSON responses |
| **Seloko Mothupi** | 24804232 | `u24804232-stack` | Connection & Integration | Connected HTML forms to API, updated dashboard KPIs from DB, verified 3 end-to-end flows |
| **Chantel Mogale** | 24821986 | `u24821986-crypto` | Deployment & Operations | Hosted app on Render, configured .env and config.py, set up logging, updated README, wrote deployment report section |

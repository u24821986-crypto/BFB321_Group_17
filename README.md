# SmartHarvest System - Rembander Agribusiness

**Module:** BFB 321 - Supply Chain Technologies and Project
**Project:** Semester 2, 2026

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
pip install pytest

### 4. Run the Unit Test Suite
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

## Folder Structure
```text
BFB321_Project/
│
├── README.md                  # This file
├── .gitignore                 # Git ignore file
│
├── models/                    # Python logic files
│   ├── bottleneck_model.py
│   ├── harvest_model.py
│   ├── optimisation_model.py
│   └── transport_model.py
│
├── tests/                     # Unit tests for models
│   ├── test_bottleneck_model.py
│   ├── test_harvest_model.py
│   ├── test_optimisation_model.py
│   └── test_transport_model.py
│
└── templates/                 # HTML files (Frontend prototype)
    ├── index.html
    ├── login.html
    ├── dashboard.html
    └── operations.html

---

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

## Deployment & Operations

### Environment Variables
The application uses a `.env` file for configuration. A template is provided in the repository as `.env.example`. To run the app locally, create a `.env` file and add your database credentials and secret key. Do not commit the `.env` file to GitHub.

### Logging & Monitoring
Basic logging has been implemented using Python's built-in `logging` module. All application errors and startup events are logged to `app.log` with timestamps to help trace issues.

### Live Deployment
The application is hosted online and can be accessed via the following live link:
**Live URL:** [INSERT RENDER LINK HERE]

**Note:** The free tier on Render may take 30-50 seconds to spin up the app if it has been idle.

---

## Task Allocation

| Team Member | Student Number | GitHub Username | Primary Role | Tasks Completed |
| :--- | :--- | :--- | :--- | :--- |
| **Seloko Mothupi** | 24804232 | `u24804232-stack` | Integration | Connected HTML forms to API, dynamic dashboard |
| **Mfanelo Shilubana** | 18142002 | `MfaneloS` | API | Built Flask routes, JSON endpoints, error handling |
| **Chantel Mogale** | 24821986 | `u24821986-crypto` | Deployment | `.env` setup, logging, Render deployment, README update |
| **Livhuwani Ndou** | 23549743 | `u23549743` | Database | Designed ERD, wrote schema.sql, set up MySQL |

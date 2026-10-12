# Smart Complaint Management System Using Flask and DevOps CI/CD Automation

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939?logo=jenkins&logoColor=white)](https://www.jenkins.io/)
[![Ansible](https://img.shields.io/badge/Ansible-Automation-EE0000?logo=ansible&logoColor=white)](https://www.ansible.com/)
[![Pytest](https://img.shields.io/badge/Pytest-Automated_Tests-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)

---

## 1. Project Overview

The **Smart Complaint Management System** is an end-to-end civic grievance management web application coupled with a complete automated DevOps CI/CD pipeline. 

Designed specifically for college DevOps laboratory demonstrations, viva presentations, and practical evaluations, this project demonstrates:
1. **A functional, responsive web application** developed with **Python Flask**, **SQLite**, **HTML5**, **CSS3**, and **JavaScript**.
2. **A containerized lifecycle** using **Docker** and persistent state management via **Docker Volumes**.
3. **Automated unit and integration testing** with **Pytest**.
4. **Continuous Integration and Continuous Deployment (CI/CD)** via **Jenkins Pipeline**.
5. **Configuration and deployment automation** using **Ansible** and the `community.docker` collection.

---

## 2. Technology Stack

| Layer | Technologies | Purpose |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript | Modern, responsive UI with navy/white environmental civic theme, custom cards, stepper progress bars, and alerts |
| **Backend** | Python 3.11, Flask 3.1.0 | RESTful routing, input validation, session-based admin authentication, and Jinja2 rendering |
| **Database** | SQLite3 (`data/complaints.db`) | Relational schema, safe parameterized SQL queries, and automatic schema initialization |
| **Testing** | Pytest 8.x | Automated test suite verifying routes, database persistence, status updates, and session security |
| **Containerization** | Docker (`python:3.11-slim`) | Lightweight container runtime, reproducible environment, and port exposure |
| **Data Persistence** | Docker Volume (`complaint_management_data`) | Host-independent persistent volume preserving SQLite database across container restarts and updates |
| **Continuous Integration** | Jenkins (`Jenkinsfile`) | Automated 3-stage pipeline (Build &rarr; Pytest Test &rarr; Ansible Deploy) |
| **Continuous Deployment** | Ansible (`complaint-deploy.yml`) | Declarative container state management using `community.docker.docker_container` |

---

## 3. Features & Roles

The system supports two core roles:

### 1. Resident / Citizen (Complainant)
- **Public Home Page:** Overview of civic operations and real-time grievance statistics.
- **Submit Complaint (`/report`):**
  - Choose department category: *Water Supply*, *Electricity*, *Sanitation*, *Road and Infrastructure*, *Maintenance*, *Other*.
  - Input incident location/street address.
  - Enter detailed grievance description.
  - Assign priority: *Low*, *Medium*, or *High* (defaults to *Medium*).
  - Receive an instant, unique **Complaint ID** (e.g., `#1`, `#2`).
  - Automatic initial status set to **`Submitted`**.
- **Track Status (`/track`):**
  - Look up ticket by numeric Complaint ID.
  - Visual 4-step progress tracker: **Submitted &rarr; In Progress &rarr; Resolved &rarr; Closed**.
  - Review timestamps, assigned department, and priority badges.

### 2. Administrator (Municipal Authority)
- **Session Authentication (`/admin/login` & `/admin/logout`):**
  - Protected administrative routes guarded by session cookies.
  - Credentials managed via environment variables (`ADMIN_USERNAME` / `ADMIN_PASSWORD`).
- **Admin Dashboard (`/admin`):**
  - Live summary KPI cards: **Total Complaints**, **Submitted**, **In Progress**, **Resolved**, and **Closed**.
  - Interactive complaints table with sorting and filtering by Department, Status, or Priority.
  - Inline status modification dropdown and one-click update actions.
- **Status Lifecycle Control (`/update_status`):**
  - Transitions grievance state safely with parameterized queries:
    $$\text{Submitted} \longrightarrow \text{In Progress} \longrightarrow \text{Resolved} \longrightarrow \text{Closed}$$

---

## 4. Application Flow vs. DevOps Flow

### Application Workflow (Runtime Citizen / Admin Interaction)
```
User / Complainant
        ↓
  Open Website (/)
        ↓
 Submit Complaint (/report)
        ↓
 Select Category & Priority
        ↓
 Enter Location & Description
        ↓
  Submit Form (POST /submit_complaint)
        ↓
   Flask Backend
        ↓
 SQLite Database (data/complaints.db)
        ↓
 Complaint Stored & ID Generated
        ↓
 User Tracks Status (/track)
        ↓
 Admin Logs In (/admin/login)
        ↓
 Admin Dashboard (/admin)
        ↓
 Update Status (/update_status)
        ↓
 Updated Status Reflected in SQLite & Public Tracker
```

### DevOps CI/CD Automation Workflow (Engineering Lifecycle)
```
      Developer
         ↓ (git push)
       GitHub
         ↓ (Webhook / Poll)
      Jenkins
         ↓ (Checkout Code)
 Stage 1: Docker Build (complaint-management-ci)
         ↓
 Stage 2: Pytest (Automated Unit & Integration Tests)
         ↓
 Stage 3: Ansible Deploy (Execute complaint-deploy.yml)
         ↓
 Docker Engine / Container (complaint-management-ansible on Port 5002:5000)
         ↓
 Docker Volume (complaint_management_data mounted to /app/data)
         ↓
 SQLite Database (/app/data/complaints.db persisted across updates)
```

> **Separation of Concerns:** Citizen actions (submitting complaints) write directly to the database at runtime and **do NOT trigger Jenkins**. Jenkins and Ansible only run when developers modify, build, test, and release code changes.

---

## 5. Project Directory Structure

```
ComplaintManagement/
│
├── app.py                     # Core Flask application, routing, DB auto-init & auth
├── requirements.txt           # Python package dependencies (Flask, pytest)
├── Dockerfile                 # Docker container specification (python:3.11-slim)
├── Jenkinsfile                # Declarative Jenkins CI/CD 3-stage pipeline definition
├── complaint-deploy.yml       # Ansible playbook deploying container with Docker Volume
├── inventory.ini              # Ansible inventory file for deployment target
├── test_app.py                # Automated Pytest suite with isolated test DB fixture
├── .gitignore                 # Excludes databases, cache files, and virtualenvs
├── README.md                  # Comprehensive project documentation
│
├── templates/
│   ├── base.html              # Base layout with navbar, alerts, footer, and styling
│   ├── index.html             # Public home page with live KPI cards & workflows
│   ├── report.html            # Complaint registration form with validation
│   ├── track.html             # Ticket lookup with 4-step progress tracker
│   ├── login.html             # Admin authentication portal
│   └── admin.html             # Admin operations dashboard with filters & table
│
├── static/
│   ├── style.css              # Custom responsive stylesheet (Navy/White theme)
│   └── script.js              # Client-side validation, mobile menu, and UI effects
│
└── data/
    └── .gitkeep               # Preserves data directory structure in Git
```

---

## 6. How to Run Locally

### Prerequisites
- Python 3.10 or 3.11 installed
- Git installed

### Step-by-Step Instructions

1. **Navigate to the project directory:**
   ```bash
   cd ComplaintManagement
   ```

2. **(Optional) Create and activate a virtual environment:**
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows PowerShell:**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application:**
   ```bash
   python app.py
   ```

5. **Open your browser and navigate to:**
   - Public Portal: [http://127.0.0.1:5000](http://127.0.0.1:5000)
   - Submit Complaint: [http://127.0.0.1:5000/report](http://127.0.0.1:5000/report)
   - Track Complaint: [http://127.0.0.1:5000/track](http://127.0.0.1:5000/track)
   - Admin Login: [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)

> **Default Admin Credentials:**
> - **Username:** `admin`
> - **Password:** `admin123`
> *(Can be overridden by setting environment variables `ADMIN_USERNAME` and `ADMIN_PASSWORD`)*

---

## 7. How to Run Pytest

Automated tests verify all application capabilities using a clean, temporary SQLite database fixture that does not affect production records.

Run the test suite:
```bash
python -m pytest test_app.py -v
```

### What Pytest Tests:
- `test_app_starts`: Confirms the Flask factory initializes properly in test mode.
- `test_home_page`: Asserts HTTP 200 and checks page branding on `/`.
- `test_report_page`: Asserts HTTP 200 and checks department options on `/report`.
- `test_submit_complaint_success`: Asserts POST `/submit_complaint` stores data in SQLite with status `Submitted` and redirects to tracking with ID.
- `test_submit_complaint_invalid_input`: Tests missing location or description returns HTTP 400 with feedback.
- `test_track_complaint_valid`: Confirms tracking returns ticket details and status.
- `test_track_complaint_not_found`: Confirms non-existent ID returns friendly notice.
- `test_track_complaint_invalid_id`: Confirms alphanumeric or malformed IDs are rejected safely.
- `test_unauthenticated_admin_access_redirect`: Asserts unauthenticated users are redirected to `/admin/login`.
- `test_admin_login_and_dashboard`: Verifies correct login grants session and access to `/admin`.
- `test_admin_login_invalid_credentials`: Verifies invalid credentials return HTTP 401.
- `test_admin_update_status`: Verifies authenticated admin can update status from `Submitted` to `In Progress` and `Resolved` directly in SQLite.
- `test_admin_logout`: Confirms session termination blocks further admin actions.

---

## 8. Docker Containerization

### Build the Docker Image
The application image is packaged with Python 3.11-slim:
```bash
docker build -t complaint-management-ci .
```

### Run Tests Inside Docker Container
Before running the container in production, run Pytest inside a disposable container:
```bash
docker run --rm complaint-management-ci python -m pytest test_app.py
```

### Run the Docker Container with Docker Volume
Run the container named `complaint-management-ansible` listening on host port `5002`:
```bash
docker run -d \
  --name complaint-management-ansible \
  -p 5002:5000 \
  -v complaint_management_data:/app/data \
  --restart unless-stopped \
  complaint-management-ci
```

Access the containerized application at:
[http://localhost:5002](http://localhost:5002)

---

## 9. Docker Volume Data Persistence Demonstration

A core requirement for DevOps laboratory demonstrations is proving that SQLite data persists even if the container is destroyed.

### Demonstration Steps for Viva / Lab Evaluation:

1. **Start the container with volume:**
   ```bash
   docker run -d --name complaint-demo -p 5002:5000 -v complaint_management_data:/app/data complaint-management-ci
   ```

2. **Submit a complaint:**
   - Open [http://localhost:5002/report](http://localhost:5002/report)
   - Submit a test complaint (e.g., Category: *Water Supply*, Location: *Ward 5*, Description: *Water pipe leaking*).
   - Note the generated Complaint ID (e.g., `#1`).

3. **Stop and permanently remove the running container:**
   ```bash
   docker stop complaint-demo
   docker rm complaint-demo
   ```

4. **Verify the container is completely gone:**
   ```bash
   docker ps -a
   ```

5. **Start a brand new container using the same Docker Volume:**
   ```bash
   docker run -d --name complaint-demo-new -p 5002:5000 -v complaint_management_data:/app/data complaint-management-ci
   ```

6. **Verify data persistence:**
   - Open [http://localhost:5002/track?complaint_id=1](http://localhost:5002/track?complaint_id=1)
   - **Result:** The complaint record `#1` is intact and displayed immediately!
   - **Reason:** The database file is located at `/app/data/complaints.db`, which is mounted to the named volume `complaint_management_data` managed by Docker outside the container lifecycle.

---

## 10. Jenkins CI/CD Pipeline

The `Jenkinsfile` defines a declarative, automated 3-stage CI/CD pipeline:

```groovy
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'complaint-management-ci'
        ANSIBLE_CONTAINER = 'ansible-docker-lab'
        PLAYBOOK_PATH = '/complaint-deploy.yml'
        INVENTORY_PATH = '/inventory.ini'
    }

    stages {
        stage('Build') {
            steps {
                echo 'Stage 1: Building Docker Image'
                sh 'docker build -t complaint-management-ci .'
            }
        }

        stage('Test') {
            steps {
                echo 'Stage 2: Running Automated Pytest Suite in Docker'
                sh 'docker run --rm complaint-management-ci python -m pytest test_app.py'
            }
        }

        stage('Deploy with Ansible') {
            steps {
                echo 'Stage 3: Deploying Container via Ansible Playbook'
                sh '''
                    docker exec ${ANSIBLE_CONTAINER} \
                    ansible-playbook \
                    -i ${INVENTORY_PATH} \
                    ${PLAYBOOK_PATH}
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Complaint Management CI/CD Pipeline Completed Successfully!'
        }
        failure {
            echo 'FAILURE: Complaint Management CI/CD Pipeline Failed!'
        }
    }
}
```

### Pipeline Execution Stages:
1. **Stage 1 (Build):** Compiles the application into a Docker image named `complaint-management-ci`.
2. **Stage 2 (Test):** Executes Pytest inside an isolated, temporary container. If any test fails, the build halts immediately, preventing faulty code from being released.
3. **Stage 3 (Deploy with Ansible):** Executes Ansible inside the `ansible-docker-lab` container to deploy or update `complaint-management-ansible` on port `5002:5000` with the persistent volume mounted.

---

## 11. Ansible Automated Deployment

The `complaint-deploy.yml` playbook uses Ansible's `community.docker.docker_container` module to guarantee declarative configuration management.

### Playbook Highlights:
```yaml
- name: Deploy Smart Complaint Management System Container
  hosts: all
  gather_facts: false
  tasks:
    - name: Ensure persistent Docker Volume exists
      community.docker.docker_volume:
        name: complaint_management_data
        state: present

    - name: Deploy application container
      community.docker.docker_container:
        name: complaint-management-ansible
        image: complaint-management-ci
        state: "{{ container_state | default('started') }}"
        restart_policy: unless-stopped
        ports:
          - "5002:5000"
        volumes:
          - "complaint_management_data:/app/data"
        recreate: true
```

### Setting up `ansible-docker-lab` in a College Lab Environment:

1. **Install Ansible Docker collection:**
   ```bash
   ansible-galaxy collection install community.docker
   ```

2. **Run Ansible container with Docker socket access:**
   If running Ansible inside a container, share the host Docker daemon socket:
   ```bash
   docker run -d \
     --name ansible-docker-lab \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -v $(pwd)/complaint-deploy.yml:/complaint-deploy.yml \
     -v $(pwd)/inventory.ini:/inventory.ini \
     willhallonline/ansible:latest sleep infinity
   ```

3. **Execute playbook manually:**
   ```bash
   docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /complaint-deploy.yml
   ```

---

## 12. College Lab Viva / Oral Examination Guide

### Q1: What is the main objective of this project?
> **Answer:** To demonstrate both a full-featured web application (Smart Complaint Management System in Python Flask & SQLite) and an automated DevOps CI/CD workflow incorporating Git, Docker, Pytest, Jenkins, and Ansible.

### Q2: Why is the SQLite database stored in `data/complaints.db` rather than the root directory?
> **Answer:** In Docker, ephemeral containers destroy data inside their writable layer when deleted. By isolating the database inside `data/`, we mount a dedicated Docker Volume (`complaint_management_data`) to `/app/data`. This decouples data storage from the container runtime, guaranteeing data persistence.

### Q3: What is the role of Pytest in the Jenkins pipeline?
> **Answer:** Pytest runs in Stage 2 inside a disposable Docker container (`docker run --rm`). It acts as a quality gate. If any unit test or regression fails, Jenkins terminates the pipeline with a failure notification and blocks Stage 3 (deployment).

### Q4: How does Ansible provide idempotent deployments?
> **Answer:** Ansible's `community.docker.docker_container` module ensures idempotence: if the container is already running with the target image, port, and volume configurations, Ansible takes no action. If the image was rebuilt or parameters changed, Ansible safely recreates the container without unnecessary downtime.

### Q5: What is the difference between the application flow and the CI/CD flow?
> **Answer:** 
> - **Application flow:** Operates when citizens report issues or admins update statuses. These operations execute within Flask and SQLite; they never trigger Jenkins.
> - **CI/CD flow:** Operates when developers make code updates. It builds the Docker image, runs tests, and automates deployment through Ansible.

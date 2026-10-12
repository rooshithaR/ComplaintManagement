import os
import sqlite3
import pytest
from app import create_app, get_db_connection


@pytest.fixture
def app(tmp_path):
    """Create and configure a fresh Flask app instance with a temporary database for each test."""
    temp_db_path = str(tmp_path / "test_complaints.db")
    app = create_app({
        'TESTING': True,
        'DATABASE': temp_db_path,
        'SECRET_KEY': 'pytest-test-secret-key'
    })
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_app_starts(app):
    """Test that Flask application initializes successfully in testing mode."""
    assert app is not None
    assert app.config['TESTING'] is True


def test_home_page(client):
    """Test that the Home page returns HTTP 200 and renders key branding."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Smart Complaint' in response.data
    assert b'Submit a Complaint' in response.data


def test_report_page(client):
    """Test that the Report page returns HTTP 200 and renders the submission form."""
    response = client.get('/report')
    assert response.status_code == 200
    assert b'Submit a Civic Complaint' in response.data
    assert b'Water Supply' in response.data


def test_submit_complaint_success(client, app):
    """Test submitting a new complaint and verify it is stored in SQLite with 'Submitted' status."""
    payload = {
        'category': 'Water Supply',
        'location': '104 Main Street, Ward 4',
        'description': 'Main pipeline ruptured, clean water flooding the street.',
        'priority': 'High'
    }
    response = client.post('/submit_complaint', data=payload, follow_redirects=False)
    assert response.status_code == 302
    assert '/track?complaint_id=1' in response.headers['Location']

    # Directly check SQLite database
    conn = get_db_connection(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM complaints WHERE id = 1')
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row['category'] == 'Water Supply'
    assert row['location'] == '104 Main Street, Ward 4'
    assert row['description'] == 'Main pipeline ruptured, clean water flooding the street.'
    assert row['priority'] == 'High'
    assert row['status'] == 'Submitted'


def test_submit_complaint_invalid_input(client):
    """Test submitting an invalid complaint (missing description and location)."""
    payload = {
        'category': 'Electricity',
        'location': '',
        'description': '',
        'priority': 'Medium'
    }
    response = client.post('/submit_complaint', data=payload)
    assert response.status_code == 400
    assert b'Location / Address is required' in response.data
    assert b'A short description of the issue is required' in response.data


def test_track_complaint_valid(client):
    """Test tracking a valid complaint by ID."""
    # Submit first
    client.post('/submit_complaint', data={
        'category': 'Sanitation',
        'location': 'Market Road',
        'description': 'Garbage bins not cleared for three days.',
        'priority': 'Medium'
    })

    # Track by ID = 1
    response = client.get('/track?complaint_id=1')
    assert response.status_code == 200
    assert b'#1' in response.data
    assert b'Sanitation' in response.data
    assert b'Market Road' in response.data
    assert b'Garbage bins not cleared for three days.' in response.data
    assert b'Submitted' in response.data


def test_track_complaint_not_found(client):
    """Test tracking a non-existent Complaint ID."""
    response = client.get('/track?complaint_id=99999')
    assert response.status_code == 200
    assert b'No Complaint Found' in response.data or b'No complaint found' in response.data


def test_track_complaint_invalid_id(client):
    """Test tracking with a non-numeric ID."""
    response = client.get('/track?complaint_id=abc_invalid')
    assert response.status_code == 200
    assert b'Invalid Complaint ID' in response.data


def test_unauthenticated_admin_access_redirect(client):
    """Test that unauthenticated users cannot access /admin or /update_status."""
    # GET /admin redirects to login
    get_res = client.get('/admin')
    assert get_res.status_code == 302
    assert '/admin/login' in get_res.headers['Location']

    # POST /update_status redirects to login
    post_res = client.post('/update_status', data={'complaint_id': '1', 'status': 'In Progress'})
    assert post_res.status_code == 302
    assert '/admin/login' in post_res.headers['Location']


def test_admin_login_and_dashboard(client):
    """Test admin login flow with valid credentials and loading dashboard with HTTP 200."""
    login_res = client.post('/admin/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=False)

    assert login_res.status_code == 302
    assert '/admin' in login_res.headers['Location']

    # After login, /admin returns HTTP 200
    dash_res = client.get('/admin')
    assert dash_res.status_code == 200
    assert b'Administrative Operations Dashboard' in dash_res.data
    assert b'Total Complaints' in dash_res.data


def test_admin_login_invalid_credentials(client):
    """Test admin login with wrong credentials."""
    login_res = client.post('/admin/login', data={
        'username': 'admin',
        'password': 'wrongpassword'
    })
    assert login_res.status_code == 401
    assert b'Invalid admin credentials' in login_res.data


def test_admin_update_status(client, app):
    """Test updating complaint status from Submitted to In Progress and Resolved."""
    # 1. Create a complaint
    client.post('/submit_complaint', data={
        'category': 'Road and Infrastructure',
        'location': 'Cross Street 5',
        'description': 'Deep pothole damaging vehicles.',
        'priority': 'High'
    })

    # 2. Login as admin
    client.post('/admin/login', data={
        'username': 'admin',
        'password': 'admin123'
    })

    # 3. Update status to 'In Progress'
    update_res = client.post('/update_status', data={
        'complaint_id': '1',
        'status': 'In Progress'
    }, follow_redirects=False)
    assert update_res.status_code == 302
    assert '/admin' in update_res.headers['Location']

    # Verify status in SQLite
    conn = get_db_connection(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM complaints WHERE id = 1')
    row = cursor.fetchone()
    assert row['status'] == 'In Progress'

    # 4. Advance to 'Resolved'
    client.post('/update_status', data={
        'complaint_id': '1',
        'status': 'Resolved'
    })
    cursor.execute('SELECT status FROM complaints WHERE id = 1')
    row = cursor.fetchone()
    assert row['status'] == 'Resolved'
    conn.close()


def test_admin_logout(client):
    """Test that logging out clears admin privileges."""
    # Login
    client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
    assert client.get('/admin').status_code == 200

    # Logout
    logout_res = client.get('/admin/logout')
    assert logout_res.status_code == 302
    assert '/admin/login' in logout_res.headers['Location']

    # Now accessing /admin redirects to login
    assert client.get('/admin').status_code == 302

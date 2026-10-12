import os
import sqlite3
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'data', 'complaints.db')

VALID_CATEGORIES = [
    'Water Supply',
    'Electricity',
    'Sanitation',
    'Road and Infrastructure',
    'Maintenance',
    'Other'
]

VALID_PRIORITIES = ['Low', 'Medium', 'High']
VALID_STATUSES = ['Submitted', 'In Progress', 'Resolved', 'Closed']


def get_db_path(app_instance=None):
    """Retrieve database path from app config, env var, or fallback default."""
    if app_instance and app_instance.config.get('DATABASE'):
        return app_instance.config['DATABASE']
    env_path = os.environ.get('DATABASE_PATH')
    if env_path:
        return env_path
    return DEFAULT_DB_PATH


def get_db_connection(db_path=None):
    """Create a connection to the SQLite database with Row factory."""
    target_path = db_path or get_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    """Initialize database and create complaints table if not existing."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Submitted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def admin_required(f):
    """Decorator to protect admin routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin authentication required. Please log in.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def create_app(test_config=None):
    """Application factory for Flask."""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'devops-secret-key-2025')

    if test_config:
        app.config.update(test_config)

    # Initialize the database on startup
    with app.app_context():
        init_db(get_db_path(app))

    # Helper for db connection within request context
    def db_conn():
        return get_db_connection(get_db_path(app))

    @app.route('/')
    def index():
        """Home page with overview, KPI statistics, and navigation."""
        conn = db_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM complaints')
        total = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'Submitted'")
        submitted = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'In Progress'")
        in_progress = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'Resolved'")
        resolved = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'Closed'")
        closed = cursor.fetchone()['count']

        conn.close()

        stats = {
            'total': total,
            'submitted': submitted,
            'in_progress': in_progress,
            'resolved': resolved,
            'closed': closed
        }
        return render_template('index.html', stats=stats)

    @app.route('/report', methods=['GET'])
    def report():
        """Render complaint submission form."""
        return render_template(
            'report.html',
            categories=VALID_CATEGORIES,
            priorities=VALID_PRIORITIES
        )

    @app.route('/submit_complaint', methods=['POST'])
    def submit_complaint():
        """Handle complaint form submission."""
        category = request.form.get('category', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'Medium').strip()

        # Validation
        errors = []
        if not category or category not in VALID_CATEGORIES:
            errors.append('Please select a valid complaint category.')
        if not location:
            errors.append('Location / Address is required.')
        if not description:
            errors.append('A short description of the issue is required.')
        if priority not in VALID_PRIORITIES:
            priority = 'Medium'

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'report.html',
                categories=VALID_CATEGORIES,
                priorities=VALID_PRIORITIES,
                form_data=request.form
            ), 400

        conn = db_conn()
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO complaints (category, location, description, priority, status)
            VALUES (?, ?, ?, ?, 'Submitted')
            ''',
            (category, location, description, priority)
        )
        complaint_id = cursor.lastrowid
        conn.commit()
        conn.close()

        flash(
            f'Complaint submitted successfully! Your tracking ID is #{complaint_id}.',
            'success'
        )
        return redirect(url_for('track', complaint_id=complaint_id))

    @app.route('/track', methods=['GET'])
    def track():
        """Track complaint status by ID."""
        raw_id = request.args.get('complaint_id', '').strip()
        complaint = None
        searched = False

        if raw_id:
            searched = True
            try:
                complaint_id = int(raw_id)
                conn = db_conn()
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM complaints WHERE id = ?',
                    (complaint_id,)
                )
                complaint = cursor.fetchone()
                conn.close()
                if not complaint:
                    flash(f'No complaint found with ID #{complaint_id}. Please check your ticket number.', 'warning')
            except ValueError:
                flash('Invalid Complaint ID. Please enter numeric ID.', 'danger')

        return render_template(
            'track.html',
            complaint=complaint,
            searched=searched,
            query_id=raw_id,
            statuses=VALID_STATUSES
        )

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        """Admin authentication."""
        if session.get('is_admin'):
            return redirect(url_for('admin'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            expected_user = os.environ.get('ADMIN_USERNAME', 'admin')
            expected_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')

            if username == expected_user and password == expected_pass:
                session['is_admin'] = True
                session['admin_user'] = username
                flash(f'Welcome, {username}! Logged in successfully.', 'success')
                return redirect(url_for('admin'))
            else:
                flash('Invalid admin credentials. Please try again.', 'danger')
                return render_template('login.html', username=username), 401

        return render_template('login.html')

    @app.route('/admin/logout', methods=['GET'])
    def admin_logout():
        """Log out the administrator."""
        session.clear()
        flash('You have been logged out securely.', 'info')
        return redirect(url_for('admin_login'))

    @app.route('/admin', methods=['GET'])
    @admin_required
    def admin():
        """Admin dashboard with KPI cards and table."""
        conn = db_conn()
        cursor = conn.cursor()

        # Metrics
        cursor.execute('SELECT COUNT(*) as count FROM complaints')
        total = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'Submitted'")
        submitted = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'In Progress'")
        in_progress = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'Resolved'")
        resolved = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'Closed'")
        closed = cursor.fetchone()['count']

        # Filter criteria
        category_filter = request.args.get('category', '').strip()
        status_filter = request.args.get('status', '').strip()
        priority_filter = request.args.get('priority', '').strip()

        query = 'SELECT * FROM complaints WHERE 1=1'
        params = []

        if category_filter and category_filter in VALID_CATEGORIES:
            query += ' AND category = ?'
            params.append(category_filter)
        if status_filter and status_filter in VALID_STATUSES:
            query += ' AND status = ?'
            params.append(status_filter)
        if priority_filter and priority_filter in VALID_PRIORITIES:
            query += ' AND priority = ?'
            params.append(priority_filter)

        query += ' ORDER BY created_at DESC, id DESC'
        cursor.execute(query, params)
        complaints = cursor.fetchall()
        conn.close()

        stats = {
            'total': total,
            'submitted': submitted,
            'in_progress': in_progress,
            'resolved': resolved,
            'closed': closed
        }

        return render_template(
            'admin.html',
            complaints=complaints,
            stats=stats,
            categories=VALID_CATEGORIES,
            priorities=VALID_PRIORITIES,
            statuses=VALID_STATUSES,
            current_category=category_filter,
            current_status=status_filter,
            current_priority=priority_filter
        )

    @app.route('/update_status', methods=['POST'])
    @admin_required
    def update_status():
        """Update the status of a complaint."""
        raw_id = request.form.get('complaint_id', '').strip()
        new_status = request.form.get('status', '').strip()

        if not raw_id or not new_status:
            flash('Complaint ID and status are required.', 'danger')
            return redirect(url_for('admin'))

        if new_status not in VALID_STATUSES:
            flash(f'Invalid status: {new_status}', 'danger')
            return redirect(url_for('admin'))

        try:
            complaint_id = int(raw_id)
        except ValueError:
            flash('Invalid Complaint ID.', 'danger')
            return redirect(url_for('admin'))

        conn = db_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT id, status FROM complaints WHERE id = ?', (complaint_id,))
        existing = cursor.fetchone()

        if not existing:
            conn.close()
            flash(f'Complaint #{complaint_id} not found.', 'danger')
            return redirect(url_for('admin'))

        cursor.execute(
            'UPDATE complaints SET status = ? WHERE id = ?',
            (new_status, complaint_id)
        )
        conn.commit()
        conn.close()

        flash(
            f'Complaint #{complaint_id} status updated to "{new_status}".',
            'success'
        )
        return redirect(url_for('admin'))

    return app


# Default application instance for local and Docker execution
app = create_app()

if __name__ == '__main__':
    # Listen on 0.0.0.0 and port 5000 as required
    app.run(host='0.0.0.0', port=5000, debug=False)

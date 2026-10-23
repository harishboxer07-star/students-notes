import os
import time
import secrets
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, abort, g
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from models import (
    init_db, close_db, get_db,
    get_admin_by_username, get_admin_by_id, count_admins,
    get_all_subjects, get_subject_by_id, get_subject_by_name,
    create_subject, update_subject, delete_subject, count_subject_notes, count_subjects,
    get_all_notes, get_recent_notes, get_notes_by_subject, get_note_by_id,
    create_note, update_note, delete_note, count_notes
)

app = Flask(__name__)
app.config.from_object(Config)

# Register database teardown
app.teardown_appcontext(close_db)

# -------------------------------------------------------------
# Security & CSRF Protection
# -------------------------------------------------------------

def generate_csrf_token():
    """Generate or retrieve per-session CSRF token."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

@app.before_request
def csrf_protect():
    """Verify CSRF token on all state-modifying POST requests."""
    if request.method == "POST":
        token = request.form.get('csrf_token')
        expected_token = session.get('csrf_token')
        if not expected_token or not token or not secrets.compare_digest(token, expected_token):
            abort(403, description="CSRF token validation failed. Please refresh the page and try again.")

@app.context_processor
def inject_global_template_context():
    """Provide helper objects, current year, and CSRF token to all templates."""
    return {
        'csrf_token': generate_csrf_token(),
        'app_name': Config.APP_NAME,
        'app_tagline': Config.APP_TAGLINE,
        'current_year': datetime.now().year,
        'is_admin_logged_in': 'admin_id' in session,
        'admin_username': session.get('admin_username')
    }

@app.template_filter('format_date')
def format_date_filter(value, format_str="%b %d, %Y"):
    """Format timestamp strings or datetime objects gracefully."""
    if not value:
        return ""
    if isinstance(value, str):
        # Try common SQLite timestamp formats
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime(format_str)
            except ValueError:
                pass
        return value[:10]  # Fallback to date portion
    if isinstance(value, datetime):
        return value.strftime(format_str)
    return str(value)

# -------------------------------------------------------------
# Authentication Guard Decorator
# -------------------------------------------------------------

def login_required(view_func):
    """Ensure user is logged in as an administrator."""
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if 'admin_id' not in session:
            flash("Please log in to access the administrator panel.", "warning")
            return redirect(url_for('admin_login', next=request.path))
        return view_func(*args, **kwargs)
    return decorated_view

# -------------------------------------------------------------
# Public Website Routes
# -------------------------------------------------------------

@app.route('/')
def index():
    """Home page with hero, search bar, subject cards, and recent notes."""
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        # If search submitted on home page, forward to notes page with query
        return redirect(url_for('notes_list', search=search_query))

    subjects = get_all_subjects()
    recent_notes = get_recent_notes(limit=6)
    total_subjects = count_subjects()
    total_notes = count_notes()

    return render_template(
        'index.html',
        subjects=subjects,
        recent_notes=recent_notes,
        total_subjects=total_subjects,
        total_notes=total_notes
    )

@app.route('/subjects')
def subjects_list():
    """Public subjects catalog in responsive grid with search."""
    search = request.args.get('search', '').strip()
    subjects = get_all_subjects(search=search if search else None)
    return render_template('subjects.html', subjects=subjects, search=search)

@app.route('/subjects/<int:subject_id>')
def subject_detail(subject_id):
    """View all notes belonging to a specific subject."""
    subject = get_subject_by_id(subject_id)
    if not subject:
        abort(404, description="Subject not found")
    
    notes = get_notes_by_subject(subject_id)
    return render_template('subject_detail.html', subject=subject, notes=notes)

@app.route('/notes')
def notes_list():
    """Public notes page with search and subject dropdown filter."""
    search = request.args.get('search', '').strip()
    subject_id_raw = request.args.get('subject_id', '').strip()
    
    subject_id = int(subject_id_raw) if subject_id_raw.isdigit() else None
    
    notes = get_all_notes(search=search if search else None, subject_id=subject_id)
    subjects = get_all_subjects()
    
    selected_subject = None
    if subject_id:
        selected_subject = get_subject_by_id(subject_id)

    return render_template(
        'notes.html',
        notes=notes,
        subjects=subjects,
        search=search,
        selected_subject_id=subject_id,
        selected_subject=selected_subject
    )

@app.route('/notes/<int:note_id>')
def note_detail(note_id):
    """Full detail view for a specific study note."""
    note = get_note_by_id(note_id)
    if not note:
        abort(404, description="Study note not found")
    
    # Fetch other notes in the same subject for "Related Notes"
    related_notes = [n for n in get_notes_by_subject(note['subject_id']) if n['id'] != note['id']][:4]

    return render_template('note_detail.html', note=note, related_notes=related_notes)

# -------------------------------------------------------------
# Admin Authentication Routes
# -------------------------------------------------------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Administrator login page with validation, show/hide password, and sessions."""
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))

    next_url = request.args.get('next', '')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        next_destination = request.form.get('next', '').strip()

        if not username or not password:
            flash("Both username and password are required.", "danger")
            return render_template('admin_login.html', username=username, next=next_destination)

        admin = get_admin_by_username(username)
        if not admin or not check_password_hash(admin['password_hash'], password):
            flash("Invalid administrator credentials. Please try again.", "danger")
            return render_template('admin_login.html', username=username, next=next_destination)

        # Successful login
        session.clear()
        session['admin_id'] = admin['id']
        session['admin_username'] = admin['username']
        # Re-generate CSRF token for the authenticated session
        session['csrf_token'] = secrets.token_hex(32)

        flash(f"Welcome back, {admin['username']}! You have securely logged in.", "success")
        if next_destination and next_destination.startswith('/admin'):
            return redirect(next_destination)
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html', next=next_url)

@app.route('/admin/logout')
def admin_logout():
    """Terminate administrator session."""
    session.clear()
    flash("You have been safely logged out.", "info")
    return redirect(url_for('admin_login'))

# -------------------------------------------------------------
# Admin Dashboard & Overview
# -------------------------------------------------------------

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Central administrator dashboard with metrics and recent items."""
    total_subjects = count_subjects()
    total_notes = count_notes()
    recent_notes = get_recent_notes(limit=5)
    subjects = get_all_subjects()[:5]

    return render_template(
        'admin_dashboard.html',
        total_subjects=total_subjects,
        total_notes=total_notes,
        recent_notes=recent_notes,
        subjects=subjects
    )

# -------------------------------------------------------------
# Admin Subject Management (CRUD)
# -------------------------------------------------------------

@app.route('/admin/subjects')
@login_required
def manage_subjects():
    """List all subjects with note counts and action buttons."""
    search = request.args.get('search', '').strip()
    subjects = get_all_subjects(search=search if search else None)
    return render_template('manage_subjects.html', subjects=subjects, search=search)

@app.route('/admin/subjects/new', methods=['GET', 'POST'])
def subject_create():
    """Create a new subject."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash("Subject name is required.", "danger")
            return render_template('subject_form.html', name=name, description=description, is_edit=False)

        existing = get_subject_by_name(name)
        if existing:
            flash(f"A subject with the name '{name}' already exists. Please use a unique name.", "danger")
            return render_template('subject_form.html', name=name, description=description, is_edit=False)

        create_subject(name, description)
        flash(f"Subject '{name}' was successfully created!", "success")
        return redirect(url_for('manage_subjects'))

    return render_template('subject_form.html', is_edit=False)

@app.route('/admin/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])
@login_required
def subject_edit(subject_id):
    """Edit an existing subject."""
    subject = get_subject_by_id(subject_id)
    if not subject:
        abort(404, description="Subject not found")

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash("Subject name is required.", "danger")
            return render_template('subject_form.html', subject=subject, name=name, description=description, is_edit=True)

        existing = get_subject_by_name(name)
        if existing and existing['id'] != subject_id:
            flash(f"Another subject with the name '{name}' already exists. Please choose a different name.", "danger")
            return render_template('subject_form.html', subject=subject, name=name, description=description, is_edit=True)

        update_subject(subject_id, name, description)
        flash(f"Subject '{name}' was updated successfully!", "success")
        return redirect(url_for('manage_subjects'))

    return render_template('subject_form.html', subject=subject, is_edit=True)

@app.route('/admin/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
def subject_delete(subject_id):
    """Delete a subject after verifying no notes are attached."""
    subject = get_subject_by_id(subject_id)
    if not subject:
        abort(404, description="Subject not found")

    notes_count = count_subject_notes(subject_id)
    if notes_count > 0:
        flash(
            f"Cannot delete subject '{subject['name']}' because it currently contains {notes_count} note(s). "
            "Please delete or reassign its notes before deleting this subject.",
            "danger"
        )
        return redirect(url_for('manage_subjects'))

    try:
        delete_subject(subject_id)
        flash(f"Subject '{subject['name']}' has been permanently deleted.", "success")
    except Exception as e:
        flash(f"Error deleting subject: {str(e)}", "danger")

    return redirect(url_for('manage_subjects'))

# -------------------------------------------------------------
# Admin Note Management (CRUD)
# -------------------------------------------------------------

@app.route('/admin/notes')
@login_required
def manage_notes():
    """List all notes in a searchable, filterable table."""
    search = request.args.get('search', '').strip()
    subject_id_raw = request.args.get('subject_id', '').strip()
    subject_id = int(subject_id_raw) if subject_id_raw.isdigit() else None

    notes = get_all_notes(search=search if search else None, subject_id=subject_id)
    subjects = get_all_subjects()

    return render_template(
        'manage_notes.html',
        notes=notes,
        subjects=subjects,
        search=search,
        selected_subject_id=subject_id
    )

@app.route('/admin/notes/new', methods=['GET', 'POST'])
@login_required
def note_create():
    """Create a new study note."""
    subjects = get_all_subjects()

    if not subjects:
        flash("You must create at least one subject before adding notes.", "warning")
        return redirect(url_for('subject_create'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subject_id_raw = request.form.get('subject_id', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip() or description or title
        pdf_url = request.form.get('pdf_url', '').strip()

        # Validation
        if not title:
            flash("Note title is required.", "danger")
            return render_template('note_form.html', subjects=subjects, is_edit=False, form_data=request.form)

        if not subject_id_raw or not subject_id_raw.isdigit():
            flash("Please select a valid subject.", "danger")
            return render_template('note_form.html', subjects=subjects, is_edit=False, form_data=request.form)

        subject_id = int(subject_id_raw)
        if not get_subject_by_id(subject_id):
            flash("The selected subject does not exist.", "danger")
            return render_template('note_form.html', subjects=subjects, is_edit=False, form_data=request.form)

        # Handle PDF (File Upload or Any URL / URN)
        pdf_file = request.files.get('pdf_file')
        if pdf_file and pdf_file.filename:
            orig_name = secure_filename(pdf_file.filename)
            if orig_name.lower().endswith('.pdf'):
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                unique_filename = f"{int(time.time())}_{orig_name}"
                save_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
                pdf_file.save(save_path)
                pdf_url = f"/static/uploads/{unique_filename}"
            else:
                flash("Uploaded file must be a .pdf document.", "warning")
                return render_template('note_form.html', subjects=subjects, is_edit=False, form_data=request.form)

        create_note(
            title=title,
            subject_id=subject_id,
            description=description,
            content=content,
            pdf_url=pdf_url if pdf_url else None
        )
        flash(f"Note '{title}' was successfully published!", "success")
        return redirect(url_for('manage_notes'))

    # Default to subject_id passed via query param if any
    preselected_subject_id = request.args.get('subject_id', '')
    return render_template(
        'note_form.html',
        subjects=subjects,
        is_edit=False,
        form_data={'subject_id': preselected_subject_id}
    )

@app.route('/admin/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def note_edit(note_id):
    """Edit an existing study note."""
    note = get_note_by_id(note_id)
    if not note:
        abort(404, description="Note not found")

    subjects = get_all_subjects()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subject_id_raw = request.form.get('subject_id', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip() or note['content'] or description or title
        pdf_url = request.form.get('pdf_url', '').strip()

        # Validation
        if not title:
            flash("Note title is required.", "danger")
            return render_template('note_form.html', note=note, subjects=subjects, is_edit=True, form_data=request.form)

        if not subject_id_raw or not subject_id_raw.isdigit():
            flash("Please select a valid subject.", "danger")
            return render_template('note_form.html', note=note, subjects=subjects, is_edit=True, form_data=request.form)

        subject_id = int(subject_id_raw)
        if not get_subject_by_id(subject_id):
            flash("Selected subject does not exist.", "danger")
            return render_template('note_form.html', note=note, subjects=subjects, is_edit=True, form_data=request.form)

        # Handle PDF (File Upload or Any URL / URN)
        pdf_file = request.files.get('pdf_file')
        if pdf_file and pdf_file.filename:
            orig_name = secure_filename(pdf_file.filename)
            if orig_name.lower().endswith('.pdf'):
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                unique_filename = f"{int(time.time())}_{orig_name}"
                save_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
                pdf_file.save(save_path)
                pdf_url = f"/static/uploads/{unique_filename}"
            else:
                flash("Uploaded file must be a .pdf document.", "warning")
                return render_template('note_form.html', note=note, subjects=subjects, is_edit=True, form_data=request.form)

        update_note(
            note_id=note_id,
            title=title,
            subject_id=subject_id,
            description=description,
            content=content,
            pdf_url=pdf_url if pdf_url else None
        )
        flash(f"Note '{title}' updated successfully!", "success")
        return redirect(url_for('manage_notes'))

    return render_template('note_form.html', note=note, subjects=subjects, is_edit=True, form_data=dict(note))

@app.route('/admin/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def note_delete(note_id):
    """Delete a study note."""
    note = get_note_by_id(note_id)
    if not note:
        abort(404, description="Note not found")

    delete_note(note_id)
    flash(f"Note '{note['title']}' has been deleted.", "success")
    return redirect(url_for('manage_notes'))

# -------------------------------------------------------------
# Error Handlers
# -------------------------------------------------------------

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('base.html', custom_error_title="403 - Forbidden Access", custom_error_message=str(error.description)), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', custom_error_title="404 - Page Not Found", custom_error_message="The requested resource or page could not be found."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', custom_error_title="500 - Server Error", custom_error_message="An unexpected error occurred. Please try again later."), 500

# -------------------------------------------------------------
# Application Startup
# -------------------------------------------------------------

if __name__ == '__main__':
    # Automatically initialize tables if not already present
    init_db()
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)

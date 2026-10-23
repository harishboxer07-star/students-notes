import sqlite3
from datetime import datetime
from flask import g
from config import Config

def get_db():
    """Establish database connection or reuse existing connection for the current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            Config.DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        # Enforce foreign key constraints in SQLite
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(db_path=None):
    """Create all required tables with primary and foreign key constraints."""
    target_path = db_path or Config.DATABASE
    conn = sqlite3.connect(target_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Admin Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Subjects Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Notes Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject_id INTEGER NOT NULL,
            description TEXT,
            content TEXT NOT NULL,
            pdf_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE RESTRICT
        );
    """)

    conn.commit()
    conn.close()

# -------------------------------------------------------------
# Admin Helper Functions
# -------------------------------------------------------------

def get_admin_by_username(username):
    db = get_db()
    return db.execute(
        "SELECT * FROM admin WHERE username = ?", (username.strip(),)
    ).fetchone()

def get_admin_by_id(admin_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM admin WHERE id = ?", (admin_id,)
    ).fetchone()

def create_admin(username, password_hash):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
        (username.strip(), password_hash)
    )
    db.commit()
    return cursor.lastrowid

def count_admins():
    db = get_db()
    result = db.execute("SELECT COUNT(*) AS total FROM admin").fetchone()
    return result['total'] if result else 0

# -------------------------------------------------------------
# Subject Helper Functions (CRUD)
# -------------------------------------------------------------

def get_all_subjects(search=None):
    db = get_db()
    query = """
        SELECT s.id, s.name, s.description, s.created_at,
               COUNT(n.id) AS notes_count
        FROM subjects s
        LEFT JOIN notes n ON s.id = n.subject_id
    """
    params = []
    if search:
        query += " WHERE s.name LIKE ? OR s.description LIKE ?"
        term = f"%{search.strip()}%"
        params.extend([term, term])
    query += " GROUP BY s.id ORDER BY s.name ASC"
    return db.execute(query, params).fetchall()

def get_subject_by_id(subject_id):
    db = get_db()
    return db.execute(
        """
        SELECT s.id, s.name, s.description, s.created_at,
               COUNT(n.id) AS notes_count
        FROM subjects s
        LEFT JOIN notes n ON s.id = n.subject_id
        WHERE s.id = ?
        GROUP BY s.id
        """,
        (subject_id,)
    ).fetchone()

def get_subject_by_name(name):
    db = get_db()
    return db.execute(
        "SELECT * FROM subjects WHERE LOWER(name) = LOWER(?)",
        (name.strip(),)
    ).fetchone()

def create_subject(name, description):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO subjects (name, description) VALUES (?, ?)",
        (name.strip(), description.strip() if description else "")
    )
    db.commit()
    return cursor.lastrowid

def update_subject(subject_id, name, description):
    db = get_db()
    db.execute(
        "UPDATE subjects SET name = ?, description = ? WHERE id = ?",
        (name.strip(), description.strip() if description else "", subject_id)
    )
    db.commit()

def count_subject_notes(subject_id):
    db = get_db()
    res = db.execute(
        "SELECT COUNT(*) AS total FROM notes WHERE subject_id = ?",
        (subject_id,)
    ).fetchone()
    return res['total'] if res else 0

def delete_subject(subject_id):
    """Safely delete subject. Fails if foreign key violation occurs (subject has notes)."""
    db = get_db()
    db.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    db.commit()

def count_subjects():
    db = get_db()
    res = db.execute("SELECT COUNT(*) AS total FROM subjects").fetchone()
    return res['total'] if res else 0

# -------------------------------------------------------------
# Notes Helper Functions (CRUD)
# -------------------------------------------------------------

def get_all_notes(search=None, subject_id=None, limit=None):
    db = get_db()
    query = """
        SELECT n.id, n.title, n.subject_id, n.description, n.content,
               n.pdf_url, n.created_at, n.updated_at,
               s.name AS subject_name
        FROM notes n
        JOIN subjects s ON n.subject_id = s.id
        WHERE 1=1
    """
    params = []
    if subject_id:
        query += " AND n.subject_id = ?"
        params.append(subject_id)
    if search:
        query += " AND (n.title LIKE ? OR n.description LIKE ? OR s.name LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term, term])
    
    query += " ORDER BY n.created_at DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    return db.execute(query, params).fetchall()

def get_recent_notes(limit=6):
    return get_all_notes(limit=limit)

def get_notes_by_subject(subject_id):
    return get_all_notes(subject_id=subject_id)

def get_note_by_id(note_id):
    db = get_db()
    return db.execute(
        """
        SELECT n.id, n.title, n.subject_id, n.description, n.content,
               n.pdf_url, n.created_at, n.updated_at,
               s.name AS subject_name
        FROM notes n
        JOIN subjects s ON n.subject_id = s.id
        WHERE n.id = ?
        """,
        (note_id,)
    ).fetchone()

def create_note(title, subject_id, description, content, pdf_url=None, created_at=None):
    db = get_db()
    cursor = db.cursor()
    now_str = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO notes (title, subject_id, description, content, pdf_url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title.strip(),
            int(subject_id),
            description.strip() if description else "",
            content.strip(),
            pdf_url.strip() if pdf_url else None,
            now_str,
            now_str
        )
    )
    db.commit()
    return cursor.lastrowid

def update_note(note_id, title, subject_id, description, content, pdf_url=None):
    db = get_db()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        """
        UPDATE notes
        SET title = ?, subject_id = ?, description = ?, content = ?, pdf_url = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            title.strip(),
            int(subject_id),
            description.strip() if description else "",
            content.strip(),
            pdf_url.strip() if pdf_url else None,
            now_str,
            note_id
        )
    )
    db.commit()

def delete_note(note_id):
    db = get_db()
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()

def count_notes():
    db = get_db()
    res = db.execute("SELECT COUNT(*) AS total FROM notes").fetchone()
    return res['total'] if res else 0

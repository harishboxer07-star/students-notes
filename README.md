# LAK04 — Student Notes & Subject Management System

An educational web platform inspired by classic study note blogs, engineered with **Python Flask**, **SQLite**, **HTML5/CSS3/JavaScript**, and **FontAwesome**.

Designed with an original modern dark-blue and crisp white academic theme, **LAK04** focuses strictly on:
- 📚 Adding, viewing, and organizing academic subjects
- 📝 Publishing and formatting high-yield study notes
- 🔍 Subject-wise exploration and fast search filtering
- 📄 Supporting supplementary PDF handouts and downloads
- 🛡️ Secure session-based administrator authentication with password hashing and CSRF protection
- ⚙️ Full CRUD operations for subjects and notes with integrity safeguards

---

## 🚀 Quick Start Guide (Windows)

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your Windows computer. Check with:
```powershell
python --version
```

### 2. Install Required Dependencies
Open PowerShell or Command Prompt in the project folder and run:
```powershell
python -m pip install -r requirements.txt
```

### 3. Initialize Database & Create Admin Account
Execute the setup script to initialize the SQLite database (`lak04.db`), configure your administrator credentials, and seed realistic academic subjects and notes:
```powershell
python init_admin.py --username admin --password admin123 --seed
```

> **Note:** You can also run `python init_admin.py` without arguments for an interactive password prompt.

### 4. Run the Flask Web Application
Start the local development server:
```powershell
python app.py
```

### 5. Access the Web Application
Open your web browser and navigate to:
- **Public Portal:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Admin Login:** [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)

**Default Admin Credentials:**
- **Username:** `admin`
- **Password:** `admin123`

---

## 📁 Project Architecture & File Structure

```text
student notes/
│
├── app.py                  # Core Flask application, routing, CSRF middleware, session security
├── config.py               # Central configuration (database URI, secrets, cookie security)
├── models.py               # SQLite database schemas and parameterized CRUD helpers
├── requirements.txt        # Minimal production-grade dependencies (Flask, Werkzeug)
├── init_admin.py           # CLI & interactive admin creator and sample data seeder
├── test_system.py          # Automated end-to-end integration test suite
├── lak04.db                # SQLite database (auto-generated)
│
├── templates/              # Semantic Jinja2 HTML5 Templates
│   ├── base.html           # Master layout: navigation bar, toasts, modal base, footer
│   ├── index.html          # Home page: hero section, search bar, stats, subjects & recent notes
│   ├── subjects.html       # Public subjects catalog grid with live search
│   ├── subject_detail.html # Subject portal displaying all notes belonging to the subject
│   ├── notes.html          # Notes repository with keyword search and subject dropdown filter
│   ├── note_detail.html    # Full reader mode with formatted content, PDF preview & download
│   ├── admin_login.html    # Admin sign-in with show/hide password toggle & CSRF
│   ├── admin_dashboard.html# Executive admin console with metrics, recent notes, and shortcuts
│   ├── manage_subjects.html# Subjects CRUD data table with delete confirmation modal
│   ├── subject_form.html   # Subject creation & edit form with duplicate validation
│   ├── manage_notes.html   # Notes CRUD data table with subject filtering and delete modal
│   └── note_form.html      # Note creation & edit form with formatting cheatsheet & PDF URL
│
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css       # Custom modern dark-blue CSS design system with micro-animations
│   └── js/
│       └── main.js         # Mobile drawer toggle, password eye toggle, auto-dismiss alerts
│
└── README.md               # Complete documentation and setup manual
```

---

## 🗄️ Database Design (`lak04.db`)

The SQLite database enforces foreign key constraints via `PRAGMA foreign_keys = ON;`:

### `admin` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique admin identifier |
| `username` | TEXT | UNIQUE, NOT NULL | Login username |
| `password_hash`| TEXT | NOT NULL | Salted hash via `werkzeug.security` |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

### `subjects` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique subject identifier |
| `name` | TEXT | UNIQUE, NOT NULL | Subject name (e.g., Operating Systems) |
| `description` | TEXT | | Overview / syllabus summary |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Subject registration date |

### `notes` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique note identifier |
| `title` | TEXT | NOT NULL | Title of the note |
| `subject_id` | INTEGER | NOT NULL, FOREIGN KEY | References `subjects(id)` (RESTRICT delete) |
| `description` | TEXT | | Brief snippet shown on preview cards |
| `content` | TEXT | NOT NULL | Full note body with headings & bullet points |
| `pdf_url` | TEXT | | Optional external/internal PDF URL |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Publication timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Modification timestamp |

---

## 🧪 CRUD Operations Testing Walkthrough

Follow these steps to test all Subject and Note CRUD operations:

### 1. Subject Management (CRUD)
1. **Login:** Navigate to `/admin/login` and log in with `admin` / `admin123`.
2. **Read:** Click **Manage Subjects** in the sidebar. You will see a data table of all subjects with their note count and creation date.
3. **Create:** Click **Add New Subject** (top-right). Enter a unique subject name (e.g. `Cloud Computing`) and a short description. Click **Create Subject**. The new subject appears immediately in the table.
4. **Duplicate Protection:** Try adding another subject with the name `Cloud Computing`. The system will reject it with a warning alert.
5. **Update:** Click the **Edit (pencil)** icon on any subject. Change the description or title, and click **Save Changes**.
6. **Integrity-Safe Delete:**
   - Attempt to delete a subject that currently contains notes: The delete confirmation modal will automatically disable the delete button and show an **Integrity Protection** warning informing you to delete or reassign its notes first.
   - For an empty subject, click the **Delete (trash)** icon and confirm in the modal dialog. The subject is permanently removed.

### 2. Note Management (CRUD)
1. **Create:** Click **Manage Notes** > **Add New Note**.
   - Select a Subject from the dropdown.
   - Enter a Title (e.g., `Introduction to Kubernetes`).
   - Enter a Summary description.
   - Enter Note Content (supports `### Heading`, `- Bullet item`, `1. Numbered item`).
   - **Attach PDF (Dual Option):**
     - **Option 1 (Direct Upload):** Choose any `.pdf` document from your local computer. It is saved directly to the server (`static/uploads/`).
     - **Option 2 (Any URL or URN):** Enter any external link (`https://...`), internal path, or academic URN identifier (e.g. `urn:isbn:978-0131103627` or `urn:nbn:...`).
   - Click **Publish Note**.
2. **Read:** In the Manage Notes table, search notes by keyword or filter by subject using the dropdown.
3. **Student View Verification:** Click the **Eye icon** or visit `/notes` on the public website to verify that students can read the full formatted content and click the **View / Read PDF** or **Download PDF** buttons.
4. **Update:** Click the **Edit (pencil)** icon in the admin table, modify the note title or content, and save.
5. **Delete:** Click the **Delete (trash)** icon on the note, confirm deletion in the modal dialog, and verify it is removed from both admin and public views.

---

## 🔒 Security Measures

- **Password Hashing:** Uses `werkzeug.security.generate_password_hash` with secure salting algorithms (scrypt/pbkdf2). Plaintext passwords are never saved.
- **CSRF Defense:** Every state-modifying POST request validates a cryptographic per-session CSRF token.
- **Session Hardening:** Cookies are flagged with `HttpOnly = True` and `SameSite = 'Lax'` to block client-side JavaScript theft.
- **SQL Injection Prevention:** 100% of database interactions use parameterized SQL placeholders (`?`).
- **Route Authorization:** Every `/admin/*` route is protected by a `@login_required` decorator.

---

## 🛠️ Automated Testing

An end-to-end integration test suite is included in `test_system.py`. Run it anytime with:
```powershell
python test_system.py
```
This tests authentication, bad credential rejection, CSRF tokens, duplicate prevention, and foreign-key integrity constraints automatically.

---

## ❓ Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `Port 5000 is in use` | Another process is using port 5000 | Kill the process or start Flask on another port by editing `app.py`: `app.run(port=5001)` |
| `CSRF token validation failed` | Browser session expired or cached form | Refresh the page and re-submit the form |
| `Cannot delete subject` | Subject contains associated notes | Delete or reassign all notes in that subject first |
| `sqlite3.OperationalError: database is locked` | SQLite file opened in another tool exclusively | Close external SQLite viewers and restart the app |
| Forgotten Admin Password | Need password reset | Run `python init_admin.py --username admin --password NewPassword123` |

---

*Developed for LAK04 — Distraction-Free Student Notes Hub.*

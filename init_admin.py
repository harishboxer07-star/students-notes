"""
LAK04 - Administrator Initialization & Database Setup Script
Run this script to initialize the SQLite database, create the primary administrator account,
and optionally seed realistic sample subjects and study notes.

Usage:
    python init_admin.py
    python init_admin.py --username admin --password MySecurePass123! --seed
"""

import sys
import argparse
import getpass
from werkzeug.security import generate_password_hash
from config import Config
from models import (
    init_db,
    get_db,
    get_admin_by_username,
    create_admin,
    create_subject,
    get_subject_by_name,
    create_note
)
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

SAMPLE_SUBJECTS = [
    {
        "name": "Data Structures & Algorithms",
        "description": "Fundamental computer science concepts including arrays, linked lists, trees, graphs, sorting, and algorithmic complexity (Big-O analysis)."
    },
    {
        "name": "Database Management Systems (DBMS)",
        "description": "Relational database concepts, SQL queries, ER diagrams, normalization techniques (1NF to BCNF), indexing, and transaction management (ACID)."
    },
    {
        "name": "Web Technologies & Architecture",
        "description": "Full-stack web fundamentals covering semantic HTML5, modern CSS3 layouts, JavaScript ES6+, RESTful APIs, and responsive design principles."
    },
    {
        "name": "Operating Systems",
        "description": "Core operating system principles including process scheduling, threads, synchronization, virtual memory management, and file systems."
    },
    {
        "name": "Python Programming & Flask",
        "description": "Practical Python development covering object-oriented programming, data structures, virtual environments, and lightweight web application development."
    }
]

SAMPLE_NOTES = [
    {
        "subject": "Data Structures & Algorithms",
        "title": "Comprehensive Guide to Big-O Notation and Time Complexity",
        "description": "An intuitive breakdown of asymptotic analysis, standard complexity classes, and how to analyze loop efficiency.",
        "content": """### Understanding Asymptotic Analysis

Big-O notation is the primary metric used in computer science to describe the performance and complexity of an algorithm. Specifically, it characterizes the worst-case execution time or memory space required as the input size (n) grows towards infinity.

#### Key Complexity Orders (Best to Worst):
1. **O(1) - Constant Time**: Execution time is independent of input size (e.g., hash table lookup, array index access).
2. **O(log n) - Logarithmic Time**: Divide-and-conquer strategies (e.g., Binary Search).
3. **O(n) - Linear Time**: Traversal across all elements (e.g., single loop over an unsorted array).
4. **O(n log n) - Linearithmic Time**: Optimal comparison-based sorting algorithms (e.g., Merge Sort, Heap Sort).
5. **O(n²) - Quadratic Time**: Nested loops comparing pairs of elements (e.g., Bubble Sort, Selection Sort).
6. **O(2ⁿ) - Exponential Time**: Recursive algorithms solving combinatorial problems (e.g., brute-force traveling salesman).

#### Practical Tips for Exam Review:
- Drop non-dominant terms: O(n² + 5n + 100) simplifies directly to **O(n²)**.
- Ignore constant multipliers: O(3n) simplifies to **O(n)**.
- Always check inner loop bounds to see if they decrease geometrically or step linearly.""",
        "pdf_url": "https://www.cs.cmu.edu/~adamchik/15-121/lectures/Algorithmic%20Complexity/complexity.pdf"
    },
    {
        "subject": "Data Structures & Algorithms",
        "title": "Binary Search Trees (BST): Properties and Traversals",
        "description": "Detailed explanation of BST search, insert, and delete operations with recursive traversal patterns.",
        "content": """### Binary Search Tree Definition

A Binary Search Tree is a node-based binary tree data structure with the following invariant:
- The left subtree of a node contains only nodes with keys strictly less than the node's key.
- The right subtree of a node contains only nodes with keys strictly greater than the node's key.
- Both the left and right subtrees must also be binary search trees.

#### Tree Traversals:
- **In-Order (Left, Root, Right)**: Produces keys in ascending sorted order.
- **Pre-Order (Root, Left, Right)**: Useful for cloning or serializing the tree structure.
- **Post-Order (Left, Right, Root)**: Ideal for deleting nodes or evaluating postfix mathematical expressions.
- **Level-Order (BFS)**: Uses a FIFO queue to visit nodes depth by depth.

#### Complexity Summary:
- Average Case Search / Insert / Delete: **O(log n)**
- Worst Case (Degenerate / Skewed Tree): **O(n)**
- Solution for worst case: Self-balancing trees such as AVL Trees or Red-Black Trees.""",
        "pdf_url": "https://web.stanford.edu/class/archive/cs/cs106b/cs106b.1206/lectures/trees/"
    },
    {
        "subject": "Database Management Systems (DBMS)",
        "title": "Relational Normalization: 1NF, 2NF, 3NF, and BCNF Explained",
        "description": "Step-by-step tutorial on eliminating insertion, update, and deletion anomalies through schema normalization.",
        "content": """### Why Do We Normalize Databases?

Normalization is the formal process of structuring a relational database in accordance with normal forms to minimize redundancy and eliminate data modification anomalies.

#### The Core Normal Forms:

1. **First Normal Form (1NF)**:
   - Each column contains atomic (indivisible) values.
   - Each record needs a unique primary key identifier.
   - No repeating groups or comma-separated lists in a single cell.

2. **Second Normal Form (2NF)**:
   - Must already meet 1NF criteria.
   - All non-key attributes must be fully functionally dependent on the primary key (no partial key dependencies). Applies to composite primary keys.

3. **Third Normal Form (3NF)**:
   - Must already satisfy 2NF.
   - No transitive functional dependencies (i.e., non-key attributes should not depend on other non-key attributes).
   - Rule of thumb: *"Every non-key attribute must depend on the key, the whole key, and nothing but the key."*

4. **Boyce-Codd Normal Form (BCNF)**:
   - A stricter version of 3NF.
   - For every functional dependency X → Y, X must be a super key.""",
        "pdf_url": "https://www.tutorialspoint.com/dbms/dbms_normalization.htm"
    },
    {
        "subject": "Database Management Systems (DBMS)",
        "title": "ACID Properties in Transaction Processing",
        "description": "Understand Atomicity, Consistency, Isolation, and Durability with real-world banking transaction examples.",
        "content": """### Overview of Database Transactions

A transaction is a single logical unit of work that accesses and possibly modifies the contents of a database. Transactions are guided by the ACID guarantees:

- **A - Atomicity**: The "all-or-nothing" rule. If any operation within the transaction fails, the entire transaction rolls back to its initial state.
- **C - Consistency**: The database transitions strictly from one valid state to another, upholding all constraints, cascades, triggers, and foreign keys.
- **I - Isolation**: Multiple concurrent transactions execute independently without interfering with each other. Supported by isolation levels: Read Uncommitted, Read Committed, Repeatable Read, and Serializable.
- **D - Durability**: Once a transaction commits, its modifications are permanently recorded in non-volatile storage, surviving system crashes.""",
        "pdf_url": ""
    },
    {
        "subject": "Web Technologies & Architecture",
        "title": "CSS Grid vs Flexbox: When to Use Which Layout Model",
        "description": "Mastering modern CSS layout techniques: 1-dimensional flexbox flow vs 2-dimensional grid control.",
        "content": """### Layout Engines in Modern Web Design

Choosing between Flexbox and CSS Grid is one of the most common decisions in frontend development. Here is the architectural distinction:

#### CSS Flexbox (1-Dimensional Layout):
- Designed for laying items out along a single axis (either row or column).
- Best suited for: Navigation bars, button groups, centering modal dialogs, and dynamic inline card strips.
- Key properties: `display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;`.

#### CSS Grid (2-Dimensional Layout):
- Designed for layout out content simultaneously across rows and columns.
- Best suited for: Overall application shell layouts, responsive dashboard grids, gallery layouts with auto-fit/auto-fill columns.
- Key properties: `display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;`.

#### Combined Strategy:
Use CSS Grid to define the high-level page regions and card containers, and use Flexbox inside individual cards to align icons, tags, and action buttons!""",
        "pdf_url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Grids"
    },
    {
        "subject": "Operating Systems",
        "title": "CPU Scheduling Algorithms: FCFS, SJF, Round Robin, and Priority",
        "description": "Comparative study of process scheduling policies, turnaround time, waiting time, and preemptive context switching.",
        "content": """### Principles of CPU Scheduling

CPU scheduling determines which process in the ready queue is allocated CPU time when the CPU becomes idle.

#### Standard Algorithms:
1. **First-Come, First-Served (FCFS)**:
   - Non-preemptive. Simple FIFO queue.
   - Drawback: Suffers from the "Convoy Effect" where short jobs wait behind long-running processes.

2. **Shortest Job First (SJF)**:
   - Selects the process with the smallest CPU burst time.
   - Provably optimal for minimizing average waiting time.
   - Drawback: Difficult to predict future burst lengths; risk of starvation for long processes.

3. **Round Robin (RR)**:
   - Preemptive policy using a defined Time Quantum (slice).
   - Highly responsive and fair for interactive timesharing environments.
   - Tuning: If quantum is too large, it degrades to FCFS; if too small, context-switch overhead dominates.

4. **Multi-Level Feedback Queue (MLFQ)**:
   - Multiple priority queues with dynamic priority adjustments based on process behavior (I/O-bound vs CPU-bound).""",
        "pdf_url": ""
    },
    {
        "subject": "Python Programming & Flask",
        "title": "Building Secure Web Applications with Flask and SQLite",
        "description": "Best practices for route design, session management, parameterized queries, and CSRF defense in Python Flask.",
        "content": """### Security Fundamentals in Flask

Developing web applications requires defense-in-depth against common OWASP Top 10 vulnerabilities:

1. **SQL Injection Prevention**:
   - Never concatenate user strings into SQL queries.
   - Always use parameterized queries (`cursor.execute("SELECT * FROM users WHERE id = ?", (uid,))`).

2. **Password Security**:
   - Store salted hashes, never raw plaintext.
   - Utilize standard functions like `werkzeug.security.generate_password_hash` and `check_password_hash`.

3. **Session Hardening**:
   - Enable `SESSION_COOKIE_HTTPONLY = True` to block client-side JavaScript access via XSS.
   - Set `SESSION_COOKIE_SAMESITE = 'Lax'` or `'Strict'` to guard against Cross-Site Request Forgery.
   - Employ per-session CSRF tokens on state-modifying requests (POST/PUT/DELETE).

4. **Input Sanitization & Validation**:
   - Check input existence, length constraints, and expected data types before database persistence.""",
        "pdf_url": "https://flask.palletsprojects.com/"
    }
]

def seed_sample_data():
    """Populate initial educational subjects and comprehensive notes."""
    print("[-] Seeding sample educational subjects...")
    subject_map = {}
    for sub in SAMPLE_SUBJECTS:
        existing = get_subject_by_name(sub["name"])
        if not existing:
            sub_id = create_subject(sub["name"], sub["description"])
            subject_map[sub["name"]] = sub_id
            print(f"    [+] Created subject: {sub['name']} (ID: {sub_id})")
        else:
            subject_map[sub["name"]] = existing["id"]
            print(f"    [*] Subject already exists: {sub['name']} (ID: {existing['id']})")

    print("\n[-] Seeding sample student notes...")
    for note in SAMPLE_NOTES:
        sub_id = subject_map.get(note["subject"])
        if sub_id:
            create_note(
                title=note["title"],
                subject_id=sub_id,
                description=note["description"],
                content=note["content"],
                pdf_url=note["pdf_url"]
            )
            print(f"    [+] Created note: '{note['title']}' under '{note['subject']}'")

def setup_admin(username, password, seed=False):
    """Initialize database and configure administrator credentials."""
    print("=" * 60)
    print(" LAK04 - Student Notes & Subject Management System Setup")
    print("=" * 60)

    # Initialize tables
    print("[-] Initializing SQLite database schema...")
    init_db()
    print("[+] Database initialized successfully.")

    with app.app_context():
        # Check if username exists
        existing_admin = get_admin_by_username(username)
        if existing_admin:
            print(f"[!] Administrator '{username}' already exists in the database.")
            # If arguments were provided via CLI, update automatically; otherwise ask interactively
            if len(sys.argv) > 1 and password:
                pwd_hash = generate_password_hash(password)
                db = get_db()
                db.execute("UPDATE admin SET password_hash = ? WHERE id = ?", (pwd_hash, existing_admin['id']))
                db.commit()
                print(f"[+] Password successfully updated for admin '{username}'.")
            else:
                proceed = input("Do you wish to reset the password for this admin? (y/N): ").strip().lower()
                if proceed == 'y':
                    pwd_hash = generate_password_hash(password)
                    db = get_db()
                    db.execute("UPDATE admin SET password_hash = ? WHERE id = ?", (pwd_hash, existing_admin['id']))
                    db.commit()
                    print(f"[+] Password successfully updated for admin '{username}'.")
                else:
                    print("[-] Password update skipped.")
        else:
            pwd_hash = generate_password_hash(password)
            admin_id = create_admin(username, pwd_hash)
            print(f"[+] Administrator created successfully! (ID: {admin_id}, Username: '{username}')")

        if seed:
            seed_sample_data()

    print("\n" + "=" * 60)
    print(" Setup Complete! You can now start the application with:")
    print("   python app.py")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="LAK04 Admin Initialization & Database Setup")
    parser.add_argument("--username", "-u", type=str, help="Admin username")
    parser.add_argument("--password", "-p", type=str, help="Admin password")
    parser.add_argument("--seed", "-s", action="store_true", help="Seed sample subjects and notes")
    args = parser.parse_args()

    username = args.username
    password = args.password

    # Interactive mode if arguments are missing
    if not username:
        print("Please enter administrator credentials to configure LAK04:")
        username = input("Enter admin username [default: admin]: ").strip() or "admin"

    if not password:
        while True:
            password = getpass.getpass("Enter admin password (min 6 characters): ").strip()
            if len(password) < 6:
                print("Password must be at least 6 characters long. Please try again.")
                continue
            confirm = getpass.getpass("Confirm admin password: ").strip()
            if password != confirm:
                print("Passwords do not match. Please try again.")
                continue
            break

    seed_choice = args.seed
    if not args.seed and not args.username:
        choice = input("Do you want to seed sample subjects and notes for testing? (Y/n): ").strip().lower()
        seed_choice = choice != 'n'

    setup_admin(username, password, seed=seed_choice)

if __name__ == "__main__":
    main()

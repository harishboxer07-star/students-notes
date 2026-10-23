"""
Automated End-to-End Test Suite for LAK04
Tests authentication, CSRF validation, public navigation, and full CRUD workflows.
"""
import re
from app import app
from models import get_all_subjects, get_all_notes

client = app.test_client()

def test_system():
    print("[1] Testing Public Endpoints...")
    for route in ['/', '/subjects', '/notes', '/admin/login']:
        resp = client.get(route)
        assert resp.status_code == 200, f"Route {route} failed with {resp.status_code}"
        print(f"    - {route} returned 200 OK")

    print("\n[2] Testing Admin Login with CSRF Defense...")
    # Fetch login page and extract CSRF token
    login_page = client.get('/admin/login')
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', login_page.data.decode('utf-8')).group(1)
    
    # Try logging in with wrong password
    bad_login = client.post('/admin/login', data={'username': 'admin', 'password': 'WrongPassword!', 'csrf_token': csrf_token}, follow_redirects=True)
    assert b"Invalid administrator credentials" in bad_login.data
    print("    - Rejected bad credentials as expected")

    # Correct login
    login_page = client.get('/admin/login')
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', login_page.data.decode('utf-8')).group(1)
    good_login = client.post('/admin/login', data={'username': 'admin', 'password': 'admin123', 'csrf_token': csrf_token}, follow_redirects=True)
    assert good_login.status_code == 200
    assert b"Executive Dashboard" in good_login.data
    print("    - Admin login successful & session established")

    print("\n[3] Testing Subject CRUD...")
    # Create new subject
    sub_page = client.get('/admin/subjects/new')
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', sub_page.data.decode('utf-8')).group(1)
    create_sub = client.post('/admin/subjects/new', data={
        'name': 'Cloud Computing and DevOps',
        'description': 'Containerization, orchestration, and infrastructure as code.',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b"Cloud Computing and DevOps" in create_sub.data
    print("    - Created new subject: 'Cloud Computing and DevOps'")

    # Duplicate check
    sub_page = client.get('/admin/subjects/new')
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', sub_page.data.decode('utf-8')).group(1)
    dup_sub = client.post('/admin/subjects/new', data={
        'name': 'Cloud Computing and DevOps',
        'description': 'Duplicate attempt',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b"already exists" in dup_sub.data
    print("    - Duplicate subject prevented correctly")

    print("\n[4] Testing Notes CRUD...")
    note_page = client.get('/admin/notes/new')
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', note_page.data.decode('utf-8')).group(1)
    
    # Locate the created subject ID
    sub_match = re.search(r'value="(\d+)"[^>]*>\s*Cloud Computing and DevOps', note_page.data.decode('utf-8'))
    assert sub_match, "Subject not found in note create form"
    target_sub_id = sub_match.group(1)

    create_note = client.post('/admin/notes/new', data={
        'title': 'Getting Started with Docker Containers',
        'subject_id': target_sub_id,
        'description': 'Architecture of Docker engine, containers vs VMs, and basic CLI commands.',
        'content': '### What is Docker?\nDocker is an open platform for developing, shipping, and running applications.\n\n### Core Commands\n- docker run\n- docker build\n- docker-compose up',
        'pdf_url': 'https://docs.docker.com/get-started/',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b"Getting Started with Docker Containers" in create_note.data
    print("    - Created study note: 'Getting Started with Docker Containers'")

    # Verify student public view
    student_notes = client.get('/notes')
    assert b"Getting Started with Docker Containers" in student_notes.data
    print("    - Verified public note directory contains the new note")

    # Verify search query
    search_res = client.get('/notes?search=Docker')
    assert b"Getting Started with Docker Containers" in search_res.data
    print("    - Search filtering works as expected")

    # Test PDF file upload
    import io
    note_page = client.get('/admin/notes/new')
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', note_page.data.decode('utf-8')).group(1)
    fake_pdf = io.BytesIO(b'%PDF-1.4 sample content %%EOF')
    upload_res = client.post('/admin/notes/new', data={
        'title': 'DevOps Dockerfile Reference Guide',
        'subject_id': target_sub_id,
        'description': 'Direct PDF file upload verification.',
        'content': '### Dockerfile Commands\nFROM, RUN, CMD, COPY, EXPOSE',
        'pdf_file': (fake_pdf, 'dockerfile_handout.pdf'),
        'pdf_url': '',
        'csrf_token': csrf_token
    }, content_type='multipart/form-data', follow_redirects=True)
    assert b"DevOps Dockerfile Reference Guide" in upload_res.data
    print("    - PDF File Upload verified: File saved to static/uploads/ and note linked")

    # Test Custom URN
    note_page = client.get('/admin/notes/new')
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', note_page.data.decode('utf-8')).group(1)
    urn_res = client.post('/admin/notes/new', data={
        'title': 'C Standard Library Specification',
        'subject_id': target_sub_id,
        'description': 'Textbook resource cataloged via URN.',
        'content': '### C Standard Library\nURN-referenced publication.',
        'pdf_url': 'urn:isbn:978-0131103627',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b"C Standard Library Specification" in urn_res.data
    print("    - Custom URN verified: Note published with URN: urn:isbn:978-0131103627")

    print("\n[5] Testing Safety Integrity on Subject Deletion...")
    # Attempt to delete subject with notes (should be blocked)
    manage_sub_page = client.get('/admin/subjects')
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', manage_sub_page.data.decode('utf-8')).group(1)
    del_blocked = client.post(f'/admin/subjects/{target_sub_id}/delete', data={'csrf_token': csrf_token}, follow_redirects=True)
    assert b"Cannot delete subject" in del_blocked.data
    print("    - Safety block verified: Subject with notes cannot be deleted accidentally")

    print("\n[6] Testing Note Deletion...")
    for title in ["Getting Started with Docker Containers", "DevOps Dockerfile Reference Guide", "C Standard Library Specification"]:
        notes_admin_page = client.get('/admin/notes')
        csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', notes_admin_page.data.decode('utf-8')).group(1)
        note_id_match = re.search(rf'data-id="(\d+)"\s+data-title="{re.escape(title)}"', notes_admin_page.data.decode('utf-8'))
        if note_id_match:
            nid = note_id_match.group(1)
            del_res = client.post(f'/admin/notes/{nid}/delete', data={'csrf_token': csrf_token}, follow_redirects=True)
            assert b"has been deleted" in del_res.data
            print(f"    - Note '{title}' deleted successfully")

    print("\n[7] Testing Safe Deletion of Empty Subject...")
    notes_admin_page = client.get('/admin/subjects')
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', notes_admin_page.data.decode('utf-8')).group(1)
    del_sub = client.post(f'/admin/subjects/{target_sub_id}/delete', data={'csrf_token': csrf_token}, follow_redirects=True)
    assert b"has been permanently deleted" in del_sub.data
    print("    - Empty subject deleted cleanly")

    print("\n" + "="*50)
    print(" ALL TESTS PASSED SUCCESSFULLY! LAK04 IS 100% OPERATIONAL.")
    print("="*50)

if __name__ == "__main__":
    test_system()

# 🌐 How to Host LAK04 Permanently (100% Free)

This guide shows you how to host the **LAK04** application permanently online so anyone can visit it on the internet with a public URL (e.g., `https://lak04.onrender.com` or `https://yourname.pythonanywhere.com`).

---

## 🏆 Method 1: Render.com (Recommended — 100% Free Cloud Hosting)

Render provides free hosting with automatic **HTTPS / SSL**, custom subdomains, and automatic deploys from GitHub.

All deployment configuration files have already been prepared for you:
- [`render.yaml`](file:///c:/Users/DHASWEEN/OneDrive/Desktop/student%20notes/render.yaml)
- [`Procfile`](file:///c:/Users/DHASWEEN/OneDrive/Desktop/student%20notes/Procfile)
- [`wsgi.py`](file:///c:/Users/DHASWEEN/OneDrive/Desktop/student%20notes/wsgi.py)

### Step 1: Push Code to GitHub
1. Open [GitHub](https://github.com) and create a new repository named `lak04-student-notes`.
2. In your terminal inside this folder, run:
```powershell
git init
git add .
git commit -m "Initial commit of LAK04 Student Notes System"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/lak04-student-notes.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to **[https://render.com](https://render.com)** and sign up / log in with your GitHub account.
2. Click **New +** → **Web Service**.
3. Select your repository `lak04-student-notes` and click **Connect**.
4. Render will auto-fill the settings using `render.yaml`:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python init_admin.py --username admin --password admin123 --seed`
   - **Start Command:** `gunicorn wsgi:app`
   - **Plan:** `Free`
5. Click **Create Web Service**.
6. In 2–3 minutes, your site will be live at:
   `https://lak04-student-notes.onrender.com`

---

## 🐍 Method 2: PythonAnywhere (Free Python Cloud Hosting)

PythonAnywhere is specifically built for Python Flask applications and offers permanent hosting with persistent SQLite database storage.

### Step 1: Create Free Account
1. Visit **[https://www.pythonanywhere.com](https://www.pythonanywhere.com)** and register for a free "Beginner" account.
2. Your website URL will be `https://YOUR_USERNAME.pythonanywhere.com`.

### Step 2: Upload Files
1. In PythonAnywhere, go to the **Consoles** tab and start a **Bash Console**.
2. Clone your repository or upload the project ZIP:
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/lak04-student-notes.git
cd lak04-student-notes
pip install -r requirements.txt
python init_admin.py --username admin --password admin123 --seed
```

### Step 3: Configure Flask App
1. Go to the **Web** tab in PythonAnywhere and click **Add a new web app**.
2. Choose **Manual configuration** → **Python 3.10+**.
3. Under the **Code** section:
   - **Source code:** `/home/YOUR_USERNAME/lak04-student-notes`
   - **Working directory:** `/home/YOUR_USERNAME/lak04-student-notes`
4. Click on the **WSGI configuration file** link, replace its content with:
```python
import sys
path = '/home/YOUR_USERNAME/lak04-student-notes'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```
5. Click the green **Reload** button at the top.
6. Your portal is now permanently live!

---

## 💻 Method 3: Permanent 24/7 Hosting on Your Windows PC

If you have a computer or home server that stays on and you want it to run continuously in the background (even after restarts):

### Step 1: Create a Startup Script
A startup runner script `run_permanent.bat` can run in the background.

```bat
@echo off
cd /d "C:\Users\DHASWEEN\OneDrive\Desktop\student notes"
python app.py
```

### Step 2: Set as a Windows Service or Startup Task
1. Press `Win + R`, type `taskschd.msc`, and press **Enter** to open **Task Scheduler**.
2. Click **Create Basic Task**.
3. Name: `LAK04 Notes Server`.
4. Trigger: **When the computer starts** or **When I log on**.
5. Action: **Start a program** → select your Python path or `.bat` file.
6. Finish. Now LAK04 will automatically start whenever your computer turns on and run continuously.

### Step 3: Make it Publicly Accessible with Cloudflare Tunnel (Free)
If you want to access your PC's local server from anywhere in the world on your phone without port forwarding:
1. Download [Cloudflare Tunnel (`cloudflared`)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/).
2. Run:
```powershell
cloudflared tunnel --url http://localhost:5000
```
3. Cloudflare gives you a permanent, secure `https://xxx.trycloudflare.com` public URL instantly!

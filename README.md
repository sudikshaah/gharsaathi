# Sahayak

Sahayak is a hyper-local domestic helper trust and verification platform. It connects household employers directly with verified local helpers (cooks, maids, drivers, babysitters, caregivers) using an intelligent proximity and skill-compatibility match engine.

## Features

- **Emerald Green Theme:** Modern, premium design featuring a dynamic light/dark mode switch.
- **Hyper-Local Matching:** Search and compatibility ratings based on geolocation and pincode proximity.
- **Verification Engine:** Dual Aadhaar and Police Clearance Certificate (PCC) upload process with OCR-assisted validation.
- **Account Moderation:** Admin panel for managing users, approving documents, and resolving disputes.
- **Direct Apply & Bookmark:** Real-time job applications and bookmarks for helpers.
- **Secure Sessions:** Complete user authentication (Employer, Helper, Admin roles) with global CSRF protection.

---

## Tech Stack

- **Backend:** Flask (Python 3.13+)
- **Database:** SQLAlchemy ORM (SQLite for development, MySQL/PostgreSQL support via PyMySQL)
- **Forms & Validation:** Flask-WTF / WTForms
- **Security:** Flask-Login, Cryptography, CSRFProtect
- **Frontend:** Bootstrap 5, Bootstrap Icons, Vanilla CSS, Vanilla JavaScript

---

## Installation & Setup

### Prerequisites
- Python 3.13 or newer installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/sahayak.git
cd sahayak
```

### 2. Set Up Virtual Environment
On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\activate
```
On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize and Seed the Database
Sahayak comes with a database seed script that drops any existing tables and initializes lookups, users, mock helper profiles, verification tickets, and job postings:
```bash
python seed_db.py
```

### 5. Run the Application
Start the development server:
```bash
python run.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## Test Logins
Use the following seed credentials to log in and test different system modules:

- **System Admin:** Phone `12345678` | Password `admin123`
- **Employer:** Phone `87654321` | Password `employer123`
- **Helper 1 (Sita - Cook):** Phone `11112222` | Password `helper123`
- **Helper 2 (Ramesh - Driver):** Phone `33334444` | Password `helper123`

---

## Running Tests
Run automated test suites with:
```bash
python -m pytest
```

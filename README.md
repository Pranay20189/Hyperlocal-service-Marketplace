# ServeHub – Service Marketplace

A full-stack service marketplace web app built with **Flask + MySQL + HTML/CSS**.

## Features

- **Dual-role login**: Customer (User) & Worker (Service Provider)
- **Browse & search** professionals by category or keyword
- **Book appointments** with date, time, duration, address
- **Worker dashboard**: Accept/reject/update booking status
- **Rating & reviews** system
- **Profile management** for workers (skills, rate, availability)
- Responsive dark-themed UI

## Tech Stack

| Layer     | Tech                   |
|-----------|------------------------|
| Backend   | Python 3.x + Flask     |
| Database  | MySQL                  |
| Frontend  | HTML5 / CSS3 / Vanilla JS |
| Auth      | SHA-256 hashed passwords + Flask sessions |

## Project Structure

```
service_marketplace/
├── app.py                  # Main Flask application
├── schema.sql              # MySQL database schema + seed data
├── requirements.txt
├── .gitignore
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── services.html
    ├── worker_profile.html
    ├── book_service.html
    ├── user_dashboard.html
    ├── user_bookings.html
    ├── worker_dashboard.html
    ├── worker_bookings.html
    └── worker_profile_edit.html
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/service-marketplace.git
cd service-marketplace
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up MySQL database
```bash
mysql -u root -p < schema.sql
```

### 5. Configure database credentials in `app.py`
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'   # ← change this
app.config['MYSQL_DB'] = 'service_marketplace'
```

### 6. Run the application
```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Demo Accounts

After running `schema.sql`, you can log in with:

| Role   | Email               | Password    |
|--------|---------------------|-------------|
| User   | rahul@example.com   | password123 |
| User   | priya@example.com   | password123 |
| Worker | arun@example.com    | password123 |
| Worker | suresh@example.com  | password123 |
| Worker | deepa@example.com   | password123 |

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: ServeHub service marketplace"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/service-marketplace.git
git push -u origin main
```

## Database Schema

```
users       → id, name, email, phone, password, created_at
workers     → id, name, email, phone, password, category, skills, hourly_rate, bio, is_available
bookings    → id, user_id(FK), worker_id(FK), service_date, service_time, duration, address, notes, total_amount, status, rating, review
```

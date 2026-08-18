from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'servicemarket_secret_key_2024'

# MySQL Configuration - Update these with your credentials
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Pranay@123'
app.config['MYSQL_DB'] = 'service_marketplace'

mysql = MySQL(app)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─── HOME ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT w.*, 
               AVG(b.rating) as avg_rating, 
               COUNT(b.id) as total_bookings
        FROM workers w
        LEFT JOIN bookings b ON w.id = b.worker_id AND b.rating IS NOT NULL
        GROUP BY w.id
        ORDER BY avg_rating DESC LIMIT 6
    """)
    featured_workers = cursor.fetchall()

    cursor.execute("SELECT DISTINCT category FROM workers ORDER BY category")
    categories = cursor.fetchall()
    cursor.close()
    return render_template('index.html', featured_workers=featured_workers, categories=categories)

# ─── AUTH ────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        email = request.form['email'].strip()
        password = hash_password(request.form['password'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if role == 'user':
            cursor.execute('SELECT * FROM users WHERE email=%s AND password=%s', (email, password))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['name'] = account['name']
                session['role'] = 'user'
                return redirect(url_for('user_dashboard'))
        elif role == 'worker':
            cursor.execute('SELECT * FROM workers WHERE email=%s AND password=%s', (email, password))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['name'] = account['name']
                session['role'] = 'worker'
                return redirect(url_for('worker_dashboard'))

        flash('Invalid credentials. Please try again.', 'error')
        cursor.close()
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        password = hash_password(request.form['password'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if role == 'user':
            cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
            if cursor.fetchone():
                flash('Email already registered!', 'error')
            else:
                cursor.execute('INSERT INTO users (name, email, phone, password) VALUES (%s,%s,%s,%s)',
                               (name, email, phone, password))
                mysql.connection.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))

        elif role == 'worker':
            category = request.form['category'].strip()
            skills = request.form['skills'].strip()
            hourly_rate = request.form['hourly_rate']
            bio = request.form.get('bio', '').strip()
            cursor.execute('SELECT * FROM workers WHERE email=%s', (email,))
            if cursor.fetchone():
                flash('Email already registered!', 'error')
            else:
                cursor.execute('''INSERT INTO workers (name, email, phone, password, category, skills, hourly_rate, bio)
                                  VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
                               (name, email, phone, password, category, skills, hourly_rate, bio))
                mysql.connection.commit()
                flash('Worker registration successful! Please login.', 'success')
                return redirect(url_for('login'))
        cursor.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ─── USER DASHBOARD ──────────────────────────────────────────────────────────
@app.route('/user/dashboard')
def user_dashboard():
    if not session.get('loggedin') or session.get('role') != 'user':
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT b.*, w.name as worker_name, w.category, w.profile_image
        FROM bookings b
        JOIN workers w ON b.worker_id = w.id
        WHERE b.user_id = %s ORDER BY b.created_at DESC LIMIT 5
    """, (session['id'],))
    recent_bookings = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) as total FROM bookings WHERE user_id=%s", (session['id'],))
    stats = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) as pending FROM bookings WHERE user_id=%s AND status='pending'", (session['id'],))
    pending = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) as completed FROM bookings WHERE user_id=%s AND status='completed'", (session['id'],))
    completed = cursor.fetchone()
    cursor.close()
    return render_template('user_dashboard.html',
                           recent_bookings=recent_bookings,
                           total=stats['total'],
                           pending=pending['pending'],
                           completed=completed['completed'])

@app.route('/user/bookings')
def user_bookings():
    if not session.get('loggedin') or session.get('role') != 'user':
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT b.*, w.name as worker_name, w.category, w.phone as worker_phone
        FROM bookings b JOIN workers w ON b.worker_id = w.id
        WHERE b.user_id = %s ORDER BY b.created_at DESC
    """, (session['id'],))
    bookings = cursor.fetchall()
    cursor.close()
    return render_template('user_bookings.html', bookings=bookings)

@app.route('/user/rate/<int:booking_id>', methods=['POST'])
def rate_booking(booking_id):
    if not session.get('loggedin') or session.get('role') != 'user':
        return redirect(url_for('login'))
    rating = request.form['rating']
    review = request.form.get('review', '')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE bookings SET rating=%s, review=%s WHERE id=%s AND user_id=%s",
                   (rating, review, booking_id, session['id']))
    mysql.connection.commit()
    cursor.close()
    flash('Rating submitted successfully!', 'success')
    return redirect(url_for('user_bookings'))

# ─── SERVICES BROWSE ─────────────────────────────────────────────────────────
@app.route('/services')
def services():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        SELECT w.*, AVG(b.rating) as avg_rating, COUNT(b.id) as total_reviews
        FROM workers w LEFT JOIN bookings b ON w.id = b.worker_id AND b.rating IS NOT NULL
        WHERE w.is_available = 1
    """
    params = []
    if category:
        query += " AND w.category = %s"
        params.append(category)
    if search:
        query += " AND (w.name LIKE %s OR w.skills LIKE %s OR w.category LIKE %s)"
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    query += " GROUP BY w.id ORDER BY avg_rating DESC"
    cursor.execute(query, params)
    workers = cursor.fetchall()
    cursor.execute("SELECT DISTINCT category FROM workers ORDER BY category")
    categories = cursor.fetchall()
    cursor.close()
    return render_template('services.html', workers=workers, categories=categories,
                           selected_category=category, search=search)

@app.route('/worker/<int:worker_id>')
def worker_profile(worker_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT w.*, AVG(b.rating) as avg_rating, COUNT(b.id) as total_reviews
        FROM workers w LEFT JOIN bookings b ON w.id = b.worker_id AND b.rating IS NOT NULL
        WHERE w.id = %s GROUP BY w.id
    """, (worker_id,))
    worker = cursor.fetchone()
    if not worker:
        return redirect(url_for('services'))
    cursor.execute("""
        SELECT b.rating, b.review, b.created_at, u.name as user_name
        FROM bookings b JOIN users u ON b.user_id = u.id
        WHERE b.worker_id = %s AND b.rating IS NOT NULL ORDER BY b.created_at DESC LIMIT 10
    """, (worker_id,))
    reviews = cursor.fetchall()
    cursor.close()
    return render_template('worker_profile.html', worker=worker, reviews=reviews)

@app.route('/book/<int:worker_id>', methods=['GET', 'POST'])
def book_service(worker_id):
    if not session.get('loggedin') or session.get('role') != 'user':
        flash('Please login to book a service.', 'info')
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM workers WHERE id=%s", (worker_id,))
    worker = cursor.fetchone()
    if not worker:
        return redirect(url_for('services'))

    if request.method == 'POST':
        service_date = request.form['service_date']
        service_time = request.form['service_time']
        duration = request.form['duration']
        address = request.form['address']
        notes = request.form.get('notes', '')
        total_amount = float(worker['hourly_rate']) * float(duration)
        cursor.execute("""
            INSERT INTO bookings (user_id, worker_id, service_date, service_time, duration, address, notes, total_amount)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (session['id'], worker_id, service_date, service_time, duration, address, notes, total_amount))
        mysql.connection.commit()
        cursor.close()
        flash('Booking confirmed successfully!', 'success')
        return redirect(url_for('user_bookings'))
    cursor.close()
    return render_template('book_service.html', worker=worker)

# ─── WORKER DASHBOARD ────────────────────────────────────────────────────────
@app.route('/worker/dashboard')
def worker_dashboard():
    if not session.get('loggedin') or session.get('role') != 'worker':
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT b.*, u.name as user_name, u.phone as user_phone
        FROM bookings b JOIN users u ON b.user_id = u.id
        WHERE b.worker_id = %s ORDER BY b.created_at DESC LIMIT 5
    """, (session['id'],))
    recent_bookings = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) as total FROM bookings WHERE worker_id=%s", (session['id'],))
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as pending FROM bookings WHERE worker_id=%s AND status='pending'", (session['id'],))
    pending = cursor.fetchone()['pending']
    cursor.execute("SELECT COUNT(*) as completed FROM bookings WHERE worker_id=%s AND status='completed'", (session['id'],))
    completed = cursor.fetchone()['completed']
    cursor.execute("SELECT SUM(total_amount) as revenue FROM bookings WHERE worker_id=%s AND status='completed'", (session['id'],))
    revenue = cursor.fetchone()['revenue'] or 0
    cursor.execute("SELECT AVG(rating) as avg_rating FROM bookings WHERE worker_id=%s AND rating IS NOT NULL", (session['id'],))
    avg_rating = cursor.fetchone()['avg_rating'] or 0
    cursor.close()
    return render_template('worker_dashboard.html',
                           recent_bookings=recent_bookings,
                           total=total, pending=pending,
                           completed=completed, revenue=revenue,
                           avg_rating=round(avg_rating, 1))

@app.route('/worker/bookings')
def worker_bookings():
    if not session.get('loggedin') or session.get('role') != 'worker':
        return redirect(url_for('login'))
    status_filter = request.args.get('status', '')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        SELECT b.*, u.name as user_name, u.phone as user_phone, u.email as user_email
        FROM bookings b JOIN users u ON b.user_id = u.id
        WHERE b.worker_id = %s
    """
    params = [session['id']]
    if status_filter:
        query += " AND b.status = %s"
        params.append(status_filter)
    query += " ORDER BY b.created_at DESC"
    cursor.execute(query, params)
    bookings = cursor.fetchall()
    cursor.close()
    return render_template('worker_bookings.html', bookings=bookings, status_filter=status_filter)

@app.route('/worker/update_booking/<int:booking_id>', methods=['POST'])
def update_booking_status(booking_id):
    if not session.get('loggedin') or session.get('role') != 'worker':
        return redirect(url_for('login'))
    status = request.form['status']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE bookings SET status=%s WHERE id=%s AND worker_id=%s",
                   (status, booking_id, session['id']))
    mysql.connection.commit()
    cursor.close()
    flash(f'Booking status updated to {status}!', 'success')
    return redirect(url_for('worker_bookings'))

@app.route('/worker/profile', methods=['GET', 'POST'])
def worker_edit_profile():
    if not session.get('loggedin') or session.get('role') != 'worker':
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        category = request.form['category']
        skills = request.form['skills']
        hourly_rate = request.form['hourly_rate']
        bio = request.form['bio']
        is_available = 1 if request.form.get('is_available') else 0
        cursor.execute("""
            UPDATE workers SET name=%s, phone=%s, category=%s, skills=%s,
            hourly_rate=%s, bio=%s, is_available=%s WHERE id=%s
        """, (name, phone, category, skills, hourly_rate, bio, is_available, session['id']))
        mysql.connection.commit()
        session['name'] = name
        flash('Profile updated successfully!', 'success')

    cursor.execute("SELECT * FROM workers WHERE id=%s", (session['id'],))
    worker = cursor.fetchone()
    cursor.close()
    return render_template('worker_profile_edit.html', worker=worker)

if __name__ == '__main__':
    app.run(debug=True)

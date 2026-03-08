-- ============================================================
--  SERVICE MARKETPLACE DATABASE SCHEMA
--  Run this file in MySQL: mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS service_marketplace;
USE service_marketplace;

-- Users Table (Customers)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    password VARCHAR(255) NOT NULL,
    profile_image VARCHAR(255) DEFAULT 'default_user.png',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workers Table (Service Providers)
CREATE TABLE IF NOT EXISTS workers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    password VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    skills TEXT,
    hourly_rate DECIMAL(10,2) DEFAULT 0.00,
    bio TEXT,
    profile_image VARCHAR(255) DEFAULT 'default_worker.png',
    is_available TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bookings Table (Links Users to Workers)
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    worker_id INT NOT NULL,
    service_date DATE NOT NULL,
    service_time TIME NOT NULL,
    duration DECIMAL(4,1) DEFAULT 1.0,
    address TEXT NOT NULL,
    notes TEXT,
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    status ENUM('pending','confirmed','in_progress','completed','cancelled') DEFAULT 'pending',
    rating TINYINT(1) CHECK (rating BETWEEN 1 AND 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
);

-- ─── SEED DATA ─────────────────────────────────────────────────────────────
-- Passwords below are SHA256 of "password123"

INSERT INTO users (name, email, phone, password) VALUES
('Rahul Sharma', 'rahul@example.com', '9876543210',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
('Priya Reddy', 'priya@example.com', '9876543211',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f');

INSERT INTO workers (name, email, phone, password, category, skills, hourly_rate, bio) VALUES
('Arun Kumar', 'arun@example.com', '9812345670',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 'Plumbing', 'Pipe repair, Leak fixing, Bathroom fitting, Water heater installation', 450.00,
 'Certified plumber with 8 years of experience. Available 7 days a week.'),

('Suresh Babu', 'suresh@example.com', '9812345671',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 'Electrical', 'Wiring, Circuit breakers, Fan installation, MCB panel, AC repair', 500.00,
 'Licensed electrician with expertise in residential and commercial wiring.'),

('Deepa Nair', 'deepa@example.com', '9812345672',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 'Cleaning', 'Deep cleaning, Carpet cleaning, Kitchen cleaning, Post-construction cleanup', 300.00,
 'Professional cleaning specialist. Eco-friendly products used.'),

('Vijay Prasad', 'vijay@example.com', '9812345673',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 'Carpentry', 'Furniture assembly, Door repair, Custom woodwork, Cabinet installation', 400.00,
 'Expert carpenter with 10 years making homes beautiful.'),

('Lakshmi Devi', 'lakshmi@example.com', '9812345674',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 'Painting', 'Interior painting, Exterior painting, Texture painting, Waterproofing', 350.00,
 'Skilled painter delivering flawless finishes every time.');

-- Sample Bookings
INSERT INTO bookings (user_id, worker_id, service_date, service_time, duration, address, notes, total_amount, status, rating, review)
VALUES
(1, 1, '2024-01-15', '10:00:00', 2.0, '123 MG Road, Hyderabad', 'Kitchen sink leaking badly',
 900.00, 'completed', 5, 'Excellent work! Fixed everything quickly.'),
(1, 2, '2024-01-20', '14:00:00', 1.5, '123 MG Road, Hyderabad', 'Fan installation in bedroom',
 750.00, 'completed', 4, 'Good work, professional attitude.'),
(2, 3, '2024-01-25', '09:00:00', 3.0, '45 Jubilee Hills, Hyderabad', 'Full house deep cleaning',
 900.00, 'pending', NULL, NULL);

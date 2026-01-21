import sqlite3
import hashlib
import os
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table with extended fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Officers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS officers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            badge_number TEXT UNIQUE,
            department TEXT,
            assigned_area TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Violations table - FIXED: Added driver_name column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violation_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            officer_id INTEGER,
            driver_name TEXT,  -- ADDED THIS COLUMN
            license_number TEXT,
            plate_number TEXT,
            vehicle_type TEXT,
            has_helmet TEXT,
            speed INTEGER,
            has_license TEXT,
            violations TEXT,
            total_fine INTEGER,
            status TEXT DEFAULT 'pending',
            payment_status TEXT DEFAULT 'unpaid',
            payment_date TIMESTAMP,
            description TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (officer_id) REFERENCES officers(id)
        )
    ''')
    
    # Appeals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appeals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            violation_id INTEGER,
            user_id INTEGER,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            officer_response TEXT,
            reviewed_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            FOREIGN KEY (violation_id) REFERENCES violation_records(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        )
    ''')
    
    # Traffic laws table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_laws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            law_code TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            fine_amount INTEGER,
            category TEXT,
            severity TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Audit logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id INTEGER,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            message TEXT,
            notification_type TEXT,
            is_read INTEGER DEFAULT 0,
            related_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Seed default data if empty
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "admin"')
    if cursor.fetchone()['count'] == 0:
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, email, password, role, first_name, last_name) VALUES (?, ?, ?, ?, ?, ?)',
                      ('admin', 'admin@traffic.local', admin_password, 'admin', 'System', 'Administrator'))
    
    cursor.execute('SELECT COUNT(*) as count FROM traffic_laws')
    if cursor.fetchone()['count'] == 0:
        default_laws = [
            ('TL001', 'Riding motorcycle without helmet', 15000 , 'safety', 'Minor'),
            ('TL002', 'Driving without valid license', 50000, 'license', 'Severe'),
            ('TL003', 'Speeding 1-10 km/h over limit', 20000, 'speed', 'Minor'),
            ('TL004', 'Speeding 11-20 km/h over limit', 40000, 'speed', 'Moderate'),
            ('TL005', 'Speeding more than 20 km/h over limit', 80000, 'speed', 'Severe'),
            ('TL006', 'Motorcycle exceeding 60 km/h', 30000, 'safety', 'Moderate'),
            ('TL007', 'Running red light', 100000, 'traffic_signal', 'Severe'),
            ('TL008', 'Using phone while driving', 25000, 'distraction', 'Minor'),
            ('TL009', 'Driving under influence', 500000, 'dui', 'Severe'),
            ('TL010', 'No vehicle registration', 100000, 'documentation', 'Severe')
        ]
        cursor.executemany('INSERT INTO traffic_laws (law_code, description, fine_amount, category, severity) VALUES (?, ?, ?, ?, ?)', 
                          default_laws)
    
    conn.commit()
    conn.close()

def drop_and_recreate_db():
    """Drop database and recreate it with new schema (for development)"""
    if os.path.exists(Config.DATABASE):
        os.remove(Config.DATABASE)
    init_db()
    print("Database recreated successfully!")
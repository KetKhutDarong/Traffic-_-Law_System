from utils.db import get_db
from datetime import datetime
import hashlib

class User:
    def __init__(self, id=None, username=None, email=None, password=None, role='user', created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.created_at = created_at or datetime.now()
    
    @staticmethod
    def create(username, email, password, role='user', first_name=None, last_name=None):
        """Create a new user in the database"""
        conn = get_db()
        cursor = conn.cursor()
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password, role, first_name, last_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, hashed_pwd, role, first_name, last_name, datetime.now()))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    @staticmethod
    def get_all(role=None):
        """Get all users, optionally filtered by role"""
        conn = get_db()
        cursor = conn.cursor()
        if role:
            cursor.execute('SELECT * FROM users WHERE role = ? ORDER BY created_at DESC', (role,))
        else:
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        results = cursor.fetchall()
        conn.close()
        return results
    
    @staticmethod
    def delete(user_id):
        """Delete a user"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def update(user_id, **kwargs):
        """Update user fields"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['username', 'email', 'role']:
                    fields.append(f'{key} = ?')
                    values.append(value)
            
            if not fields:
                return False
            
            values.append(user_id)
            query = f'UPDATE users SET {", ".join(fields)} WHERE id = ?'
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

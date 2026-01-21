from utils.db import get_db
from datetime import datetime

class Violation:
    @staticmethod
    def create(user_id, vehicle_type, violations, total_fine, status='pending', payment_status='unpaid'):
        """Create a new violation record"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO violation_records (user_id, vehicle_type, violations, total_fine, status, payment_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, vehicle_type, violations, total_fine, status, payment_status, datetime.now()))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_by_user(user_id):
        """Get all violations for a user"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM violation_records WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    @staticmethod
    def get_all():
        """Get all violations"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM violation_records ORDER BY created_at DESC')
        results = cursor.fetchall()
        conn.close()
        return results
    
    @staticmethod
    def get_by_id(violation_id):
        """Get violation by ID"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM violation_records WHERE id = ?', (violation_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    @staticmethod
    def update_status(violation_id, status=None, payment_status=None):
        """Update violation status"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            if status:
                cursor.execute('UPDATE violation_records SET status = ? WHERE id = ?', (status, violation_id))
            if payment_status:
                cursor.execute('UPDATE violation_records SET payment_status = ? WHERE id = ?', (payment_status, violation_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_stats():
        """Get violation statistics"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM violation_records')
        total = cursor.fetchone()['total'] or 0
        
        cursor.execute('SELECT SUM(total_fine) as collected FROM violation_records WHERE payment_status = "paid"')
        collected = cursor.fetchone()['collected'] or 0
        
        cursor.execute('''
            SELECT vehicle_type, COUNT(*) as count FROM violation_records
            GROUP BY vehicle_type
        ''')
        by_vehicle = cursor.fetchall()
        
        conn.close()
        return {
            'total': total,
            'collected': collected,
            'by_vehicle_type': [{'vehicle_type': row['vehicle_type'], 'count': row['count']} for row in by_vehicle] if by_vehicle else []
        }

from flask import Blueprint, jsonify, request, session
from utils.db import get_db
from utils.decorators import login_required, permission_required

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    conn = get_db()
    cursor = conn.cursor()
    
    # Based on user role, return different data
    if session.get('role') == 'admin':
        cursor.execute('SELECT COUNT(*) as total FROM violation_records')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT SUM(total_fine) as total FROM violation_records')
        total_fines = cursor.fetchone()['total'] or 0
    elif session.get('role') == 'officer':
        cursor.execute('SELECT COUNT(*) as total FROM officers WHERE user_id = ?', (session['user_id'],))
        officer = cursor.fetchone()
        if officer:
            cursor.execute('SELECT COUNT(*) as total FROM violation_records WHERE officer_id = ?', (officer['id'],))
            total = cursor.fetchone()['total']
        else:
            total = 0
        total_fines = 0
    else:
        cursor.execute('SELECT COUNT(*) as total FROM violation_records WHERE user_id = ?', (session['user_id'],))
        total = cursor.fetchone()['total']
        total_fines = 0
    
    conn.close()
    
    return jsonify({
        'total': total,
        'total_fines': total_fines
    })

@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM notifications
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (session['user_id'],))
    
    notifications = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'notifications': [dict(n) for n in notifications]
    })

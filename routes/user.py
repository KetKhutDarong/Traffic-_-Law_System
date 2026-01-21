from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for
from utils.decorators import login_required, role_required
from utils.db import get_db
from utils.expert_system import check_violations
import json

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user violations
    cursor.execute('''
        SELECT * FROM violation_records 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    violations = cursor.fetchall()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as total FROM violation_records WHERE user_id = ?',
                  (session['user_id'],))
    total_violations = cursor.fetchone()['total']
    
    cursor.execute('SELECT SUM(total_fine) as total FROM violation_records WHERE user_id = ? AND payment_status = "unpaid"',
                  (session['user_id'],))
    unpaid_fines = cursor.fetchone()['total'] or 0
    
    # Get appeals
    cursor.execute('''
        SELECT a.*, vr.total_fine FROM appeals a
        JOIN violation_records vr ON a.violation_id = vr.id
        WHERE a.user_id = ?
        ORDER BY a.created_at DESC
    ''', (session['user_id'],))
    appeals = cursor.fetchall()
    
    conn.close()
    
    return render_template('user/dashboard.html', violations=violations, 
                         appeals=appeals, total_violations=total_violations, 
                         unpaid_fines=unpaid_fines)

@user_bp.route('/check-violation', methods=['POST'])
@login_required
def check_violation():
    data = request.get_json()
    
    facts = {
        'vehicle': data.get('vehicle'),
        'helmet': data.get('helmet'),
        'speed': int(data.get('speed', 0)),
        'license': data.get('license'),
        'registration': data.get('registration', 'yes'),
        'red_light': data.get('red_light', 'no'),
        'phone': data.get('phone', 'no'),
        'alcohol': data.get('alcohol', 'no')
    }
    
    result = check_violations(facts)
    
    # Save violation if detected
    if result['status'] == 'violation':
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO violation_records 
            (user_id, vehicle_type, has_helmet, speed, has_license, violations, total_fine, status, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            facts.get('vehicle'),
            facts.get('helmet'),
            facts.get('speed'),
            facts.get('license'),
            json.dumps(result['violations']),
            result['fine'],
            'pending',
            'Self-reported violation'
        ))
        conn.commit()
        conn.close()
    
    return jsonify(result)

@user_bp.route('/appeals/<int:violation_id>', methods=['POST'])
@login_required
def submit_appeal(violation_id):
    reason = request.form.get('reason')
    
    if not reason or len(reason) < 10:
        return jsonify({'success': False, 'message': 'Appeal reason must be at least 10 characters'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify violation belongs to user
    cursor.execute('SELECT id FROM violation_records WHERE id = ? AND user_id = ?',
                  (violation_id, session['user_id']))
    if not cursor.fetchone():
        return jsonify({'success': False, 'message': 'Violation not found'})
    
    try:
        cursor.execute('''
            INSERT INTO appeals (violation_id, user_id, reason, status)
            VALUES (?, ?, ?, ?)
        ''', (violation_id, session['user_id'], reason, 'pending'))
        conn.commit()
        return jsonify({'success': True, 'message': 'Appeal submitted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@user_bp.route('/profile')
@login_required
def profile():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    return render_template('user/profile.html', user=user)

@user_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET first_name = ?, last_name = ?, email = ?, phone = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (first_name, last_name, email, phone, session['user_id']))
        conn.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

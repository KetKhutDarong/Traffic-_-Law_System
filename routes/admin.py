from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for
from utils.decorators import login_required, role_required
from utils.db import get_db
from models.user import User
from models.violation import Violation
from services.violation_service import ViolationService
import hashlib
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    violation_stats = ViolationService.get_dashboard_stats()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # System statistics
    total_users = User.get_all(role='user')
    total_officers = User.get_all(role='officer')
    
    cursor.execute('SELECT COUNT(*) as total FROM appeals WHERE status = "pending"')
    pending_appeals = cursor.fetchone()['total'] or 0
    
    # FIXED: Updated query to show driver_name instead of username
    cursor.execute('''
        SELECT 
            vr.id, 
            vr.driver_name,  -- Use driver_name instead of username
            vr.vehicle_type, 
            vr.total_fine, 
            vr.status, 
            vr.created_at,
            o.badge_number,
            u.username as officer_username  -- Show officer's username
        FROM violation_records vr
        LEFT JOIN officers o ON vr.officer_id = o.id
        LEFT JOIN users u ON o.user_id = u.id  -- Get officer's user info
        ORDER BY vr.created_at DESC LIMIT 10
    ''')
    recent_activity = cursor.fetchall()
    
    conn.close()
    
    stats = {
        'total_violations': violation_stats['total'],
        'total_collected': violation_stats['collected'],
        'total_users': len(total_users) if total_users else 0,
        'total_officers': len(total_officers) if total_officers else 0,
        'pending_appeals': pending_appeals
    }
    
    severity_stats = violation_stats['by_vehicle_type'] if violation_stats['by_vehicle_type'] else []
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_activity=recent_activity,
                         severity_stats=severity_stats)

@admin_bp.route('/users')
@role_required('admin')
def manage_users():
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/add', methods=['POST'])
@role_required('admin')
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    
    try:
        User.create(username, email, password, role)
        flash('User added successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/user/<int:user_id>/edit', methods=['POST'])
@role_required('admin')
def edit_user(user_id):
    username = request.form.get('username')
    email = request.form.get('email')
    role = request.form.get('role')
    
    try:
        User.update(user_id, username=username, email=email, role=role)
        flash('User updated successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@role_required('admin')
def delete_user(user_id):
    # Prevent admin from deleting themselves
    if session.get('user_id') == user_id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        User.delete(user_id)
        flash('User deleted successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/officers')
@role_required('admin')
def manage_officers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            u.id,
            u.username,
            u.email,
            u.first_name,
            u.last_name,
            u.role,
            u.is_active,
            u.created_at,
            o.badge_number, 
            o.department, 
            o.assigned_area,
            o.created_at as officer_since
        FROM users u
        LEFT JOIN officers o ON u.id = o.user_id
        WHERE u.role = "officer"
        ORDER BY u.created_at DESC
    ''')
    officers = cursor.fetchall()
    conn.close()
    
    return render_template('admin/officers.html', officers=officers)

@admin_bp.route('/officer/add', methods=['POST'])
@role_required('admin')
def add_officer():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    badge_number = request.form.get('badge_number')
    department = request.form.get('department')
    assigned_area = request.form.get('assigned_area')
    
    try:
        user_id = User.create(username, email, password, 'officer', first_name, last_name)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO officers (user_id, badge_number, department, assigned_area)
            VALUES (?, ?, ?, ?)
        ''', (user_id, badge_number, department, assigned_area))
        conn.commit()
        conn.close()
        flash('Officer added successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_officers'))

@admin_bp.route('/officer/<int:user_id>/edit', methods=['POST'])
@role_required('admin')
def edit_officer(user_id):
    badge_number = request.form.get('badge_number')
    department = request.form.get('department')
    assigned_area = request.form.get('assigned_area')
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE officers 
            SET badge_number = ?, department = ?, assigned_area = ?
            WHERE user_id = ?
        ''', (badge_number, department, assigned_area, user_id))
        conn.commit()
        conn.close()
        flash('Officer updated successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_officers'))

@admin_bp.route('/officer/<int:user_id>/delete', methods=['POST', 'GET'])
@role_required('admin')
def delete_officer(user_id):
    try:
        User.delete(user_id)
        flash('Officer deleted successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_officers'))

@admin_bp.route('/laws')
@role_required('admin')
def manage_laws():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM traffic_laws ORDER BY category')
    laws = cursor.fetchall()
    conn.close()
    
    return render_template('admin/laws.html', laws=laws)

@admin_bp.route('/laws/add', methods=['POST'])
@role_required('admin')
def add_law():
    law_code = request.form.get('law_code')
    description = request.form.get('description')
    fine_amount = request.form.get('fine_amount')
    category = request.form.get('category')
    severity = request.form.get('severity')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO traffic_laws (law_code, description, fine_amount, category, severity)
            VALUES (?, ?, ?, ?, ?)
        ''', (law_code, description, fine_amount, category, severity))
        conn.commit()
        return jsonify({'success': True, 'message': 'Law added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@admin_bp.route('/laws/edit/<int:law_id>', methods=['GET', 'POST'])
@role_required('admin')
def edit_law(law_id):
    conn = get_db()
    
    if request.method == 'POST':
        data = request.json
        conn.execute('''
            UPDATE traffic_laws
            SET description = ?, fine_amount = ?, category = ?, severity = ?
            WHERE id = ?
        ''', (data['description'], data['fine_amount'], data['category'], data['severity'], law_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    law = conn.execute('SELECT * FROM traffic_laws WHERE id = ?', (law_id,)).fetchone()
    conn.close()
    
    if law:
        return jsonify({
            'id': law[0],
            'law_code': law[1],
            'description': law[2],
            'fine_amount': law[3],
            'category': law[4],
            'severity': law[5],
            'active': law[6]
        })
    return jsonify({'error': 'Law not found'}), 404

@admin_bp.route('/laws/delete/<int:law_id>', methods=['DELETE'])
@role_required('admin')
def delete_law(law_id):
    conn = get_db()
    conn.execute('DELETE FROM traffic_laws WHERE id = ?', (law_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@admin_bp.route('/appeals')
@role_required('admin')
def manage_appeals():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, u.username, vr.violations, vr.total_fine
        FROM appeals a
        LEFT JOIN users u ON a.user_id = u.id
        LEFT JOIN violation_records vr ON a.violation_id = vr.id
        ORDER BY a.created_at DESC
    ''')
    appeals = cursor.fetchall()
    conn.close()
    
    return render_template('admin/appeals.html', appeals=appeals)

@admin_bp.route('/appeals/<int:appeal_id>/approve', methods=['POST'])
@role_required('admin')
def approve_appeal(appeal_id):
    response = request.form.get('response')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE appeals 
            SET status = 'approved', officer_response = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (response, session['user_id'], appeal_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Appeal approved'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@admin_bp.route('/appeals/<int:appeal_id>/reject', methods=['POST'])
@role_required('admin')
def reject_appeal(appeal_id):
    response = request.form.get('response')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE appeals 
            SET status = 'rejected', officer_response = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (response, session['user_id'], appeal_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Appeal rejected'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@admin_bp.route('/payments')
@role_required('admin')
def payments():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all violations with payment information
    cursor.execute('''
        SELECT vr.*, 
               vr.driver_name,
               vr.license_number,
               vr.plate_number,
               u.username as reported_by,
               uo.username as officer_name, 
               uo.first_name as officer_first_name, 
               uo.last_name as officer_last_name
        FROM violation_records vr
        LEFT JOIN users u ON vr.user_id = u.id
        LEFT JOIN officers o ON vr.officer_id = o.id
        LEFT JOIN users uo ON o.user_id = uo.id
        ORDER BY vr.created_at DESC
    ''')
    violations = cursor.fetchall()
    
    # Payment statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_violations,
            SUM(total_fine) as total_fines,
            SUM(CASE WHEN payment_status = 'paid' THEN total_fine ELSE 0 END) as collected,
            SUM(CASE WHEN payment_status = 'unpaid' THEN total_fine ELSE 0 END) as outstanding,
            COUNT(CASE WHEN payment_status = 'paid' THEN 1 END) as paid_violations,
            COUNT(CASE WHEN payment_status = 'unpaid' THEN 1 END) as unpaid_violations,
            COUNT(CASE WHEN payment_status = 'pending' THEN 1 END) as pending_violations
        FROM violation_records
    ''')
    stats = cursor.fetchone()
    
    conn.close()
    
    return render_template('admin/payments.html', violations=violations, stats=stats)

@admin_bp.route('/update-payment/<int:violation_id>/<status>', methods=['POST'])
@role_required('admin')
def update_payment(violation_id, status):
    if status not in ['paid', 'unpaid', 'pending', 'overdue']:
        return jsonify({'success': False, 'message': 'Invalid status'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        payment_date = datetime.now().isoformat() if status == 'paid' else None
        cursor.execute('''
            UPDATE violation_records 
            SET payment_status = ?, payment_date = ?
            WHERE id = ?
        ''', (status, payment_date, violation_id))
        conn.commit()
        return jsonify({'success': True, 'message': f'Payment status updated to {status}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for
from utils.decorators import login_required, role_required
from utils.db import get_db
from utils.expert_system import check_violations
import json
from datetime import datetime

officer_bp = Blueprint('officer', __name__, url_prefix='/officer')

@officer_bp.route('/dashboard')
@role_required('officer')
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get officer info with user details
    cursor.execute('''
        SELECT o.*, u.first_name, u.last_name, u.username, u.email 
        FROM officers o
        JOIN users u ON o.user_id = u.id
        WHERE u.id = ?
    ''', (session['user_id'],))
    officer = cursor.fetchone()
    
    if not officer:
        flash('Officer profile not found', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Get violations recorded by this officer
    cursor.execute('''
        SELECT vr.*
        FROM violation_records vr
        WHERE vr.officer_id = ?
        ORDER BY vr.created_at DESC
    ''', (officer['id'],))
    violations = cursor.fetchall()
    
    # Parse JSON violations for each violation
    parsed_violations = []
    for v in violations:
        v_dict = dict(v)
        # Parse the violations JSON string if it exists
        if v_dict['violations'] and isinstance(v_dict['violations'], str):
            try:
                v_dict['parsed_violations'] = json.loads(v_dict['violations'])
            except json.JSONDecodeError:
                # If not valid JSON, treat as comma-separated string
                v_dict['parsed_violations'] = [viol.strip() for viol in v_dict['violations'].split(',') if viol.strip()]
        else:
            v_dict['parsed_violations'] = []
        parsed_violations.append(v_dict)
    
    # Get statistics
    cursor.execute('''SELECT COUNT(*) as total FROM violation_records WHERE officer_id = ?''',
                  (officer['id'],))
    total_recorded = cursor.fetchone()['total']
    
    cursor.execute('''SELECT SUM(total_fine) as total FROM violation_records WHERE officer_id = ? AND payment_status = "paid"''',
                  (officer['id'],))
    collected_fines = cursor.fetchone()['total'] or 0
    
    conn.close()
    
    return render_template('officer/dashboard.html', 
                         officer=officer, 
                         violations=parsed_violations,
                         total_recorded=total_recorded, 
                         collected_fines=collected_fines)

@officer_bp.route('/record-violation', methods=['POST'])
@role_required('officer')
def record_violation():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get officer ID
    cursor.execute('SELECT id FROM officers WHERE user_id = ?', (session['user_id'],))
    officer = cursor.fetchone()
    
    if not officer:
        flash('Officer profile not found', 'error')
        return redirect(url_for('officer.dashboard'))
    
    # Get driver information
    driver_name = request.form.get('driver_name')
    license_number = request.form.get('license_number')
    plate_number = request.form.get('plate_number')
    vehicle_type = request.form.get('vehicle')
    
    if not driver_name or not plate_number or not vehicle_type:
        flash('Driver name, vehicle plate number and vehicle type are required', 'error')
        return redirect(url_for('officer.dashboard'))
    
    facts = {
        'vehicle': vehicle_type,
        'helmet': request.form.get('helmet'),
        'speed': int(request.form.get('speed', 0)),
        'license': request.form.get('license'),
        'registration': request.form.get('registration', 'yes'),
        'red_light': request.form.get('red_light', 'no'),
        'phone': request.form.get('phone', 'no'),
        'alcohol': request.form.get('alcohol', 'no')
    }
    
    result = check_violations(facts)
    
    try:
        cursor.execute('''
            INSERT INTO violation_records 
            (officer_id, driver_name, license_number, plate_number, vehicle_type, 
             has_helmet, speed, has_license, violations, total_fine, status, 
             description, location, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            officer['id'],
            driver_name,
            license_number,
            plate_number,
            vehicle_type,
            facts.get('helmet'),
            facts.get('speed'),
            facts.get('license'),
            json.dumps(result['violations']),
            result['fine'],
            'confirmed',
            request.form.get('description', ''),
            request.form.get('location', ''),
            'unpaid'  # Default payment status
        ))
        conn.commit()
        
        # Flash success message
        if result['violations']:
            violation_count = len(result['violations'])
            flash(f'✓ Successfully recorded {violation_count} violation(s) for {driver_name} with total fine: {result["fine"]:,} KHR', 'success')
        else:
            flash(f'No violations detected for {driver_name}', 'info')
        
    except Exception as e:
        flash(f'Error recording violation: {str(e)}', 'error')
        print(f"Database error: {str(e)}")  # For debugging
    finally:
        conn.close()
    
    return redirect(url_for('officer.dashboard'))

@officer_bp.route('/mark-paid/<int:violation_id>', methods=['POST', 'GET'])
@role_required('officer')
def mark_paid(violation_id):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE violation_records 
            SET payment_status = 'paid', payment_date = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (violation_id,))
        conn.commit()
        flash('Violation marked as paid', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('officer.dashboard'))

@officer_bp.route('/update-payment-status/<int:violation_id>/<status>', methods=['POST'])
@role_required('officer')
def update_payment_status(violation_id, status):
    if status not in ['paid', 'unpaid', 'pending', 'overdue']:
        return jsonify({'success': False, 'message': 'Invalid payment status'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        payment_date = datetime.now() if status == 'paid' else None
        cursor.execute('''
            UPDATE violation_records 
            SET payment_status = ?, payment_date = ?
            WHERE id = ?
        ''', (status, payment_date, violation_id))
        conn.commit()
        return jsonify({'success': True, 'message': f'Violation marked as {status}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@officer_bp.route('/payments')
@role_required('officer')
def payments():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get officer ID
    cursor.execute('SELECT id FROM officers WHERE user_id = ?', (session['user_id'],))
    officer = cursor.fetchone()
    
    if not officer:
        flash('Officer profile not found', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Get all violations with payment status
    cursor.execute('''
        SELECT vr.*, u.username, u.first_name, u.last_name
        FROM violation_records vr
        LEFT JOIN users u ON vr.user_id = u.id
        WHERE vr.officer_id = ?
        ORDER BY vr.created_at DESC
    ''', (officer['id'],))
    violations = cursor.fetchall()
    
    # Payment statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN payment_status = 'paid' THEN 1 ELSE 0 END) as paid_count,
            SUM(CASE WHEN payment_status = 'unpaid' THEN 1 ELSE 0 END) as unpaid_count,
            SUM(CASE WHEN payment_status = 'pending' THEN 1 ELSE 0 END) as pending_count,
            SUM(CASE WHEN payment_status = 'paid' THEN total_fine ELSE 0 END) as collected,
            SUM(CASE WHEN payment_status = 'unpaid' THEN total_fine ELSE 0 END) as outstanding
        FROM violation_records 
        WHERE officer_id = ?
    ''', (officer['id'],))
    stats = cursor.fetchone()
    
    conn.close()
    
    return render_template('officer/payments.html', violations=violations, stats=stats, officer=officer)
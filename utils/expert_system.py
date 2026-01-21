import json

def check_violations(facts):
    """Expert system engine for traffic violations - UPDATED WITH KHR VALUES"""
    violations = []
    total_fine = 0
    advice = []
    law_codes = []
    severity_level = 'none'
    
    vehicle = facts.get('vehicle')
    has_helmet = facts.get('helmet')
    speed = facts.get('speed')
    has_license = facts.get('license')
    has_registration = facts.get('registration', 'yes')
    ran_red_light = facts.get('red_light', 'no')
    using_phone = facts.get('phone', 'no')
    alcohol = facts.get('alcohol', 'no')
    
    max_severity = 0  # 0=none, 1=minor, 2=moderate, 3=severe
    
    # Rule 1: Helmet check for motorcycles
    if vehicle == 'motorcycle' and has_helmet == 'no':
        violations.append('Riding motorcycle without helmet')
        total_fine += 15000  # 60,000,000 KHR
        advice.append('Always wear a helmet when riding a motorcycle')
        law_codes.append('TL001')
        max_severity = max(max_severity, 1)
    
    # Rule 2: License check
    if has_license == 'no':
        violations.append('Driving without a valid license')
        total_fine += 50000  # 200,000,000 KHR
        advice.append('Get a proper driving license before operating any vehicle')
        law_codes.append('TL002')
        max_severity = max(max_severity, 3)
    
    # Rule 3: Vehicle registration
    if has_registration == 'no':
        violations.append('Vehicle not registered')
        total_fine += 100000  # 400,000,000 KHR
        advice.append('Register your vehicle with proper authorities')
        law_codes.append('TL010')
        max_severity = max(max_severity, 3)
    
    # Rule 4: Speed limit check
    if speed > 40:
        over_limit = speed - 40
        violations.append(f'Speeding - {over_limit} km/h over the 40 km/h limit')
        
        if over_limit <= 10:
            total_fine += 20000  # 80,000,000 KHR
            law_codes.append('TL003')
            max_severity = max(max_severity, 1)
        elif over_limit <= 20:
            total_fine += 40000  # 160,000,000 KHR
            law_codes.append('TL004')
            max_severity = max(max_severity, 2)
        else:
            total_fine += 80000  # 320,000,000 KHR
            law_codes.append('TL005')
            max_severity = max(max_severity, 3)
        
        advice.append('Follow speed limits to ensure safety')
    
    # Rule 5: Motorcycle on highway
    if vehicle == 'motorcycle' and speed > 60:
        violations.append('Motorcycle exceeding safe speed of 60 km/h')
        total_fine += 30000  # 120,000,000 KHR
        advice.append('Motorcycles should not exceed 60 km/h for safety')
        law_codes.append('TL006')
        max_severity = max(max_severity, 2)
    
    # Rule 6: Red light violation
    if ran_red_light == 'yes':
        violations.append('Running red light')
        total_fine += 100000  # 400,000,000 KHR
        advice.append('Always stop at red lights - it prevents accidents')
        law_codes.append('TL007')
        max_severity = max(max_severity, 3)
    
    # Rule 7: Phone usage
    if using_phone == 'yes':
        violations.append('Using mobile phone while driving')
        total_fine += 25000  # 100,000,000 KHR
        advice.append('Use hands-free devices or pull over to use your phone')
        law_codes.append('TL008')
        max_severity = max(max_severity, 1)
    
    # Rule 8: Driving under influence
    if alcohol == 'yes':
        violations.append('Driving under influence of alcohol')
        total_fine += 500000  # 2,000,000,000 KHR
        advice.append('NEVER drink and drive - take a taxi or use a designated driver')
        law_codes.append('TL009')
        max_severity = max(max_severity, 3)
    
    # Map severity level
    severity_map = {0: 'none', 1: 'minor', 2: 'moderate', 3: 'severe'}
    severity_level = severity_map[max_severity]
    
    # Generate result
    if len(violations) == 0:
        result = {
            'status': 'legal',
            'message': 'No violations detected. You are following traffic rules!',
            'violations': [],
            'fine': 0,
            'advice': ['Keep driving safely and responsibly'],
            'law_codes': [],
            'severity': 'none'
        }
    else:
        result = {
            'status': 'violation',
            'message': f'Found {len(violations)} violation(s)',
            'violations': violations,
            'fine': total_fine,
            'advice': advice,
            'law_codes': law_codes,
            'severity': severity_level
        }
    
    return result
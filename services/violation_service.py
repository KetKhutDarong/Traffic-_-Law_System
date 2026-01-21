from models.violation import Violation
from utils.expert_system import check_violations

class ViolationService:
    @staticmethod
    def record_violation(user_id, vehicle_type, helmet, speed, license):
        """Record a violation using the expert system"""
        facts = {
            'vehicle': vehicle_type,
            'helmet': helmet,
            'speed': speed,
            'license': license
        }
        result = check_violations(facts)
        
        if result['fine'] > 0:
            return Violation.create(
                user_id=user_id,
                vehicle_type=vehicle_type,
                violations=', '.join(result['violations']),
                total_fine=result['fine'],
                status='pending',
                payment_status='unpaid'
            )
        return None
    
    @staticmethod
    def get_user_violations(user_id):
        """Get all violations for a user"""
        return Violation.get_by_user(user_id)
    
    @staticmethod
    def get_dashboard_stats():
        """Get violation statistics for dashboard"""
        return Violation.get_stats()
    
    @staticmethod
    def mark_as_paid(violation_id):
        """Mark violation as paid"""
        return Violation.update_status(violation_id, payment_status='paid')

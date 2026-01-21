import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE = 'traffic_system.db'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_REFRESH_EACH_REQUEST = True
    
    # Role permissions mapping
    ROLE_PERMISSIONS = {
        'admin': ['view_all', 'manage_users', 'manage_officers', 'manage_laws', 'view_reports', 'manage_appeals', 'system_settings'],
        'officer': ['view_violations', 'create_violations', 'manage_own_violations', 'view_assigned_cases'],
        'user': ['view_own_violations', 'view_appeals', 'submit_appeal', 'view_profile']
    }
    
    ROLE_HIERARCHY = {'admin': 3, 'officer': 2, 'user': 1}

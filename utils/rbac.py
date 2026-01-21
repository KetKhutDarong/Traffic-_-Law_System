from config import Config

def check_permission(role, permission):
    """Check if a role has a specific permission"""
    permissions = Config.ROLE_PERMISSIONS.get(role, [])
    return permission in permissions

def get_role_hierarchy(role):
    """Get hierarchy level of a role"""
    return Config.ROLE_HIERARCHY.get(role, 0)

def can_manage_user(admin_role, target_role):
    """Check if admin can manage a user of target_role"""
    return get_role_hierarchy(admin_role) > get_role_hierarchy(target_role)

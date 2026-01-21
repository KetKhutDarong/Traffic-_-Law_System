import hashlib
from models.user import User

class AuthService:
    @staticmethod
    def hash_password(password):
        """Hash a password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify a password against its hash"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def register(username, email, password):
        """Register a new user"""
        # Check if user exists
        if User.get_by_username(username):
            return {'success': False, 'message': 'Username already exists'}
        
        try:
            user_id = User.create(username, email, password, role='user')
            return {'success': True, 'message': 'Registration successful', 'user_id': user_id}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def login(username, password):
        """Login user"""
        user = User.get_by_username(username)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        if user['password'] != hashed_pwd:
            return {'success': False, 'message': 'Invalid password'}
        
        return {'success': True, 'user': user}

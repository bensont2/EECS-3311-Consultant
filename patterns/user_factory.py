from models import Client, Consultant, Admin

# [DESIGN PATTERN: Simple Factory]
# Centralises object creation logic. It decouples the application from needing to know 
# exactly which subclass of User to instantiate based on user input.

class UserFactory:
    @staticmethod
    def create_user(role, name, email, password_hash, **kwargs):
        if role == 'client':
            return Client(name=name, email=email, password_hash=password_hash, role=role)
        elif role == 'consultant':
            return Consultant(
                name=name, 
                email=email, 
                password_hash=password_hash, 
                role=role,
                specialty=kwargs.get('specialty', ''),
                bio=kwargs.get('bio', ''),
                hourly_rate=kwargs.get('hourly_rate', 0.0),
                approval_status='pending'
            )
        elif role == 'admin':
            return Admin(name=name, email=email, password_hash=password_hash, role=role)
        else:
            raise ValueError(f"Invalid user role: {role}")
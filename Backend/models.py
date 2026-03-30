from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Base user model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

# Represents a client who books consultations.
class Client(User):
    __mapper_args__ = {'polymorphic_identity': 'client'}

class Consultant(User):
    __mapper_args__ = {'polymorphic_identity': 'consultant'}
    specialty = db.Column(db.String(100))
    bio = db.Column(db.Text)
    hourly_rate = db.Column(db.Float)
    approval_status = db.Column(db.String(20), default='pending')

# Represents a platform administrator.
class Admin(User):
    __mapper_args__ = {'polymorphic_identity': 'admin'}
    admin_level = db.Column(db.Integer, default=1)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    consultant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# A time slot a consultant marks as available for bookings.
class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consultant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)

# Status tracks the lifecycle: Requested -> Confirmed -> Completed / Cancelled.
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    consultant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    availability_id = db.Column(db.Integer, db.ForeignKey('availability.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Requested')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    client = db.relationship('User', foreign_keys=[client_id])
    consultant = db.relationship('User', foreign_keys=[consultant_id])
    service = db.relationship('Service')
    availability = db.relationship('Availability')

# Records a payment transaction linked to a booking.
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    transaction_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    method_type = db.Column(db.String(50), nullable=False)
    display_label = db.Column(db.String(100), nullable=False)
    encrypted_details = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)

# Admins update these at runtime without requiring a code deploy.
class SystemPolicy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy_name = db.Column(db.String(100), unique=True, nullable=False)
    policy_value = db.Column(db.String(255), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# In-app notifications sent to any user type.
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
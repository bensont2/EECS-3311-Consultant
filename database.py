from models import db, User, Client, Consultant, Admin, Service, Availability, SystemPolicy
from werkzeug.security import generate_password_hash
from datetime import date, time, timedelta

def seed_db():
    db.create_all()
    
    if Admin.query.first():
        return
        
    admin = Admin(
        name="System Admin", 
        email="admin@platform.com", 
        password_hash=generate_password_hash("admin123"),
        role="admin"
    )
    db.session.add(admin)

    policy = SystemPolicy(policy_name="cancellation_hours", policy_value="24", updated_by=1)
    db.session.add(policy)

    c1 = Consultant(
        name="Alice Finance", email="alice@test.com", 
        password_hash=generate_password_hash("password123"), role="consultant",
        specialty="Investment Banking", hourly_rate=150.0, approval_status="approved"
    )
    c2 = Consultant(
        name="Bob Taxes", email="bob@test.com", 
        password_hash=generate_password_hash("password123"), role="consultant",
        specialty="Tax Planning", hourly_rate=100.0, approval_status="approved"
    )
    db.session.add_all([c1, c2])
    db.session.commit()

    client1 = Client(name="John Doe", email="client1@test.com", password_hash=generate_password_hash("password123"), role="client")
    client2 = Client(name="Jane Smith", email="client2@test.com", password_hash=generate_password_hash("password123"), role="client")
    db.session.add_all([client1, client2])
    
    s1 = Service(name="Portfolio Review", description="Full review.", duration_minutes=60, base_price=150.0, consultant_id=c1.id)
    s2 = Service(name="Tax Strategy", description="Tax audit.", duration_minutes=30, base_price=50.0, consultant_id=c2.id)
    db.session.add_all([s1, s2])
    db.session.commit()

    today = date.today()
    slots = [
        Availability(consultant_id=c1.id, date=today + timedelta(days=2), start_time=time(10,0), end_time=time(11,0)),
        Availability(consultant_id=c1.id, date=today + timedelta(days=3), start_time=time(14,0), end_time=time(15,0)),
        Availability(consultant_id=c2.id, date=today + timedelta(days=1), start_time=time(9,0), end_time=time(9,30))
    ] 
    db.session.add_all(slots)
    db.session.commit()
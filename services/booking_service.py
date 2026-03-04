from datetime import datetime, timedelta
from models import db, Booking, SystemPolicy, Availability
from patterns.booking_state import get_state_object

def transition_booking(booking, action):
    state = get_state_object(booking.status)
    if action == 'confirm':
        state.confirm(booking)
    elif action == 'reject':
        state.reject(booking)
    elif action == 'cancel':
        check_cancellation_policy(booking)
        state.cancel(booking)
        if booking.availability:
            booking.availability.is_booked = False
    elif action == 'pay':
        state.process_payment(booking)
    elif action == 'complete':
        state.complete(booking)
    else:
        raise ValueError("Unknown action.")
    db.session.commit()

def check_cancellation_policy(booking):
    policy = SystemPolicy.query.filter_by(policy_name='cancellation_hours').first()
    hours = int(policy.policy_value) if policy else 24
    
    avail = booking.availability
    if not avail:
        return
        
    booking_datetime = datetime.combine(avail.date, avail.start_time)
    if datetime.now() + timedelta(hours=hours) > booking_datetime:
        raise Exception(f"Bookings must be cancelled at least {hours} hours in advance.")
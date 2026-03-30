from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import db, Availability, Booking
from services.booking_service import transition_booking
from services.notification_service import create_notification
from datetime import datetime

consultant_bp = Blueprint('consultant', __name__, url_prefix='/consultant')

def consultant_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'consultant':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@consultant_bp.route('/dashboard')
@consultant_required
def dashboard():
    requests = Booking.query.filter_by(consultant_id=session['user_id'], status='Requested').all()
    return render_template('consultant/dashboard.html', requests=requests)

@consultant_bp.route('/availability', methods=['GET', 'POST'])
@consultant_required
def availability():
    if request.method == 'POST':
        date_obj = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        start = datetime.strptime(request.form['start_time'], '%H:%M').time()
        end = datetime.strptime(request.form['end_time'], '%H:%M').time()
        
        avail = Availability(consultant_id=session['user_id'], date=date_obj, start_time=start, end_time=end)
        db.session.add(avail)
        db.session.commit()
        flash('Availability added.')
        
    slots = Availability.query.filter_by(consultant_id=session['user_id']).all()
    return render_template('consultant/availability.html', slots=slots)

@consultant_bp.route('/requests')
@consultant_required
def requests_view():
    bookings = Booking.query.filter_by(consultant_id=session['user_id']).all()
    return render_template('consultant/requests.html', bookings=bookings)

@consultant_bp.route('/accept/<int:booking_id>', methods=['POST'])
@consultant_required
def accept(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    try:
        transition_booking(booking, 'confirm')
        create_notification(booking.client_id, f"Booking {booking.id} confirmed.")
        flash('Booking accepted.')
    except Exception as e:
        flash(str(e))
    return redirect(url_for('consultant.requests_view'))

@consultant_bp.route('/reject/<int:booking_id>', methods=['POST'])
@consultant_required
def reject(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    try:
        transition_booking(booking, 'reject')
        booking.availability.is_booked = False
        create_notification(booking.client_id, f"Booking {booking.id} rejected.")
        flash('Booking rejected.')
    except Exception as e:
        flash(str(e))
    return redirect(url_for('consultant.requests_view'))

@consultant_bp.route('/complete/<int:booking_id>', methods=['POST'])
@consultant_required
def complete(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    try:
        transition_booking(booking, 'complete')
        flash('Booking marked as complete.')
    except Exception as e:
        flash(str(e))
    return redirect(url_for('consultant.requests_view'))
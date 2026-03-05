from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import db, Service, Availability, Booking, PaymentMethod, Payment
from services.booking_service import transition_booking
from services.payment_service import execute_transaction
from services.notification_service import create_notification
import json

client_bp = Blueprint('client', __name__, url_prefix='/client')

def client_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'client':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@client_bp.route('/dashboard')
@client_required
def dashboard():
    bookings = Booking.query.filter_by(client_id=session['user_id']).all()
    return render_template('client/dashboard.html', bookings=bookings)

@client_bp.route('/services')
@client_required
def services():
    all_services = Service.query.all()
    availabilities = Availability.query.filter_by(is_booked=False).all()
    return render_template('client/services.html', services=all_services, availabilities=availabilities)

@client_bp.route('/book/<int:availability_id>', methods=['GET', 'POST'])
@client_required
def book(availability_id):
    avail = Availability.query.get_or_404(availability_id)
    service = Service.query.filter_by(consultant_id=avail.consultant_id).first()
    
    if request.method == 'POST':
        booking = Booking(
            client_id=session['user_id'], consultant_id=avail.consultant_id,
            service_id=service.id, availability_id=avail.id, notes=request.form.get('notes')
        )
        avail.is_booked = True
        db.session.add(booking)
        db.session.commit()
        create_notification(avail.consultant_id, f"New booking request from Client ID {session['user_id']}")
        flash('Booking requested successfully.')
        return redirect(url_for('client.dashboard'))
        
    return render_template('client/book.html', avail=avail, service=service)

@client_bp.route('/cancel/<int:booking_id>', methods=['POST'])
@client_required
def cancel(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    try:
        transition_booking(booking, 'cancel')
        create_notification(booking.consultant_id, f"Booking {booking.id} was cancelled.")
        flash('Booking cancelled.')
    except Exception as e:
        flash(str(e))
    return redirect(url_for('client.bookings'))

@client_bp.route('/bookings')
@client_required
def bookings():
    user_bookings = Booking.query.filter_by(client_id=session['user_id']).all()
    return render_template('client/bookings.html', bookings=user_bookings)

@client_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@client_required
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if request.method == 'POST':
        try:
            method = request.form.get('payment_method', 'credit_card')

            details = {
                # credit/debit
                'card_number': request.form.get('card_number'),
                'expiry':      request.form.get('expiry'),
                'cvv':         request.form.get('cvv'),
                # paypal
                'email':          request.form.get('email'),
                # bank transfer
                'account_number': request.form.get('account_number'),
                'routing_number': request.form.get('routing_number'),
            }

            txn_id = execute_transaction(booking.id, session['user_id'], booking.service.base_price, method, details)
            transition_booking(booking, 'pay')
            create_notification(booking.consultant_id, f"Payment received for booking {booking.id}")
            flash(f'Payment successful! TXN: {txn_id}')
            return redirect(url_for('client.bookings'))
        except Exception as e:
            flash(str(e))
    return render_template('client/payment.html', booking=booking)

@client_bp.route('/payment-methods', methods=['GET', 'POST'])
@client_required
def payment_methods():
    if request.method == 'POST':
        details = {'card': request.form.get('card_number')}
        pm = PaymentMethod(
            client_id=session['user_id'], method_type='credit_card',
            display_label=request.form.get('label'), encrypted_details=json.dumps(details)
        )
        db.session.add(pm)
        db.session.commit()
        flash('Payment method added.')
    methods = PaymentMethod.query.filter_by(client_id=session['user_id']).all()
    return render_template('client/payment_methods.html', methods=methods)

@client_bp.route('/payment-methods/<int:id>', methods=['POST'])
@client_required
def delete_payment_method(id):
    pm = PaymentMethod.query.get_or_404(id)
    db.session.delete(pm)
    db.session.commit()
    flash('Method removed.')
    return redirect(url_for('client.payment_methods'))

@client_bp.route('/payment-history')
@client_required
def payment_history():
    payments = Payment.query.filter_by(client_id=session['user_id']).all()
    return render_template('client/payment_history.html', payments=payments)
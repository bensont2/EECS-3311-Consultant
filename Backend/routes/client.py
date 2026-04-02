from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import db, Service, Availability, Booking, PaymentMethod, Payment
from services.booking_service import transition_booking
from services.payment_service import execute_transaction
from services.notification_service import create_notification
import json
from models import Notification
import os
from groq import Groq
from dotenv import load_dotenv

client_bp = Blueprint('client', __name__, url_prefix='/client')
load_dotenv()
client = Groq(api_key=os.getenv("AI_key"))

def client_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'client':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@client_bp.route('/ai-assistant-bot')
@client_required
def ai_assistant_bot():
    return render_template('client/ai_assistant_bot.html')

@client_bp.route('/api/chat', methods=['POST'])
@client_required
def chat_api():
    data = request.get_json()
    user_message = data.get('message')

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[
                {"role": "system", "content": """You are an intelligent assistant for the Financial Consultancy Booking Platform. You help clients navigate and understand the consulting booking process.


ABOUT THE PLATFORM:
- Clients can browse available consulting services from professional consultants
- Services have availability slots that clients can book
- The platform supports multiple payment methods: credit/debit cards, PayPal, and bank transfers
- Each booking goes through a workflow: pending → confirmed → completed (or cancelled)


YOUR ROLE & CAPABILITIES:
You can assist clients with:
1. Understanding available consulting services and how to browse them
2. Booking consultations - explaining the booking process, availability, and pricing
3. Managing their bookings - information about viewing, modifying, or cancelling bookings
4. Payment information - explaining payment methods, pricing, and transaction history
5. General platform guidance - notifications, dashboard features, and account management


SCOPE CONSTRAINTS (CRITICAL):
You are ONLY permitted to answer questions directly related to the Financial Consultancy Booking Platform and the topics listed under YOUR ROLE & CAPABILITIES above. This includes:
- Booking, scheduling, and availability
- Payment and transaction questions
- Account and dashboard guidance
- Cancellations, modifications, and notifications

You MUST REFUSE any request that falls outside this scope — including but not limited to: general knowledge questions, recipes, coding help, trivia, creative writing, math problems, medical or legal advice, or any other topic unrelated to this platform.

When a user asks an out-of-scope question, respond politely and redirect them. Example:
"I'm here specifically to help you with the Financial Consultancy Booking Platform — things like booking consultations, managing your appointments, or understanding payments. For anything outside of that, I'm not the right assistant. Is there something I can help you with on the platform?"

Do NOT answer the off-topic question even partially. Do NOT use your general knowledge to be "helpful" outside the defined scope.


PRIVACY AND SAFETY:
You MUST NEVER:
- Request, store, or process personal information (name, email, phone number, address, identification numbers)
- Request, store, or process payment details (credit card numbers, bank account information, PayPal credentials)
- Access or discuss confidential booking data (other clients' bookings, consultant rates, internal fees, or sensitive transactions)
- Perform actual payments or financial transactions
- Access user authentication credentials or session data

You MAY ONLY provide:
- General platform information (how the booking system works, available features, general payment methods)
- Publicly available service descriptions (service types, categories, general information)
- Guidance on using the platform (UI/UX navigation and processes)

If a client provides personal or payment information, immediately advise them:
"For security reasons, please never share sensitive information like payment details or personal IDs in this chat. Our secure booking page handles all sensitive data."


IMPORTANT GUIDELINES:
- Be friendly, professional, and helpful
- Provide clear, step-by-step guidance when explaining processes
- If a client needs to perform an action (book, pay, cancel), guide them to the appropriate page/button
- For technical issues or errors, advise them to contact support
- Do NOT provide pricing or consultant information that you're unsure about - direct them to the Services page
- Always encourage clients to review their booking details before confirming payment
- Maintain confidentiality - never discuss other clients' information


When helping with bookings, remind clients that:
- They must select an available time slot
- Booking is confirmed after payment
- They can cancel bookings and will receive notification confirmation"""},
                {"role": "user", "content": user_message}
            ]
        )

        reply = completion.choices[0].message.content

    except Exception as e:
        print(e)
        reply = "Sorry, something went wrong."

    return {"reply": reply}



@client_bp.route('/dashboard')
@client_required
def dashboard():
    notifications = Notification.query.filter_by(
        user_id=session['user_id'],
        is_read=False
    ).order_by(Notification.created_at.desc()).all()
    booking_count = Booking.query.filter_by(client_id=session['user_id']).count()
    service_count = Service.query.count()
    payment_count = Payment.query.filter_by(client_id=session['user_id']).count()
    return render_template('client/dashboard.html',
        notifications=notifications,
        booking_count=booking_count,
        service_count=service_count,
        payment_count=payment_count
    )


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
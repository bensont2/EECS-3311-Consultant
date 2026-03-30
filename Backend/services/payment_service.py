import time
import uuid
from patterns.payment_strategy import (
    PaymentContext, CreditCardPayment, DebitCardPayment, 
    PayPalPayment, BankTransferPayment
)
from models import db, Payment, Booking

def execute_transaction(booking_id, client_id, amount, method_type, details):
    strategies = {
        'credit_card': CreditCardPayment(),
        'debit_card': DebitCardPayment(),
        'paypal': PayPalPayment(),
        'bank_transfer': BankTransferPayment()
    }
    
    strategy = strategies.get(method_type)
    if not strategy:
        raise ValueError("Invalid payment method selected.")
        
    context = PaymentContext(strategy)
    context.execute_payment(amount, details)
    
    
    time.sleep(2)
    
    txn_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    
    payment = Payment(
        booking_id=booking_id,
        client_id=client_id,
        amount=amount,
        method=method_type,
        status='success',
        transaction_id=txn_id
    )
    db.session.add(payment)
    return txn_id
import re
from datetime import datetime

# DESIGN PATTERN: Strategy
# Different payment methods require different validation logic. The Strategy pattern lets 
# you swap payment algorithms at runtime without changing the core client code.

class PaymentStrategy:
    def process_payment(self, amount, details):
        raise NotImplementedError("Subclasses must implement process_payment")

class CreditCardPayment(PaymentStrategy):
    def process_payment(self, amount, details):
        card_num = details.get('card_number', '').replace(' ', '')
        expiry = details.get('expiry', '')
        cvv = details.get('cvv', '')
        
        if not re.match(r'^\d{16}$', card_num):
            raise ValueError("Invalid credit card number.")
        if not re.match(r'^\d{2}/\d{2}$', expiry):
            raise ValueError("Invalid expiry format (MM/YY).")
        if not re.match(r'^\d{3,4}$', cvv):
            raise ValueError("Invalid CVV.")
        
        return True

class DebitCardPayment(CreditCardPayment):
    pass 

class PayPalPayment(PaymentStrategy):
    def process_payment(self, amount, details):
        email = details.get('email', '')
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError("Invalid PayPal email address.")
        return True

class BankTransferPayment(PaymentStrategy):
    def process_payment(self, amount, details):
        account = details.get('account_number', '')
        routing = details.get('routing_number', '')
        if not account or not routing:
            raise ValueError("Bank transfer requires account and routing numbers.")
        return True

class PaymentContext:
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy
        
    def execute_payment(self, amount, details):
        return self._strategy.process_payment(amount, details)
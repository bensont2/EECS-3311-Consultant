# [DESIGN PATTERN: State]
# Booking has complex state-dependent behaviour. The State Pattern eliminates large 
# if/elif chains in the booking logic and makes each state's rules self-contained.

class BookingState:
    def confirm(self, booking):
        raise Exception(f"Cannot confirm a booking from state: {booking.status}")
    def reject(self, booking):
        raise Exception(f"Cannot reject a booking from state: {booking.status}")
    def cancel(self, booking):
        raise Exception(f"Cannot cancel a booking from state: {booking.status}") 
    def process_payment(self, booking):
        raise Exception(f"Cannot process payment for a booking in state: {booking.status}")
    def complete(self, booking):
        raise Exception(f"Cannot complete a booking from state: {booking.status}")

class RequestedState(BookingState):
    def confirm(self, booking):
        booking.status = 'Confirmed'
        # Transitions immediately to PendingPayment after confirmation
        booking.status = 'Pending Payment'
    def reject(self, booking):
        booking.status = 'Rejected'
    def cancel(self, booking):
        booking.status = 'Cancelled'

class ConfirmedState(BookingState):
    def process_payment(self, booking):
        booking.status = 'Paid'
    def cancel(self, booking):
        booking.status = 'Cancelled'

class PendingPaymentState(BookingState):
    def process_payment(self, booking):
        booking.status = 'Paid'
    def cancel(self, booking):
        booking.status = 'Cancelled'

class PaidState(BookingState):
    def complete(self, booking):
        booking.status = 'Completed'
    def cancel(self, booking):
        booking.status = 'Cancelled'

class CompletedState(BookingState):
    pass

class RejectedState(BookingState):
    pass

class CancelledState(BookingState):
    pass

def get_state_object(status):
    states = {
        'Requested': RequestedState(),
        'Confirmed': ConfirmedState(),
        'Pending Payment': PendingPaymentState(),
        'Paid': PaidState(),
        'Completed': CompletedState(),
        'Rejected': RejectedState(),
        'Cancelled': CancelledState()
    }
    return states.get(status, BookingState())
# patterns/proxy.py
"""
Proxy pattern for handling payment processing.
PaymentProxy performs extra steps like logging or checking before delegating
to the RealPaymentProcessor.
"""
class PaymentInterface:
    def pay(self, user_id, amount):
        raise NotImplementedError

class RealPaymentProcessor(PaymentInterface):
    def pay(self, user_id, amount):
        print(f"[RealPaymentProcessor] Charging ${amount:.2f} for user {user_id}.")
        return True  # Simulation of a successful payment.

class PaymentProxy(PaymentInterface):
    def __init__(self):
        self.real_processor = RealPaymentProcessor()

    def pay(self, user_id, amount):
        print("[PaymentProxy] Verifying payment details...")
        success = self.real_processor.pay(user_id, amount)
        if success:
            print("[PaymentProxy] Payment successful!")
        else:
            print("[PaymentProxy] Payment failed!")
        return success

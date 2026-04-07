import reflex as rx
import random
import string
import asyncio
from .cart_state import CartState

class PaymentState(CartState):
    """
    State managing the simulated payment flow for demo purposes.
    Inherits CartState to access total_price and cart methods.
    """
    order_id: str = ""
    status: str = "idle"  # idle, processing, success

    async def simulate_payment(self):
        """Simulate a realistic payment processing flow for demo."""
        if self.total_price <= 0:
            return

        # Generate a mock order ID
        self.order_id = "ORD-" + "".join(random.choices(string.digits, k=10))
        self.status = "processing"
        yield

        # Simulate network delay (2 seconds)
        await asyncio.sleep(2)

        # Mark as success, clear cart, redirect to orders
        self.status = "success"
        self.clear_cart()
        yield
        yield rx.redirect("/orders")

import reflex as rx
from components.navbar import navbar
from state.cart_state import CartState
from state.user_state import UserState

@rx.page(route="/payment", title="Checkout")
def payment() -> rx.Component:
    """Clean checkout page — shows price summary, redirects to Razorpay."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Order Summary", size="8", margin_top="2rem", margin_bottom="1rem"),
                rx.grid(
                    # Left Column: Shipping & Security Info
                    rx.vstack(
                        rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon(tag="shield-check", size=24, color="blue"),
                                    rx.heading("Secure Checkout", size="4"),
                                    spacing="2",
                                ),
                                rx.divider(),
                                rx.text("Your payment is 100% secure and encrypted.", size="2", color="gray"),
                                rx.text("Powered by Razorpay Payment Gateway.", size="2", color="gray"),
                                rx.badge("Test Mode Active", color_scheme="orange"),
                                width="100%",
                                align_items="start",
                                spacing="4",
                            ),
                            padding="1.5rem",
                            width="100%",
                            shadow="md",
                        ),
                        rx.card(
                            rx.vstack(
                                rx.heading("Shipping Information", size="4"),
                                rx.divider(),
                                rx.text(UserState.customer_display_name, weight="bold"),
                                rx.text("Standard Delivery (3-5 business days)", size="2"),
                                rx.text("Free Shipping on this order", size="2", color="green"),
                                width="100%",
                                align_items="start",
                                spacing="4",
                            ),
                            padding="1.5rem",
                            width="100%",
                            shadow="md",
                            margin_top="1rem",
                        ),
                        width="100%",
                    ),
                    # Right Column: Price Breakdown + Pay Button
                    rx.card(
                        rx.vstack(
                            rx.heading("Price Summary", size="4", margin_bottom="1rem"),
                            rx.hstack(
                                rx.text("Subtotal", color="gray"),
                                rx.spacer(),
                                rx.text("₹", CartState.total_price),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.text("Tax (GST 18%)", color="gray"),
                                rx.spacer(),
                                rx.text("₹", CartState.tax_amount),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.text("Delivery Charges", color="gray"),
                                rx.spacer(),
                                rx.text("FREE", color="green"),
                                width="100%",
                            ),
                            rx.divider(margin_y="1rem"),
                            rx.hstack(
                                rx.text("Total Payable", size="5", weight="bold"),
                                rx.spacer(),
                                rx.text(
                                    "₹",
                                    CartState.total_payable,
                                    size="5",
                                    weight="bold",
                                    color="blue",
                                ),
                                width="100%",
                            ),
                            # Hint to the user to enter the amount on Razorpay
                            rx.callout(
                                rx.hstack(
                                    rx.icon(tag="info", size=16),
                                    rx.text(
                                        "On the Razorpay page, enter the amount shown above (₹",
                                        CartState.total_payable,
                                        ") to complete your payment.",
                                        size="2",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                                color_scheme="blue",
                                variant="surface",
                                margin_top="1rem",
                                width="100%",
                            ),
                            rx.link(
                                rx.button(
                                    rx.icon(tag="credit-card", size=18),
                                    "Pay Now with Razorpay",
                                    color_scheme="blue",
                                    size="4",
                                    width="100%",
                                    margin_top="1rem",
                                ),
                                href=CartState.direct_payment_url,
                                is_external=True,
                                width="100%",
                            ),
                            rx.text(
                                "You will be redirected to Razorpay's secure payment page in a new tab.",
                                size="1",
                                color="gray",
                                text_align="center",
                                margin_top="0.5rem",
                                width="100%",
                            ),
                            width="100%",
                            align_items="start",
                        ),
                        padding="2rem",
                        width="100%",
                        shadow="lg",
                        background_color="#fff",
                    ),
                    columns="2",
                    spacing="6",
                    width="100%",
                    margin_top="1rem",
                ),
                width="100%",
                align_items="center",
            ),
            size="3",
        ),
        background_color="#f2f5f7",
        min_height="100vh",
    )

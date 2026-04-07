import reflex as rx
from components.navbar import navbar

@rx.page(route="/checkout", title="Checkout")
def checkout() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Secure Checkout", size="8", margin_top="3rem", margin_bottom="2rem"),
                
                rx.card(
                    rx.vstack(
                        rx.input(placeholder="Full Name", width="100%", size="3"),
                        rx.input(placeholder="Phone Number", width="100%", size="3"),
                        rx.text_area(placeholder="Delivery Address", width="100%", size="3"),
                        
                        rx.link(
                            rx.button("Proceed to Payment", color_scheme="blue", size="3", width="100%", margin_top="1rem"),
                            href="/payment",
                            width="100%"
                        ),
                        width="100%"
                    ),
                    padding="2rem",
                    width="100%",
                    max_width="500px",
                    shadow="lg"
                ),
                
                width="100%",
                align_items="center"
            ),
            size="3"
        )
    )

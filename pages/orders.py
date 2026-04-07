import reflex as rx
from components.navbar import navbar

@rx.page(route="/orders", title="Order History")
def orders() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.heading("Order History", size="8", margin_top="3rem"),

            size="3"
        )
    )

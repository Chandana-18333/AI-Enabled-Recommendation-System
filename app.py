import reflex as rx
from state.products import ProductsState  # 🔥 import your state


def product_card(item):
    return rx.box(
        rx.image(
            src=item.get("ImageURL", "/placeholder.jpg"),
            width="120px",
            height="120px",
        ),
        rx.text(item.get("Product_Display_Name", "No Name"), font_weight="bold"),
        rx.text(f"₹{item.get('Price', '0')}"),
        rx.text(f"⭐ {item.get('Rating', 'N/A')}"),
        border="1px solid #ddd",
        padding="10px",
        border_radius="10px",
        width="150px",
    )


def index():
    return rx.container(
        rx.vstack(
            rx.heading("🛍️ Product Store"),

            rx.input(
                placeholder="Search...",
                on_change=ProductsState.update_search,
            ),

            rx.select(
                ["default", "low_to_high", "high_to_low"],
                on_change=ProductsState.update_sort,
            ),

            # 🔥 IMPORTANT PART
            rx.cond(
                ProductsState.all_products,
                rx.grid(
                    rx.foreach(
                        ProductsState.all_products,
                        lambda item: product_card(item),
                    ),
                    columns="4",
                    spacing="4",
                ),
                rx.text("No products found"),
            ),
        ),
        padding="20px",
    )


# 🔥 CRITICAL LINE (DON’T MISS)
app = rx.App()
app.add_page(index, route="/", on_load=ProductsState.fetch_products)
app.compile()
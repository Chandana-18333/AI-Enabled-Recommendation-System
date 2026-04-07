import reflex as rx
from state.wishlist_state import WishlistState

def product_card(product: dict) -> rx.Component:
    """
    A reusable product card component.
    Expects a dictionary representing a product from our dataset.
    """
    # Safe fallback values for UI
    img_url = rx.cond(
        product.contains("ImageURL"),
        product["ImageURL"],
        "/placeholder.jpg",
    )
    brand = rx.cond(
        product.contains("Brand"),
        product["Brand"],
        "Unknown Brand",
    )
    category = rx.cond(
        product.contains("Category"),
        product["Category"],
        "",
    )

    display_name = rx.cond(
        product.contains("Product_Display_Name"),
        product["Product_Display_Name"],
        rx.cond(
            product.contains("ProductName"),
            product["ProductName"],
            rx.cond(
                (brand != "") | (category != ""),
                f"{brand} {category}".strip(),
                "Product",
            ),
        ),
    )
    description = rx.cond(
        product.contains("Description"),
        product["Description"],
        "",
    )
    
    return rx.card(
        rx.vstack(
            rx.image(
                src=img_url, 
                height="150px", 
                width="100%", 
                object_fit="cover",
                fallback="https://via.placeholder.com/150"
            ),
            rx.box(
                rx.text(display_name, font_weight="bold", font_size="md", no_of_lines=1),
                rx.text(description, color="gray", font_size="xs", no_of_lines=2, margin_top="0.25rem"),
                margin_top="0.5rem"
            ),
            rx.hstack(
                # Use dataset rating if available
                rx.badge("★ ", product.get("Rating", "N/A"), color_scheme="green"),
                rx.spacer(),
                rx.text(f"₹{product['Price']}", font_weight="bold", color="blue.600"),
                width="100%",
                padding_top="0.5rem"
            ),
            rx.hstack(
                rx.link(
                    rx.button("View Detail", width="100%"),
                    href=f"/product/{product['ProdID']}",
                    flex="1"
                ),
                rx.button(
                    rx.icon("heart"),
                    color_scheme="red",
                    variant="soft",
                    on_click=WishlistState.add_to_wishlist(product)
                ),
                width="100%",
                margin_top="1rem",
                spacing="2"
            ),
            
            align_items="start",
            height="100%",
            justify_content="space-between"
        ),
        shadow="sm",
        _hover={"shadow": "md", "transform": "translateY(-2px)", "transition": "all 0.2s"},
        overflow="hidden",
        border_radius="md",
        width="100%"
    )

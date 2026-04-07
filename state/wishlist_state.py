import reflex as rx
from typing import List, Dict, Any


class WishlistState(rx.State):
    """State for managing the user's wishlist."""
    wishlist_items: List[Dict[str, Any]] = []

    def add_to_wishlist(self, product: Dict[str, Any]):
        """Add a product to the wishlist if it doesn't already exist."""
        product_id = product.get("ProdID")
        already_in = any(item.get("ProdID") == product_id for item in self.wishlist_items)
        if not already_in:
            self.wishlist_items.append(product.copy())
            return rx.toast.success("Added to Wishlist!", position="top-right")
        else:
            return rx.toast.info("Already in Wishlist!", position="top-right")

    def remove_from_wishlist(self, product_id):
        """Remove a product from the wishlist by its ProdID."""
        self.wishlist_items = [
            item for item in self.wishlist_items if item.get("ProdID") != product_id
        ]

    @rx.var
    def wishlist_count(self) -> int:
        return len(self.wishlist_items)

import reflex as rx
from state.user_state import UserState

@rx.page(route="/profile", title="User Profile")
def profile() -> rx.Component:
    """
    Displays user info and mock order history.
    """
    return rx.container(
        rx.vstack(
            rx.heading("User Profile", size="8", margin_bottom="2rem"),
            
            rx.cond(
                UserState.logged_in,
                rx.card(
                    rx.vstack(
                        rx.avatar(fallback="U", size="5", margin_bottom="1rem"),
                        
                        rx.hstack(
                            rx.text("Internal User ID:", font_weight="bold"),
                            rx.text(UserState.user_id.to_string()),
                        ),
                        
                        rx.hstack(
                            rx.text("Firebase UID:", font_weight="bold"),
                            rx.text(UserState.firebase_uid),
                        ),
                        
                        rx.hstack(
                            rx.text("Status:", font_weight="bold"),
                            rx.badge(
                                rx.cond(UserState.is_new_user, "New User", "Returning User"), 
                                color_scheme=rx.cond(UserState.is_new_user, "green", "blue")
                            )
                        ),
                        
                        rx.divider(margin_top="1rem", margin_bottom="1rem"),
                        
                        rx.button("Log Out", on_click=UserState.logout, color_scheme="red", width="100%"),
                        
                        align_items="start",
                        width="100%"
                    ),
                    width="100%",
                    max_width="400px",
                    padding="2rem"
                ),
                
                rx.box(
                    rx.text("You are not logged in.", margin_bottom="1rem"),
                    rx.link(rx.button("Go to Login"), href="/login")
                )
            ),
            
            padding_top="4rem",
            align_items="center",
            width="100%"
        ),
        size="3",
        margin="auto"
    )

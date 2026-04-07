import reflex as rx
from state.user_state import UserState
from components.navbar import navbar

@rx.page(route="/login", title="Log In")
def login() -> rx.Component:
    """Authentication login page simulated heavily for Reflex without active Firebase listeners."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Log In to Your Account", size="8", margin_bottom="1rem"),
                rx.text("Access your personalized AI recommendations.", color="gray", margin_bottom="2rem"),
                
                rx.card(
                    rx.vstack(
                        rx.input(placeholder="Email Address", width="100%", size="3", on_change=UserState.set_email),
                        rx.input(placeholder="Password", type="password", width="100%", size="3", margin_bottom="1rem", on_change=UserState.set_password),
                        
                        rx.cond(
                            UserState.auth_error != "",
                            rx.text(UserState.auth_error, color="red", size="2", margin_bottom="1rem")
                        ),
                        
                        rx.button("Secure Login", on_click=UserState.login_with_firebase, width="100%", color_scheme="blue", size="3"),
                        
                        rx.cond(
                            UserState.logged_in,
                            rx.callout(
                                "Successfully Logged In! Redirecting...", 
                                icon="check_circle", 
                                color_scheme="green", 
                                margin_top="1rem", 
                                width="100%"
                            ),
                            rx.text("Don't have an account?", margin_top="2rem", color="gray")
                        ),
                        rx.cond(
                            ~UserState.logged_in,
                            rx.link("Sign Up Here", href="/signup", color="blue.500", weight="bold")
                        ),
                        
                        align_items="center",
                        width="100%"
                    ),
                    padding="3rem",
                    width="100%",
                    max_width="450px",
                    shadow="lg",
                    border_radius="xl",
                    background_color="white"
                ),
                
                padding_top="10vh",
                width="100%",
                align_items="center"
            ),
            size="4"
        ),
        background_color="#f9fafb",
        min_height="100vh"
    )

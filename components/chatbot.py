import reflex as rx
import os
import pandas as pd

def _get_top_products_context(data_path="cleaned_data.csv", top_n=8) -> str:
    """Load top-rated products from CSV and format them as readable context for the AI."""
    try:
        df = pd.read_csv(data_path)
        required = ['ProdID', 'Rating', 'Category', 'Brand']
        if not all(c in df.columns for c in required):
            return ""

        # Compute price from ProdID (same logic as home page)
        def compute_price(pid):
            base = (int(pid) * 137 + 479) % 4500
            return max(199, base)

        agg = {'Rating': 'mean', "User's ID": 'count', 'Category': 'first', 'Brand': 'first'}
        if 'Product_Display_Name' in df.columns:
            agg['Product_Display_Name'] = 'first'

        stats = df.groupby('ProdID').agg(agg).rename(columns={"User's ID": 'Reviews'})
        top = stats.sort_values(by=['Rating', 'Reviews'], ascending=[False, False]).head(top_n).reset_index()

        lines = []
        for _, row in top.iterrows():
            name = str(row.get('Product_Display_Name', f"{row['Brand']} {row['Category']}"))[:55]
            price = compute_price(int(row['ProdID']))
            rating = round(float(row['Rating']), 1)
            lines.append(f"ProdID: {row['ProdID']} | Name: {name} | Brand: {row['Brand']} | Price: ₹{price:,} | Rating: {rating}⭐")

        return "Top-rated products in our dataset:\n" + "\n".join(lines)
    except Exception:
        return ""


class ChatState(rx.State):
    is_open: bool = False
    messages: list[dict[str, str]] = [
        {"role": "assistant", "content": "Hi! I'm your AI shopping assistant. Ask me about best sellers, recommendations, or any product!"}
    ]
    current_input: str = ""

    def toggle_chat(self):
        self.is_open = not self.is_open

    def set_current_input(self, val: str):
        self.current_input = val

    def send_message(self):
        if not self.current_input.strip():
            return

        user_text = self.current_input
        self.messages.append({"role": "user", "content": user_text})
        self.current_input = ""
        yield

        target_key = os.getenv("GROQ_API_KEY", "")
        if not target_key:
            self.messages.append({"role": "assistant", "content": "⚠️ Please set GROQ_API_KEY in your .env file and restart."})
            return

        try:
            import groq
            client = groq.Groq(api_key=target_key)

            product_context = _get_top_products_context()
            system_prompt = (
                "You are a helpful AI shopping assistant for an Indian e-commerce store. "
                "IMPORTANT RULES:\n"
                "1. Always use Indian Rupees (₹) for ALL prices. NEVER use $ or USD.\n"
                "2. NEVER output raw CSV data, column names, or table formats.\n"
                "3. Present product lists as a clean, readable bulleted list.\n"
                "4. CRITICAL: Every product you list MUST include a clickable Markdown link in the format: [View Product](/product/PROD_ID_HERE).\n"
                "5. Keep text responses friendly and concise.\n"
                "6. When asked about best-selling or top-rated products, use the data below.\n\n"
                + product_context
            )

            api_messages = [{"role": "system", "content": system_prompt}] + self.messages

            chat_completion = client.chat.completions.create(
                messages=api_messages,
                model="llama-3.1-8b-instant",
            )
            bot_response = chat_completion.choices[0].message.content
            self.messages.append({"role": "assistant", "content": bot_response})

        except Exception as e:
            self.messages.append({"role": "assistant", "content": f"API Error: {str(e)}"})


def chatbot() -> rx.Component:
    """Floating AI assistant for the E-commerce app."""
    return rx.box(
        rx.cond(
            ChatState.is_open,
            rx.card(
                rx.vstack(
                    # ── Header ────────────────────────────────────────────
                    rx.hstack(
                        rx.icon(tag="bot", color="blue"),
                        rx.heading("AI Assistant", size="4"),
                        rx.spacer(),
                        rx.button(
                            rx.icon("x"),
                            size="1",
                            variant="ghost",
                            on_click=ChatState.toggle_chat,
                        ),
                        width="100%",
                        border_bottom="1px solid #eaeaea",
                        padding_bottom="0.5rem",
                    ),

                    # ── Messages ──────────────────────────────────────────
                    rx.vstack(
                        rx.foreach(
                            ChatState.messages,
                            lambda m: rx.box(
                                rx.markdown(m["content"]),
                                background_color=rx.cond(
                                    m["role"] == "user", "blue.100", "gray.100"
                                ),
                                color=rx.cond(m["role"] == "user", "blue.900", "black"),
                                padding="0.75rem",
                                border_radius="lg",
                                align_self=rx.cond(
                                    m["role"] == "user", "flex-end", "flex-start"
                                ),
                                max_width="85%",
                                # Apply basic styling to links within markdown
                                sx={
                                    "p": {"margin_bottom": "0.5em", "font_size": "0.875rem"},
                                    "ul": {"padding_left": "1.25em"},
                                    "a": {"color": "#4f46e5", "font_weight": "bold", "text_decoration": "none"},
                                    "a:hover": {"text_decoration": "underline"}
                                }
                            ),
                        ),
                        width="100%",
                        height="380px",
                        overflow_y="auto",
                        padding_y="1rem",
                        align_items="stretch",
                        spacing="2",
                    ),

                    # ── Input ─────────────────────────────────────────────
                    rx.hstack(
                        rx.input(
                            placeholder="Ask about products...",
                            value=ChatState.current_input,
                            on_change=ChatState.set_current_input,
                            on_key_down=lambda e: rx.cond(
                                e == "Enter", ChatState.send_message(), rx.noop()
                            ),
                            width="100%",
                        ),
                        rx.button(
                            rx.icon("send"),
                            on_click=ChatState.send_message,
                            color_scheme="blue",
                        ),
                        width="100%",
                    ),

                    width="100%",
                    height="100%",
                    spacing="2",
                ),
                position="fixed",
                bottom="5rem",
                right="2rem",
                width="390px",
                shadow="2xl",
                border_radius="lg",
                z_index="2000",
                background_color="white",
            ),
        ),

        # ── FAB ───────────────────────────────────────────────────────────
        rx.button(
            rx.icon(tag="message-circle", size=24),
            position="fixed",
            bottom="2rem",
            right="2rem",
            size="4",
            border_radius="full",
            color_scheme="indigo",
            shadow="xl",
            on_click=ChatState.toggle_chat,
            z_index="2000",
        ),
    )

import os
import reflex as rx
from reflex.plugins import SitemapPlugin
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use REFLEX_API_URL when provided by deployed environments.
# Fall back to local Reflex runtime in development.
api_url = os.environ.get("https://ai-enabled-recommendation-engine-for-an-e-commerce-platform-sil.reflex.run")

config = rx.Config(
    app_name="AI_Enabled_Recommendation_Engine_for_an_E_commerce_Platform",
    api_url="https://ai-enabled-recommendation-engine-for-an-e-commerce-platform-sil.reflex.run",
    plugins=[SitemapPlugin()],
    # Backend configuration for Reflex deployment
    # Ensures backend/ directory is included in the deployment
    include_directories=["backend", "components", "pages", "state", "assets"],
)

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Security ---
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_change_me")
API_KEY_SECRET = os.getenv("API_KEY_SECRET", "default_api_key_change_me")

# --- Database ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Dine@2003"),
    "database": os.getenv("DB_NAME", "face_recognition"),
    "pool_name": "face_rec_pool",
    "pool_size": 5,
}

# --- LLM ---
API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- SMTP ---
SMTP_CONFIG = {
    "server": os.getenv("SMTP_SERVER"),
    "port": int(os.getenv("SMTP_PORT", 587)),
    "user": os.getenv("SMTP_USER"),
    "password": os.getenv("SMTP_PASSWORD"),
}
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")


# --- Paths ---
PREDICTOR_PATH = os.getenv(
    "SHAPE_PREDICTOR_PATH", "shape_predictor_68_face_landmarks.dat"
)
PLOT_DIR = os.getenv("PLOT_DIR", "plots")
REPORT_DIR = os.getenv("REPORT_DIR", "reports")

# --- Ensure Directories Exist ---
for dir_path in [PLOT_DIR, REPORT_DIR]:
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")
        except Exception as e:
            print(f"Error creating directory {dir_path}: {e}")

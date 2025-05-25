# 1. Monkey Patch FIRST!
import eventlet

eventlet.monkey_patch()

# 2. Standard Library Imports
import os
import logging
import re  # <-- Import re here for the /get-plot fix

# 3. Flask and Extensions Imports
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_caching import Cache

# 4. Local Module Imports
from auth import api_key_required
from utils import handle_question
from dashboard_queries import get_kpi_stats, get_visit_trend, get_top_visitors
from reports import generate_and_email_report
from config import PLOT_DIR, SECRET_KEY
# Import manager AFTER app and socketio are created or use a function.

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)  # Log to console
logger = logging.getLogger(__name__)

# --- App Initialization ---
app = Flask(__name__)  # No static_folder needed if served via route
app.config["SECRET_KEY"] = SECRET_KEY
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300

# --- Extensions ---
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Be more specific for production
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
cache = Cache(app)

# --- Set SocketIO instance for Manager ---
# Import manager *after* socketio is defined
from recognition_manager import recognition_manager_instance, set_socketio_instance

set_socketio_instance(socketio)

# --- API Endpoints ---


@app.route("/api/recognition/start", methods=["POST"])
@api_key_required
def start_rec():
    data = request.get_json() or {}
    logger.info(f"Received start recognition request: {data}")
    result = recognition_manager_instance.start(
        data.get("start_time"), data.get("end_time")
    )
    return jsonify(result)


@app.route("/api/recognition/stop", methods=["POST"])
@api_key_required
def stop_rec():
    logger.info("Received stop recognition request.")
    result = recognition_manager_instance.stop()
    return jsonify(result)


@app.route("/api/recognition/status", methods=["GET"])
@api_key_required
def status_rec():
    result = recognition_manager_instance.get_status()
    return jsonify(result)


@app.route("/api/chat", methods=["POST"])
@api_key_required
def chat():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "No question provided"}), 400
    question = data["question"]
    logger.info(f"Chat question: {question}")
    summary, plot_filename = handle_question(question)
    return jsonify({"summary": summary, "plotFilename": plot_filename})


# IMPORTANT: Removing @api_key_required for DEMO purposes as discussed.
# Add better security (signed URLs/tokens) for production.
@app.route("/api/get-plot/<filename>", methods=["GET"])
def get_plot(filename):
    logger.info(f"Serving plot: {filename}")
    # Security: Ensure filename is safe (e.g., only hex and .png)
    if not re.match(r"^[a-f0-9]+\.png$", filename):
        logger.warning(f"Invalid plot filename requested: {filename}")
        return "Invalid filename", 400
    try:
        return send_from_directory(PLOT_DIR, filename, mimetype="image/png")
    except FileNotFoundError:
        logger.error(f"Plot file not found: {filename}")
        return "Plot not found", 404


@app.route("/api/dashboard/stats", methods=["GET"])
@api_key_required
@cache.cached(timeout=60)
def dashboard_stats():
    logger.debug("Fetching dashboard stats.")
    stats = get_kpi_stats()
    return jsonify(stats)


@app.route("/api/dashboard/visit-trend", methods=["GET"])
@api_key_required
@cache.cached(timeout=300)
def dashboard_visit_trend():
    logger.debug("Fetching visit trend.")
    trend = get_visit_trend()
    return jsonify(trend)


@app.route("/api/dashboard/top-visitors", methods=["GET"])
@api_key_required
@cache.cached(timeout=300)
def dashboard_top_visitors():
    logger.debug("Fetching top visitors.")
    top = get_top_visitors()
    return jsonify(top)


@app.route("/api/reports/generate", methods=["POST"])
@api_key_required
def generate_report_api():
    data = request.get_json()
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    if not start_date or not end_date:
        return jsonify(
            {"status": "error", "message": "Start and end dates are required."}
        ), 400
    logger.info(f"Generating report from {start_date} to {end_date}.")
    result = generate_and_email_report(start_date, end_date)
    return jsonify(result)


# --- SocketIO Events ---
@socketio.on("connect")
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    # Send initial status on connect
    socketio.emit(
        "rec_status_update", recognition_manager_instance.get_status(), room=request.sid
    )


@socketio.on("disconnect")
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")


# --- Frontend Serving ---
@app.route("/")
def serve_index():
    return send_from_directory("frontend", "dashboard.html")


@app.route("/<path:path>")
def serve_frontend_files(path):
    # Basic security: prevent accessing parent directories or hidden files.
    if ".." in path or path.startswith("."):
        return "Not Found", 404

    # Use os.path.join for safer path construction
    # Use os.path.abspath to prevent path traversal issues
    base_dir = os.path.abspath(os.path.join(os.getcwd(), "frontend"))
    requested_path = os.path.abspath(os.path.join(base_dir, path))

    # Check if the requested path is within the frontend directory
    if not requested_path.startswith(base_dir):
        return "Not Found", 404

    if os.path.exists(requested_path) and not os.path.isdir(requested_path):
        return send_from_directory("frontend", path)
    else:
        logger.warning(f"Frontend file not found or is a directory: {path}")
        # If not found, you might want to return index.html for Single Page Apps
        # but here we return 404.
        return "Not Found", 404


# --- Main Execution ---
if __name__ == "__main__":
    logger.info("Starting Flask-SocketIO server with eventlet...")
    # Make sure Plot and Report dirs exist before starting
    from config import PLOT_DIR, REPORT_DIR  # Re-import locally if needed

    os.makedirs(PLOT_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    # Run with eventlet
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False)

import cv2
import threading
import time
import datetime
from main import FaceProcessor
import logging

logger = logging.getLogger(__name__)

# This will be set by app.py after initialization
socketio = None  # <-- NO 'from app import socketio' HERE!


def set_socketio_instance(sio):
    """Sets the global socketio instance."""
    global socketio
    socketio = sio
    logger.info("SocketIO instance set for RecognitionManager.")


class RecognitionManager:
    def __init__(self):
        self.running = False
        self.thread = None
        self.face_processor = FaceProcessor()
        self.start_time_obj = None  # Use datetime.time objects
        self.end_time_obj = None
        self.lock = threading.Lock()
        self.last_status_emit = 0
        self.camera_index = 0  # Default camera index

    def _emit_status(self):
        """Emits the current status via SocketIO if available."""
        global socketio
        if socketio:
            current_time = time.time()
            if current_time - self.last_status_emit > 5:  # Emit every 5 secs
                status = self.get_status()
                # Use socketio.emit - it handles multiple clients
                socketio.emit("rec_status_update", status)
                self.last_status_emit = current_time
        # else:
        #     logger.debug("SocketIO not yet set, cannot emit status.")

    def _recognition_loop(self):
        logger.info(f"Attempting to open camera index {self.camera_index}...")
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            logger.error(f"Error: Could not open webcam index {self.camera_index}.")
            with self.lock:
                self.running = False
            self._emit_status()  # Emit stopped status
            return

        logger.info(f"Recognition loop started (Camera {self.camera_index}).")

        while True:
            with self.lock:
                if not self.running:
                    break

            self._emit_status()

            now = datetime.datetime.now().time()
            in_schedule = True  # Assume running unless proven otherwise
            if self.start_time_obj and self.end_time_obj:
                if self.start_time_obj <= self.end_time_obj:
                    if not (self.start_time_obj <= now <= self.end_time_obj):
                        in_schedule = False
                else:
                    if not (now >= self.start_time_obj or now <= self.end_time_obj):
                        in_schedule = False

            if not in_schedule:
                logger.debug("Outside scheduled time. Sleeping.")
                time.sleep(30)
                continue

            ret, frame = cap.read()
            if not ret:
                logger.warning("Warning: Could not read frame, skipping.")
                time.sleep(1)
                continue

            try:
                results = self.face_processor.process_frame(frame)
                if results and socketio:
                    logger.debug(f"Recognition Results: {results}")
                    socketio.emit("new_recognition", {"results": results})
            except Exception as e:
                logger.error(f"Error processing frame: {e}", exc_info=True)

            time.sleep(1)

        cap.release()
        logger.info("Recognition loop stopped and camera released.")
        self._emit_status()

    def start(self, start_str=None, end_str=None):
        with self.lock:
            if self.running:
                return {"status": "error", "message": "Recognition already running."}

            self.start_time_obj = None
            self.end_time_obj = None

            if start_str and end_str:
                try:
                    self.start_time_obj = datetime.datetime.strptime(
                        start_str, "%H:%M"
                    ).time()
                    self.end_time_obj = datetime.datetime.strptime(
                        end_str, "%H:%M"
                    ).time()
                    logger.info(
                        f"Recognition scheduled between {start_str} and {end_str}."
                    )
                except ValueError:
                    return {
                        "status": "error",
                        "message": "Invalid time format. Use HH:MM.",
                    }
            else:
                logger.info("Recognition starting immediately (continuous).")

            self.running = True
            self.thread = threading.Thread(target=self._recognition_loop, daemon=True)
            self.thread.start()
            return {"status": "success", "message": "Recognition process initiated."}

    def stop(self):
        with self.lock:
            if not self.running:
                return {"status": "error", "message": "Recognition not running."}
            self.running = False
            logger.info("Stop signal sent to recognition thread.")

        if self.thread:
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning("Recognition thread did not stop cleanly.")
        self.thread = None
        return {"status": "success", "message": "Recognition stopped."}

    def get_status(self):
        return {"running": self.running, "scheduled": bool(self.start_time_obj)}


recognition_manager_instance = RecognitionManager()

import cv2
import face_recognition
import numpy as np
import uuid
import datetime
from cachetools import TTLCache
import faiss
from config import PREDICTOR_PATH
from database import fetch_all_customers_for_rec, insert_customer, update_customer_visit
import os
import logging

logger = logging.getLogger(__name__)


# --- FAISS functions ---
def build_faiss_index(customers):
    if not customers:
        return None, []
    valid_customers = [c for c in customers if c.get("face_encoding")]
    if not valid_customers:
        return None, []

    encodings_list = [
        np.frombuffer(c["face_encoding"], dtype=np.float64) for c in valid_customers
    ]

    # Ensure all encodings have the same dimension (128)
    X_list = [enc for enc in encodings_list if enc.shape == (128,)]
    if not X_list:
        return None, []

    X = np.array(X_list).astype("float32")

    if X.shape[0] == 0:
        return None, []

    index = faiss.IndexFlatL2(X.shape[1])
    index.add(X)
    # Map index back to customer unique_id for *valid* encodings
    id_list = [
        c["unique_id"]
        for c, enc in zip(valid_customers, encodings_list)
        if enc.shape == (128,)
    ]
    return index, id_list


def search_faiss_index(index, id_list, face_encoding, threshold=0.6):
    if index is None or not id_list:
        return None
    face_encoding_np = np.array(face_encoding).astype("float32").reshape(1, -1)
    D, I = index.search(face_encoding_np, 1)
    if D.size > 0 and I.size > 0 and D[0][0] < threshold:
        idx = I[0][0]
        if 0 <= idx < len(id_list):
            return id_list[idx]
    return None


# --- Face Recognition Core ---
class FaceProcessor:
    def __init__(self):
        if not os.path.exists(PREDICTOR_PATH):
            logger.error(f"Predictor file not found: {PREDICTOR_PATH}")
            raise FileNotFoundError(f"Predictor file not found: {PREDICTOR_PATH}")
        self.customers = []
        self.faiss_index = None
        self.id_list = []
        self.known_encodings = []
        self.known_ids = []
        self.cache = TTLCache(maxsize=500, ttl=3600)  # 1 hour cache
        self.refresh_data()

    def refresh_data(self):
        logger.info("Refreshing customer data for face recognition...")
        try:
            self.customers = fetch_all_customers_for_rec()
            if not self.customers:
                logger.warning("No customers found in DB or no encodings available.")
                self.customers = []
                self.faiss_index, self.id_list = None, []
                self.known_encodings, self.known_ids = [], []
                return

            self.faiss_index, self.id_list = build_faiss_index(self.customers)

            valid_customers = [c for c in self.customers if c.get("face_encoding")]
            encodings_list = [
                np.frombuffer(c["face_encoding"], dtype=np.float64)
                for c in valid_customers
            ]

            self.known_encodings = [
                enc for enc in encodings_list if enc.shape == (128,)
            ]
            self.known_ids = [
                c["unique_id"]
                for c, enc in zip(valid_customers, encodings_list)
                if enc.shape == (128,)
            ]

            logger.info(f"Data refreshed. {len(self.known_ids)} known faces loaded.")
        except Exception as e:
            logger.error(f"Error refreshing face recognition data: {e}")

    def process_frame(self, frame):
        """Processes a single frame for faces and identifies/adds customers."""
        if not self.known_ids:
            logger.warning(
                "No known faces loaded, attempting refresh before processing."
            )
            self.refresh_data()
            if not self.known_ids:
                logger.warning("Still no known faces after refresh, skipping frame.")
                return []

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Use a smaller frame for faster detection (optional)
        # small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        results = []

        for encoding in face_encodings:
            customer_id = None
            is_new = False

            # 1. Try FAISS
            faiss_id = search_faiss_index(self.faiss_index, self.id_list, encoding)

            if faiss_id:
                customer_id = faiss_id
            elif self.known_encodings:  # Only search if known_encodings exist
                # 2. Try face_recognition.compare_faces
                matches = face_recognition.compare_faces(
                    self.known_encodings, encoding, tolerance=0.6
                )
                if True in matches:
                    first_match_index = matches.index(True)
                    customer_id = self.known_ids[first_match_index]

            # 3. If still no match, it's a new customer
            if not customer_id:
                unique_id = str(uuid.uuid4())
                encoding_blob = encoding.tobytes()
                insert_customer(
                    unique_id, None, None, encoding_blob, datetime.datetime.now(), 1
                )
                logger.info(f"New customer detected: {unique_id}")
                customer_id = unique_id
                is_new = True
                self.refresh_data()  # Refresh data immediately after adding

            # 4. Update visit / Cache Check
            if customer_id and customer_id not in self.cache:
                if not is_new:
                    logger.info(f"Existing customer seen: {customer_id}")
                    update_customer_visit(customer_id)
                self.cache[customer_id] = True
                results.append({"customer_id": customer_id, "new": is_new})
            elif customer_id:
                logger.debug(f"Customer in cache: {customer_id}")

        return results

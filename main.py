# main.py
"""
Main entry point for the Face Recognition Customer Management System.
Handles video capture, face recognition, customer analytics, and natural language database queries.
Follows PEP 8 and professional Pythonic style.
"""

import mysql.connector
import cv2
import dlib
import face_recognition_models
import face_recognition
import numpy as np
import uuid
import datetime
from cachetools import TTLCache
import faiss
from utils import handle_question
from utils import (
    generate_visit_history_report,
    plot_visit_analytics,
    export_customers_to_excel,
)
from config import DB_CONFIG


# Database functions
def create_connection():
    return mysql.connector.connect(**DB_CONFIG)


def insert_customer(
    conn, unique_id, name, email, face_encoding, last_visited, visit_count
):
    cursor = conn.cursor()
    query = """INSERT INTO customers (unique_id, name, email, face_encoding, last_visited, visit_count) VALUES (%s, %s, %s, %s, %s, %s)"""
    cursor.execute(
        query, (unique_id, name, email, face_encoding, last_visited, visit_count)
    )
    conn.commit()


def update_customer_visit(conn, customer_id):
    cursor = conn.cursor()
    query = """UPDATE customers SET last_visited = NOW(), visit_count = visit_count + 1 WHERE unique_id = %s"""
    cursor.execute(query, (str(customer_id),))
    conn.commit()


def fetch_customers(conn):
    cursor = conn.cursor()
    query = """SELECT * FROM customers"""
    cursor.execute(query)
    return cursor.fetchall()


conn = create_connection()


def is_existing_customer(face_encoding, customers):
    for customer in customers:
        db_encoding = np.frombuffer(customer[4], dtype=np.float64)
        if face_recognition.compare_faces([db_encoding], face_encoding, tolerance=0.6)[
            0
        ]:
            return True, customer
    return False, None


def save_new_customer(face_encoding):
    unique_id = str(uuid.uuid4())  # Generate a unique ID
    name = None  # No longer ask for name
    email = None  # No longer ask for email
    encoding_blob = face_encoding.tobytes()
    last_visited = datetime.datetime.now()  # Set to current time
    visit_count = 1
    insert_customer(
        conn, unique_id, name, email, encoding_blob, last_visited, visit_count
    )
    return unique_id, name, email


def build_faiss_index(customers):
    if not customers:
        return None, []
    X = np.array(
        [np.frombuffer(customer[4], dtype=np.float64) for customer in customers]
    ).astype("float32")
    index = faiss.IndexFlatL2(X.shape[1])
    index.add(X)
    return index, [customer[1] for customer in customers]  # [unique_id, ...]


def search_faiss_index(index, id_list, face_encoding, threshold=0.6):
    if index is None or len(id_list) == 0:
        return False, None
    face_encoding = np.array(face_encoding).astype("float32").reshape(1, -1)
    D, I = index.search(face_encoding, 1)
    if D[0][0] < threshold:
        return True, id_list[I[0][0]]
    return False, None


# Fetch existing customers and build FAISS index
customers = fetch_customers(conn)
faiss_index, id_list = build_faiss_index(customers)

# Set up a cache with a max size and a TTL (in seconds)
# Example: max 1000 customers, 1 hour TTL (3600 seconds)
customer_cache = TTLCache(maxsize=1000, ttl=3600)

# Initialize dlib's face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Initialize the video stream
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB (face_recognition uses RGB format)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame)

    for face_location in face_locations:
        # Get the facial encoding
        face_encoding = face_recognition.face_encodings(rgb_frame, [face_location])[0]

        # Use FAISS for fast matching
        is_existing_faiss, customer_id = search_faiss_index(
            faiss_index, id_list, face_encoding, threshold=0.6
        )

        if is_existing_faiss:
            # Find the customer record by unique_id
            customer = next((c for c in customers if c[1] == customer_id), None)
            customer_name = customer[2] if customer else None
            # Double check with face_recognition
            if customer:
                db_encoding = np.frombuffer(customer[4], dtype=np.float64)
                if face_recognition.compare_faces(
                    [db_encoding], face_encoding, tolerance=0.6
                )[0]:
                    if customer_id in customer_cache:
                        print(
                            f"Customer {customer_id} is in cache, skipping DB update."
                        )
                    else:
                        print(
                            f"Existing customer detected by FAISS and confirmed by face_recognition. Customer ID: {customer_id}, Name: {customer_name}"
                        )
                        update_customer_visit(conn, customer_id)
                        customer_cache[customer_id] = True
                else:
                    print(
                        "FAISS match, but face_recognition did not confirm. Treating as new customer."
                    )
                    unique_id, name, email = save_new_customer(face_encoding)
                    customer_cache[unique_id] = True
                    customers = fetch_customers(conn)
                    faiss_index, id_list = build_faiss_index(customers)
            else:
                print(
                    "FAISS found a customer_id, but no matching record in DB. Skipping."
                )
        else:
            # Use face_recognition.compare_faces for final check
            is_existing, customer = is_existing_customer(face_encoding, customers)
            if is_existing:
                customer_id = customer[1]
                customer_name = customer[2]
                if customer_id in customer_cache:
                    print(f"Customer {customer_id} is in cache, skipping DB update.")
                else:
                    print(
                        f"Existing customer detected by face_recognition. Customer ID: {customer_id}, Name: {customer_name}"
                    )
                    update_customer_visit(conn, customer_id)
                    customer_cache[customer_id] = True
            else:
                print("New customer detected. Saving to database.")
                unique_id, name, email = save_new_customer(face_encoding)
                customer_cache[unique_id] = True
                customers = fetch_customers(conn)
                faiss_index, id_list = build_faiss_index(customers)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release video resources and close OpenCV windows
cap.release()
cv2.destroyAllWindows()

# Generate reports and analytics
generate_visit_history_report(conn)
plot_visit_analytics(conn)
export_customers_to_excel(conn)

# Example: handle a natural language question
user_input = "what pattern did you understand this whole db data from this database?"
summary = handle_question(user_input)
print(f"\nLLM Summary: {summary}")

# Close the database connection
conn.close()

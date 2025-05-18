# Customer Recognition System

This project is a Face Recognition Customer Management System that handles video capture, face recognition, customer analytics, and natural language database queries. It uses Python and several libraries for face detection, database management, and analytics.

## Features

- Real-time face recognition using `dlib` and `face_recognition`.
- Customer data storage and management using MySQL.
- Analytics and reporting for customer visits.
- Natural language query handling for database insights.

## Prerequisites

Before running the project, ensure you have the following installed:

1. Python 3.8.10
2. MySQL server.
3. CMake and Visual Studio Build Tools (for `dlib` and `face_recognition`).

## Installation

1. Clone the repository or download the project files.

2. Navigate to the project directory:

   ```bash
   cd customer_recognition
   ```

3. Create and activate a virtual environment:

   ```bash
   pip install uv
   uv venv
   
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

4. Install the required Python packages using the following commands:

   ```bash
    uv pip install -r requirements.txt
   ```

   If you want to use the GPU version of FAISS, replace the last command with:

   ```bash
   uv pip install faiss-gpu
   ```

5. Ensure the `shape_predictor_68_face_landmarks.dat` file is present in the project directory. This file is required for facial landmark detection.

6. Configure the database connection in `config.py` by updating the `DB_CONFIG` dictionary with your MySQL credentials.

## Database Setup

Before running the project, you need to create the `customer_recognition` table in your MySQL database. Use the following SQL command to create the table:

```sql
CREATE TABLE customers (
    unique_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    face_encoding BLOB,
    last_visited DATETIME,
    visit_count INT
);
```

This table includes the following columns:
- `unique_id`: A unique identifier for each customer.
- `name`: The name of the customer (can be NULL).
- `email`: The email address of the customer (can be NULL).
- `face_encoding`: A binary representation of the customer's face encoding.
- `last_visited`: The last time the customer visited.
- `visit_count`: The total number of visits by the customer.

## Running the Project

1. Start the MySQL server and ensure the database is set up with the required schema.

2. Run the main script(before run main script ensure to activate the virtual envionment):

   ```bash
   python main.py
   ```

3. The application will start capturing video from your webcam and perform real-time face recognition.

4. Press `q` to quit the application.

## Additional Information

- Reports and analytics will be generated and saved as files in the project directory.
- Ensure your webcam is connected and accessible for the application to work.

## Troubleshooting

- If you encounter issues with `dlib` installation, ensure you have CMake and Visual Studio Build Tools installed on your system.
- For any database-related errors, verify your MySQL server is running and the credentials in `config.py` are correct.

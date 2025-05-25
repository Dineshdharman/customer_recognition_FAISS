# Face Recognition Customer Management System

## Project Overview

This project is a "Face Recognition Customer Management System" designed to identify customers in real-time via webcam, manage their information and visit history in a database, and provide insights through an intelligent chatbot and a dynamic dashboard. It leverages computer vision for identification, a Python/Flask backend for core logic and API services, and a SvelteKit frontend for user interaction.

**Core Features:**
* **Real-Time Face Recognition:** Identifies known customers and registers new ones using live webcam feed.
* **Customer Database:** Stores customer profiles, face encodings, and visit history in a MySQL database.
* **Intelligent Chatbot:** Allows users to ask natural language questions about customer data, get summaries, and request data visualizations.
* **Dynamic Dashboard:** Displays key metrics like total customers, new customers today, visit trends, and top visitors with real-time updates.
* **Automated Reporting:** Generates CSV reports of customer visits for specified date ranges and emails them to an administrator.
* **Recognition Management:** Allows users to start/stop the face recognition process continuously or on a schedule.

## Technology Stack

* **Backend:**
    * Python 3.8+
    * Flask (Web framework)
    * Flask-SocketIO (WebSockets for real-time communication)
    * Flask-Caching (Performance enhancement)
    * OpenCV (Image/video processing)
    * dlib (Face detection and landmarking)
    * face\_recognition (Face encoding and comparison)
    * FAISS (Efficient similarity search for faces)
    * MySQL (Database)
    * mysql.connector (Python MySQL driver)
    * Pandas (Data manipulation for reports)
    * Matplotlib (Plot generation)
    * LangChain (LLM orchestration)
    * OpenRouter API (Access to Large Language Models)
    * smtplib (Email sending)
    * python-dotenv (Environment variable management)
    * eventlet (WSGI server for SocketIO)
* **Frontend (SvelteKit):**
    * SvelteKit
    * TypeScript
    * Tailwind CSS (Styling)
    * Chart.js (Data visualization)
    * socket.io-client (WebSocket client)
    * flatpickr (Date/time picker)
    * Font Awesome (Icons)
* **Database:**
    * MySQL Server (Version 8.0+ recommended)

## Project Structure

It's recommended to have two main project folders (one for backend, one for frontend) inside a parent directory:

your-main-project-folder/
├── facetrack-backend/       # Python/Flask backend
│   ├── plots/              # Auto-created for plot images
│   ├── reports/            # Auto-created for CSV reports
│   ├── .env                # YOUR Environment variables (DATABASE, API Keys, SMTP)
│   ├── app.py              # Main Flask application
│   ├── auth.py             # API key authentication
│   ├── config.py           # Configuration loader
│   ├── database.py         # Database connection and queries
│   ├── dashboard_queries.py # SQL queries for dashboard
│   ├── main_refactored.py  # Core face processing logic
│   ├── recognition_manager.py # Background thread for recognition
│   ├── reports.py          # Report generation and emailing
│   ├── requirements.txt    # Python dependencies
│   ├── utils.py            # Chatbot logic, LLM interaction, plotting
│   └── shape_predictor_68_face_landmarks.dat # dlib model file (needs download)
│
└── facetrack-svelte-frontend/ # SvelteKit frontend
├── static/
│   └── favicon.png     # (Default or your custom favicon)
├── src/
│   ├── app.css         # Global styles and Tailwind directives
│   ├── app.d.ts        # SvelteKit type definitions
│   ├── app.html        # Main HTML shell for SvelteKit
│   ├── lib/
│   │   ├── components/   # Reusable Svelte components (Sidebar, KpiCard, Charts, etc.)
│   │   │   ├── BarChart.svelte
│   │   │   ├── ChartCard.svelte
│   │   │   ├── ChatBubble.svelte
│   │   │   ├── Header.svelte
│   │   │   ├── KpiCard.svelte
│   │   │   ├── LineChart.svelte
│   │   │   ├── Notifications.svelte
│   │   │   └── Sidebar.svelte
│   │   ├── stores/       # Svelte stores (e.g., for notifications, socket status)
│   │   │   ├── notifications.ts
│   │   │   └── socket.ts
│   │   ├── api.ts        # Helper functions for API calls to backend
│   │   └── config.ts     # Frontend configuration (e.g., backend URL)
│   └── routes/           # SvelteKit pages/routes
│       ├── +layout.svelte  # Main layout for all pages
│       ├── +page.svelte      # Dashboard page
│       ├── chat/
│       │   └── +page.svelte  # Chatbot page
│       └── settings/
│           └── +page.svelte  # Settings page
├── .env                  # Frontend environment variables (VITE_BACKEND_URL, VITE_API_KEY)
├── package.json          # NPM package dependencies and scripts
├── postcss.config.cjs    # PostCSS configuration (for Tailwind)
├── svelte.config.js      # SvelteKit configuration
├── tailwind.config.cjs   # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
└── vite.config.ts        # Vite configuration

## Setup and Installation

**I. Backend Setup (`facetrack-backend/`)**

1.  **Prerequisites:**
    * Python 3.8 or newer installed.
    * MySQL Server installed and running.
    * Access to an SMTP server (e.g., Gmail with an App Password) for the email reports feature.
    * An OpenRouter API key for the chatbot functionality.

2.  **Download dlib Model File:**
    * Download the `shape_predictor_68_face_landmarks.dat` file. This file is essential for face landmark detection by the `dlib` library. You can typically find links to it on the dlib website or through web searches for "dlib shape predictor 68 download".
    * Place this downloaded file directly into your `facetrack-backend/` root directory.

3.  **Database Creation:**
    * Connect to your MySQL server (using a tool like MySQL Workbench, phpMyAdmin, or the command line).
    * Execute the following SQL commands to create the necessary database and table:
        ```sql
        CREATE DATABASE IF NOT EXISTS face_recognition;
        USE face_recognition;
        CREATE TABLE IF NOT EXISTS customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            unique_id VARCHAR(36) NOT NULL UNIQUE,
            name VARCHAR(255) NULL,
            email VARCHAR(255) NULL,
            face_encoding BLOB NOT NULL,
            last_visited TIMESTAMP NULL,
            visit_count INT DEFAULT 1,
            INDEX(unique_id)
        );
        ```

4.  **Configure Environment Variables:**
    * In the `facetrack-backend/` directory, create a file named `.env`.
    * Copy the content from the `.env` example template (provided in previous detailed responses or by looking at the variables used in `config.py`) into this file.
    * **Crucially, update the following placeholders with your actual credentials and keys:**
        * `SECRET_KEY`: A long, random string for Flask session security.
        * `API_KEY_SECRET`: A secret key that the frontend will use to authenticate with the backend API.
        * `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: Your MySQL connection details. Ensure the `DB_PASSWORD` is correct.
        * `OPENROUTER_API_KEY`: Your valid API key from OpenRouter.
        * `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`: Your email sending credentials. If using Gmail for `SMTP_USER`, you **must** use a 16-digit **App Password** for `SMTP_PASSWORD` (generated from your Google Account security settings), not your regular Gmail password.
        * `ADMIN_EMAIL`: The email address where generated reports will be sent.

5.  **Install Python Dependencies:**
    * Navigate to the `facetrack-backend/` directory in your terminal.
    * It is highly recommended to create and activate a Python virtual environment:
        ```bash
        python -m venv .venv
        # On Windows:
        .\.venv\Scripts\activate
        # On macOS/Linux:
        source .venv/bin/activate
        ```
    * Install all required libraries using the `requirements.txt` file:
        ```bash
        pip install -r requirements.txt
        ```
        *Note: Installing `dlib` can sometimes be challenging, especially on Windows. You might need to have CMake and a C++ compiler (like Visual Studio Build Tools with C++ development workload) installed first. If you encounter issues, search online for specific instructions for installing `dlib` on your operating system.*

6.  **Run the Backend Server:**
    * Ensure your virtual environment is activated.
    * From the `facetrack-backend/` directory, run:
        ```bash
        python app.py
        ```
    * The backend server should start, typically listening on `http://localhost:5000`. Observe the terminal output for any error messages, especially related to database connections. You should see logs indicating successful startup.

**II. Frontend Setup (`facetrack-svelte-frontend/`)**

1.  **Prerequisites:**
    * Node.js (which includes npm) LTS version installed (e.g., v18.x, v20.x). You can download it from [nodejs.org](https://nodejs.org/).

2.  **Initialize SvelteKit Project & Install Dependencies:**
    * If you haven't already, create the SvelteKit project:
        ```bash
        # Navigate to where you want your frontend project (e.g., your-main-project-folder/)
        npm create svelte@latest facetrack-svelte-frontend
        # Follow the prompts:
        # - Choose "Skeleton project"
        # - Select "Yes, using TypeScript syntax" (recommended)
        # - Add ESLint, Prettier (recommended)
        cd facetrack-svelte-frontend
        ```
    * Install necessary Node.js dependencies:
        ```bash
        npm install
        npm install -D tailwindcss postcss autoprefixer svelte-preprocess
        npm install chart.js socket.io-client flatpickr date-fns @fortawesome/fontawesome-free
        ```
    * Initialize Tailwind CSS (this will create `tailwind.config.cjs` and `postcss.config.cjs`):
        ```bash
        npx tailwindcss init -p
        ```
    * **Configure** `tailwind.config.cjs`, `postcss.config.cjs`, `svelte.config.js`, and `src/app.css` as per the full code examples provided in previous responses to correctly integrate Tailwind CSS.

3.  **Configure Frontend Environment Variables:**
    * In the `facetrack-svelte-frontend/` directory, create a file named `.env`.
    * Add the following lines. **Ensure `VITE_API_KEY` matches the `API_KEY_SECRET` value you set in the backend's `.env` file**:
        ```env
        VITE_BACKEND_URL=http://localhost:5000
        VITE_API_KEY=another_strong_secret_key_for_api_access_change_me
        ```

4.  **Place Component and Route Files:**
    * Create the directory structure under `src/lib/components/`, `src/lib/stores/`, and `src/routes/` as shown in the project structure.
    * Populate these directories and files with the Svelte component code (`.svelte` files) and TypeScript files (`.ts`) provided in the detailed "Full Frontend Svelte Code" response.

5.  **Run the Frontend Development Server:**
    * In your terminal, ensure you are in the `facetrack-svelte-frontend/` directory.
    * Run:
        ```bash
        npm run dev
        ```
    * This will start the SvelteKit development server, typically on `http://localhost:5173` (it will tell you the exact port). It should also automatically open this URL in your default web browser.

## Using the Application

1.  Ensure both the **backend (`python app.py` in `facetrack-backend/`)** and **frontend (`npm run dev` in `facetrack-svelte-frontend/`)** servers are running.
2.  Open your web browser and navigate to the frontend URL provided by the SvelteKit dev server (e.g., `http://localhost:5173`).
3.  **Dashboard:** View customer statistics (total customers, new today, visits today) and trends (visit trend chart, top visitors chart). These should update in near real-time based on backend activity.
4.  **Chatbot:** Interact with the AI assistant. Ask questions about your customer data in natural language (e.g., "How many customers visited last week?", "Show me a chart of new customers per day", "Hi, who are you?").
5.  **Settings:**
    * **Recognition Control:** Start continuous recognition, set a schedule for recognition (start/end times), or stop the recognition process. The status should update in real-time.
    * **Report Generation:** Select a date range using the date picker and click "Generate & Email Report". The report will be sent to the `ADMIN_EMAIL` configured in the backend's `.env` file.

## Troubleshooting Tips

* **Backend "Access Denied" for Database:** The most common issue. Double-check `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` in the backend's `.env` file. Verify the password by logging into MySQL manually. Ensure your MySQL user has the correct permissions.
* **Backend Email Failure (`[Errno 11001] No address found` or `SMTPAuthenticationError`):**
    * For `Errno 11001`: Verify `SMTP_SERVER` in `.env` is correct (e.g., `smtp.gmail.com`) and that the machine running the backend has proper internet/DNS connectivity.
    * For `SMTPAuthenticationError`: Ensure `SMTP_USER` and `SMTP_PASSWORD` are correct, and that `SMTP_PASSWORD` is a **Gmail App Password** if using Gmail.
* **Frontend Connection Errors to Backend (`ERR_CONNECTION_REFUSED` for API calls or WebSockets):**
    * Confirm the Python backend server (`app.py`) is actually running and didn't crash. Check its terminal for errors.
    * Ensure `VITE_BACKEND_URL` in the frontend's `.env` file is correct (usually `http://localhost:5000`).
* **Frontend API Errors (401 Unauthorized):** Ensure `VITE_API_KEY` in the frontend's `.env` exactly matches `API_KEY_SECRET` in the backend's `.env`.
* **Tailwind CSS Not Applying / SvelteKit Build Errors:**
    * Ensure `tailwindcss`, `postcss`, `autoprefixer` are listed in `devDependencies` in `package.json` and `npm install` completed successfully.
    * Verify all configuration files: `tailwind.config.cjs` (especially the `content` array), `postcss.config.cjs`, and `svelte.config.js` (ensure `vitePreprocess()` is used).
    * Confirm `src/app.css` starts with the `@tailwind` directives and is imported in `src/routes/+layout.svelte`.
    * If you encounter "tailwindcss not recognized" or similar when running `npx tailwindcss init -p`, it means the Tailwind CLI is not properly installed or accessible in your path. Ensure `npm install -D tailwindcss` completed successfully.
* **`Cannot find module '$lib/...'` in SvelteKit:** Check that the file exists at the specified path (e.g., `src/lib/api.ts`) and that the import statement in your Svelte component is correct.
* **Browser Console (F12):** This is your best friend for frontend issues. Always check the "Console" tab for JavaScript errors and the "Network" tab for failed API requests (404s, 401s, 500s) or WebSocket connection problems.
* **Backend Terminal:** The terminal running `python app.py` will show detailed logs, including Python exceptions, SQL queries (if you enable verbose logging in `database.py`), and SocketIO events. This is crucial for diagnosing backend issues.
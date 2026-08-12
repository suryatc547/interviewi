# Python API Instructions

## Prerequisites
- Python 3.8+
- pip

## Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

2.  **Activate the virtual environment:**
    - On Windows:
      ```powershell
      .\venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  **Start the development server:**
    ```bash
    flask run
    # or
    python app.py
    ```

2.  The API will be available at `http://localhost:5000` (by default).

# interviewi

Welcome to the `interviewi` project.

## Directory Structure

The project is divided into two main parts:

- **interview-api**: The Python Flask backend application.
- **web**: The Angular frontend application.

```
interviewi/
├── interview-api/
│   ├── controllers/   # Route handlers and request processing
│   ├── models/        # Database models and schemas
│   └── services/      # Business logic and external service integrations
└── web/
    └── src/
        ├── app/       # Angular components and modules
        ├── assets/    # Static assets
        └── environments/ # Configuration files
```

## Backend (interview-api) Instructions

The backend is built using **Python** and **Flask**. It follows a layered architecture to separate concerns.

### Code Structure

- **Controllers (`controllers/`)**: 
  - Define the API endpoints (routes).
  - Parse requests and send responses.
  - Call services to perform business logic.
  - *Example*: `auth_controller.py` handles `/login` and `/register`.

- **Services (`services/`)**:
  - Contain the core business logic.
  - Interact with database models or external APIs.
  - *Example*: `auth_service.py` handles password hashing and token generation.

- **Models (`models/`)**:
  - Define the data structure (e.g., SQLAlchemy classes).
  - Interact directly with the database.
  - *Example*: `user_model.py` represents the User table.

### Flask Framework Setup

To get started with the backend:

1.  **Create a Virtual Environment**:
    ```bash
    cd interview-api
    python -m venv venv
    ```

2.  **Activate Virtual Environment**:
    - Windows: `.\venv\Scripts\Activate`
    - Mac/Linux: `source venv/bin/activate`

3.  **Install Dependencies**:
    *Ensure you have a `requirements.txt` file (create one if missing).*
    ```bash
    pip install flask
    ```

4.  **Run the Application**:
    *Create a main entry point like `app.py` or `run.py` in the `interview-api` root.*
    ```bash
    python run.py
    ```

## Frontend (web)

The frontend uses the **Angular** folder structure.

- **src/app**: Contains the main application logic, components, and modules.
- **src/assets**: Stores images, icons, and global styles.
- **src/environments**: Holds environment-specific variables (api URLs, etc).

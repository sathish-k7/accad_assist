# AI Academic Assistant API

This repository contains the backend API for the AI Academic Assistant, a powerful tool for students and educators.

## Features

- **Document Summarization**: Upload PDF, DOCX, or TXT files and receive intelligent summaries in various formats (detailed, brief, bullet points, outline).
- **Question Generation**: Automatically generate question papers for different courses, exam types, and difficulty levels.
- **Course Management**: View available courses and statistics.

## Tech Stack

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **Uvicorn**: A lightning-fast ASGI server.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd backend_API
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access the interactive API documentation at `http://localhost:8000/docs`.

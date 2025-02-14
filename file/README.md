# Bita File Service

This document provides instructions on how to set up and run the Bita File Service either by creating a virtual environment or using Docker.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Docker (optional)

## Running with Virtual Environment

1. **Clone the repository:**

    ```bash
    git clone https://github.com/gumiapps/bita_services
    cd bita_services/file
    ```

2. **Create a virtual environment:**

    ```bash
    python3 -m venv .venv
    ```

3. **Activate the virtual environment:**

    - On Windows:

        ```bash
        .\.venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```bash
        source .venv/bin/activate
        ```

4. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Set Up Environment Variables:**
    Copy .env.example to .env
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file in a text editor and update the values as needed.

6. **Run the application:**

    ```bash
    python manage.py runserver
    ```

## Running with Docker

1. **Clone the repository:**

    ```bash
    git clone https://github.com/gumiapps/bita_services
    cd bita_services/file
    ```

2. **Set Up Environment Variables:**
    Copy .env.example to .env
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file in a text editor and update the values as needed.

3. **Build the Docker image:**

    ```bash
    sudo docker compose build
    ```

4. **Run the Docker containers:**

    ```bash
    sudo docker compose up
    ```

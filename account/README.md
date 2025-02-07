# Bita Authentication Service

This document provides instructions on how to set up and run the Bita Authentication Service either by creating a virtual environment or using Docker.

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Docker (optional)

## Running with Virtual Environment

1. **Clone the repository:**

    ```bash
    git clone https://github.com/gumiapps/bita_services
    cd bita_services/account
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
    cd bita_services/account
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

## Accessing the Application

Once the application is running, you can access it at `http://localhost:8000`.

## API Documentation

You can use either swagger or redoc to browse the API docs and try out the request and response formats.
- **Swagger** - `http://localhost:8000/swagger/`
- **Redoc** - `http://localhost:8000/redoc/`

## API Endpoints

- To access the Authentication Service APIs, a valid API key must be provided in the "X-API-Key" http header.

### Authentication

- **POST /token**
  - Description: Accepts a phone number or email and authenticates a user and returns a JWT access token and a refresh token as well as the logged in user data.
  - Request Body: 
    ```json
    {
     "identifier": "912121212", 
     "password": "testpass123" 
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczODM0MDk2OSwiaWF0IjoxNzM4MjU0NTY5LCJqdGkiOiIzODk2ZDE2OWZmYmE0MTFkODAwNTAwNTg2MTdhYjEwYSIsInVzZXJfaWQiOjEsImVtYWlsIjoiYWxlYmVAZ21haWwuY29tIiwidXNlcm5hbWUiOiIifQ.QzsSNGaXGqJzydyFv9saw8Gyh53iWPipuNGfPYqDp-M",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM4MjU0ODY5LCJpYXQiOjE3MzgyNTQ1NjksImp0aSI6ImQ0Y2JhMzYxNGY3NTQ0MTRhMTcxYTVjNTFjMDJiZTU4IiwidXNlcl9pZCI6MSwiZW1haWwiOiJhbGViZUBnbWFpbC5jb20iLCJ1c2VybmFtZSI6IiJ9.l2nQrnktyRlyeKeBYeT2gu10ZWs4_NATL_T7SAd9HXU",
        "user": {
            "id": 1,
            "email": "alebe@gmail.com",
            "username": "",
            "first_name": "Alebe",
            "last_name": "",
            "phone": "924384072"
        }
    }
    ```

- **POST /token/refresh**
  - Description: Accepts a valid JWT refresh token and returns a new access token.
  - Request Body: 
    ```json
    {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczODM0MDk2OSwiaWF0IjoxNzM4MjU0NTY5LCJqdGkiOiIzODk2ZDE2OWZmYmE0MTFkODAwNTAwNTg2MTdhYjEwYSIsInVzZXJfaWQiOjEsImVtYWlsIjoiYWxlYmVAZ21haWwuY29tIiwidXNlcm5hbWUiOiIifQ.QzsSNGaXGqJzydyFv9saw8Gyh53iWPipuNGfPYqDp-M"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM4MjU1MTU2LCJpYXQiOjE3MzgyNTQ1NjksImp0aSI6IjI1M2M2NmRkZDk2YzRlN2RhZGYzOTRjNzk1YTBkOTlkIiwidXNlcl9pZCI6MSwiZW1haWwiOiJhbGViZUBnbWFpbC5jb20iLCJ1c2VybmFtZSI6IiJ9.y5g_Gm8m6Zzrdsc7pRJV3W63bgs0h9YXbY8NNxnrH3A"
    }
    ```

- **POST /token/verify**
  - Description: Accepts a JWT access token and returns a success code (200) if it is valid and 401 otherwise
  - Request Body: 
    ```json
    {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczODM0MDk2OSwiaWF0IjoxNzM4MjU0NTY5LCJqdGkiOiIzODk2ZDE2OWZmYmE0MTFkODAwNTAwNTg2MTdhYjEwYSIsInVzZXJfaWQiOjEsImVtYWlsIjoiYWxlYmVAZ21haWwuY29tIiwidXNlcm5hbWUiOiIifQ.QzsSNGaXGqJzydyFv9saw8Gyh53iWPipuNGfPYqDp-M"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "detail": "Token is valid",
        "user": {
          "email": "testuser@gmail.com",
          "first_name": "",
          "last_name": "",
          "phone": "912345678",
          "id": 1
        }
    }
    ```

### Password Management APIs

- **PUT /password-change**
  - Description: Accepts an old password and a new password from an authenticated user and changes the password from the old one to the new one.
  - Prerequisite: A valid access token in the HTTP Authorization header. e.g `Bearer {token}` and a correct old_password parameter
  - Request Body: 
    ```json
    {
        "old_password": "testpass123",
        "new_password": "testpass321",
        "new_password_confirm": "testpass321"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "detail": "Password has been changed."
    }
    ```

- **POST /password-reset**
  - Description: Accepts an email account and sends out a password reset email to that account.
  - Request Body: 
    ```json
    {
        "email": "account@example.com"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "detail": "Password reset link sent."
    }
    ```

- **POST /password-reset-confirm/{uidb64}/{token}**
  - Description: Sent out in the password reset email and only works if uidb64 and token are correct. It resets the password of a user who forgot their password.
  - Prerequisite: A correct token and uidb64 in the url.
  - Request Body: 
    ```json
    {
        "password": "string",
        "password_confirm": "string"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "detail": "Password has been reset."
    }
    ```

### User management APIs

- **GET /users?page={page_number}**
  - Description: Returns a list of registered users paginated 10 at a time.
  - Prerequisites: Must have a valid access token in the Authorization header and must be a superuser / admin.
  - Successful Response Body: 
    ```json
    {
        "count": 2,
        "next": null,
        "previous": null,
        "results": [
            {
                "email": "user1@gmail.com",
                "first_name": "user1",
                "last_name": "",
                "phone": "91313131313",
                "username": ""
            },
            {
                "email": "user3@gmail.com",
                "first_name": "user3",
                "last_name": "",
                "phone": "91414141414",
                "username": ""
            }
        ]
    }
    ```

- **POST /users**
  - Description: Registeres a new regular user account
  - Request Body:
    ```json
    {
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string",
        "phone": "981051299",
        "username": "ObDJAPuoSDHZ",
        "password": "testpass123"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string",
        "phone": "981051299",
        "username": "ObDJAPuoSDHZ"
    }
    ```

- **GET /users/{id}**
  - Description: Returns details about a user queried by id.
  - Prerequisites: The request user must be a superuser or the owner of the queried account.
  - Successful Response Body: 
    ```json
    {
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string",
        "phone": "981051299",
        "username": "ObDJAPuoSDHZ"
    }
    ```

- **PUT /users/{id}**
  - Description: Edits all the fields of a user account
  - Prerequisites: The request user must be a superuser or the owner of the queried account.
  - Request Body:
    ```json
    {
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string2",
        "phone": "981051299",
        "username": "ObDJAPuoSDHZ"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string2",
        "phone": "981051299",
        "username": "ObDJAPuoSDHZ"
    }
    ```

- **PATCH /users/{id}**
  - Description: Edits one or more of the fields shown in the example request body of a user account
  - Prerequisites: The request user must be a superuser or the owner of the queried account.
  - Request Body:
    ```json
    {
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string2",
        "phone": "981051299",
        "username": "ObDJAPuoSDHZ"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string2",
        "phone": "981051299",
        "username": "ObDJAPuoSDHZ"
    }
    ```

- **DELETE /users/{id}**
  - Description: Deletes a user account
  - Prerequisites: The request user must be a superuser or the owner of the queried account.
  - On success it sends out a 204 http status code with no response body

### Customer management APIs

- **GET /customers?page={page_number}**
  - Description: Returns a list of registered customers paginated 10 at a time.
  - Prerequisites: Must have a valid access token in the Authorization header and must be a superuser / admin.
  - Successful Response Body: 
    ```json
    {
        "count": 123,
        "next": "http://api.example.org/customers/?page=4",
        "previous": "http://api.example.org/customers/?page=2",
        "results": [
          {
            "id": 0,
            "first_name": "string",
            "last_name": "string",
            "phone": "914398326",
            "email": "user@example.com",
            "address": "string"
          }
        ]
    }
    ```

- **POST /customers**
  - Description: Registeres a new customer
  - Prerequisites: The request user must be a superuser or the owner of the queried account.
  - Request Body:
    ```json
    {
        "first_name": "string",
        "last_name": "string",
        "phone": "900740695",
        "email": "user@example.com",
        "address": "string"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "first_name": "string",
        "last_name": "string",
        "phone": "927650842",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **GET /customers/{id}**
  - Description: Returns details about a customer queried by id.
  - Prerequisites: The request user must be a superuser.
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "first_name": "string",
        "last_name": "string",
        "phone": "945367584",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **PUT /costomers/{id}**
  - Description: Edits all the fields of a customer.
  - Prerequisites: The request user must be a superuser.
  - Request Body:
    ```json
    {
        "first_name": "string",
        "last_name": "string",
        "phone": "959346791",
        "email": "user@example.com",
        "address": "string"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "first_name": "string",
        "last_name": "string",
        "phone": "947028458",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **PATCH /customers/{id}**
  - Description: Edits one or more of the fields shown in the example request body of a customer
  - Prerequisites: The request user must be a superuser.
  - Request Body:
    ```json
    {
        "first_name": "string",
        "last_name": "string",
        "phone": "959346791",
        "email": "user@example.com",
        "address": "string"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "first_name": "string",
        "last_name": "string",
        "phone": "947028458",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **DELETE /customers/{id}**
  - Description: Deletes a customer.
  - Prerequisites: The request user must be a superuser or the owner of the queried account.
  - On success it sends out a 204 http status code with no response body

### Supplier management APIs

- **GET /suppliers?page={page_number}**
  - Description: Returns a list of registered suppliers paginated 10 at a time.
  - Prerequisites: Must have a valid access token in the Authorization header and must be a superuser / admin.
  - Successful Response Body: 
    ```json
    {
        "count": 123,
        "next": "http://api.example.org/suppliers/?page=4",
        "previous": "http://api.example.org/suppliers/?page=2",
        "results": [
          {
            "id": 0,
            "name": "string",
            "phone": "914398326",
            "email": "user@example.com",
            "address": "string"
          }
        ]
    }
    ```

- **POST /suppliers**
  - Description: Registeres a new supplier
  - Prerequisites: The request user must be a superuser or the owner of the queried account.
  - Request Body:
    ```json
    {
        "name": "string",
        "phone": "900740695",
        "email": "user@example.com",
        "address": "string"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "name": "string",
        "phone": "927650842",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **GET /suppliers/{id}**
  - Description: Returns details about a supplier queried by id.
  - Prerequisites: The request user must be a superuser.
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "name": "string",
        "phone": "945367584",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **PUT /suppliers/{id}**
  - Description: Edits all the fields of a supplier.
  - Prerequisites: The request user must be a superuser.
  - Request Body:
    ```json
    {
        "name": "string",
        "phone": "959346791",
        "email": "user@example.com",
        "address": "string"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "name": "string",
        "phone": "947028458",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **PATCH /suppliers/{id}**
  - Description: Edits one or more of the fields shown in the example request body of a supplier
  - Prerequisites: The request user must be a superuser.
  - Request Body:
    ```json
    {
        "name": "string",
        "phone": "959346791",
        "email": "user@example.com",
        "address": "string"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "name": "string",
        "phone": "947028458",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **DELETE /suppliers/{id}**
  - Description: Deletes a supplier.
  - Prerequisites: The request user must be a superuser or the owner of the queried account.
  - On success it sends out a 204 http status code with no response body

### Business management APIs

- **GET /businesses?page={page_number}**
  - Description: Returns a list of registered businesses paginated 10 at a time.
  - Prerequisites: Must have a valid access token in the Authorization header.
  - Successful Response Body: 
    ```json
    {
        "count": 123,
        "next": "http://api.example.org/accounts/?page=4",
        "previous": "http://api.example.org/accounts/?page=2",
        "results": [
          {
            "id": 0,
            "created_at": "2025-02-07T16:03:17.017Z",
            "updated_at": "2025-02-07T16:03:17.017Z",
            "name": "string",
            "address": "string",
            "category": "string",
            "owner": 0
          }
        ]
    }
    ```

- **POST /businesses**
  - Description: Registeres a new business
  - Prerequisites: The request user must be a superuser or the owner of the queried account.
  - Request Body:
    ```json
    {
        "name": "string",
        "phone": "900740695",
        "email": "user@example.com",
        "address": "string"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "name": "string",
        "phone": "927650842",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **GET /suppliers/{id}**
  - Description: Returns details about a supplier queried by id.
  - Prerequisites: The request user must be a superuser.
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "name": "string",
        "phone": "945367584",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **PUT /suppliers/{id}**
  - Description: Edits all the fields of a supplier.
  - Prerequisites: The request user must be a superuser.
  - Request Body:
    ```json
    {
        "name": "string",
        "phone": "959346791",
        "email": "user@example.com",
        "address": "string"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "name": "string",
        "phone": "947028458",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **PATCH /suppliers/{id}**
  - Description: Edits one or more of the fields shown in the example request body of a supplier
  - Prerequisites: The request user must be a superuser.
  - Request Body:
    ```json
    {
        "name": "string",
        "phone": "959346791",
        "email": "user@example.com",
        "address": "string"
    }
    ```
  - Successful Response Body: 
    ```json
    {
        "id": 0,
        "name": "string",
        "phone": "947028458",
        "email": "user@example.com",
        "address": "string"
    }
    ```

- **DELETE /suppliers/{id}**
  - Description: Deletes a supplier.
  - Prerequisites: The request user must be a superuser or the owner of the queried account.
  - On success it sends out a 204 http status code with no response body
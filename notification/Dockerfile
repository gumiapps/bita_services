FROM python:3.11.4-slim-buster

# Install necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the requirements file first to cache dependencies
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port your Django app runs on
EXPOSE 8000

# Set the default command to run the Django app
CMD ["uvicorn", "notification.asgi:application", "--host", "0.0.0.0", "--port", "8000"]



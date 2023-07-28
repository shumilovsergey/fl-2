
# Base image
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED=1


# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY . .

ARG ENV_FILE
ENV ENV_FILE=${ENV_FILE}
RUN if [ "$ENV_FILE" ]; then cp "$ENV_FILE" .env; fi

# Set the port number from the environment variable
ENV PORT=5002

EXPOSE 5002
# Define volume for database
VOLUME bd:/app

# Start server
CMD python manage.py runserver 0.0.0.0:${PORT}

# Use an official Python runtime as the base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY . /code/

# Create a volume for the database
VOLUME /code/db

# Expose the port where the application will run
EXPOSE 8000

# Run the Django development server
CMD python manage.py runserver 0.0.0.0:8000
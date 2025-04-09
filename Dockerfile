FROM python:3.9-slim

# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Update package list and install system dependencies including GDAL libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Optionally set the GDAL_LIBRARY_PATH; adjust if necessary
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so

# Copy requirements.txt and install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the code
COPY . /app/

# Expose the port
EXPOSE 8000

# Default CMD (for Django via Gunicorn, for example)
CMD ["gunicorn", "turl_street_group_assignment.wsgi:application", "--bind", "0.0.0.0:8000"]

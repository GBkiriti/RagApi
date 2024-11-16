# Use the base Python image
FROM python:3.11-slim

# Update and install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    build-essential \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Download and compile the latest version of SQLite
RUN wget https://sqlite.org/2023/sqlite-autoconf-3410000.tar.gz && \
    tar xzf sqlite-autoconf-3410000.tar.gz && \
    cd sqlite-autoconf-3410000 && \
    ./configure && make && make install && \
    cd .. && rm -rf sqlite-autoconf-3410000*  # Clean up SQLite files after installation

# Verify the installed SQLite version in Python
RUN python3 -c "import sqlite3; print(sqlite3.sqlite_version)"

# Upgrade pip and install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt  # Use --no-cache-dir to reduce image size

# Copy the application code
COPY . /app

# Expose the FastAPI port
EXPOSE 8000

# Define the command to run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--reload"]
# We import the python slim 
FROM python:3.12-slim

# Avoid overwritting the files and buffering 
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create the app directory
WORKDIR /app
# Install all the dependencies that are needed for libgomp1
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    cmake \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the code which is in current directory contents into the container at /app
COPY . .

# We install the application
RUN pip install --no-cache-dir -e .

# We run the training pipeline script
RUN python pipeline/training_pipeline.py

# We expose the port the app runs on
EXPOSE 5001

# We define the command to run the application
CMD ["python", "application.py"]
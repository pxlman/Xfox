FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    libevdev-dev \
    libudev-dev \
    udev \
    && rm -rf /var/lib/apt/lists/*

# Install evdev from PyPI
RUN pip install evdev

# Create working directory
WORKDIR /app

# Copy your script into the container
COPY run.py .

# Default command to run your script
CMD ["python", "run.py"]


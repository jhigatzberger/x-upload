# Use a lightweight Python image
FROM python:3.9-slim

# Make sure we can install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sudo \
    git \
    # Additional libs for chromium, if needed:
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libgbm1 \
    libgtk-3-0 \
    # cleanup
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements.txt and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Flask app
COPY . .

EXPOSE 5000

# Run the Flask app by default
CMD ["python", "app.py"]
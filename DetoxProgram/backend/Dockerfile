FROM python:3.11-slim

# Install system dependencies, including OpenJDK JRE for KoNLPy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME pointing to the JRE installation path in debian/ubuntu
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose port (Cloud Run defaults to 8080 or reads PORT environment variable)
EXPOSE 8080

# Run FastAPI app using uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]

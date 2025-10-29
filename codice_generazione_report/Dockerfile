FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for WeasyPrint (PDF generation)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libcairo2 \
    libxml2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from analysis service backend directory
COPY codice_generazione_report/backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the analysis service backend code
COPY codice_generazione_report/backend ./backend

# Copy the shared src directory (contains logging_config and api_clients)
COPY src ./src

# Create outputs directory
RUN mkdir -p /app/outputs

# Set PYTHONPATH to include /app so imports work correctly
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose port 8001
EXPOSE 8001

# Run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]

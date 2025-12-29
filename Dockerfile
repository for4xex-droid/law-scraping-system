# Multi-stage build for optimal image size
# 1. Builder Stage (Rust)
FROM rust:1.83-slim-bookworm as builder
WORKDIR /app
COPY backend/ ./backend/
# Build the application in release mode
WORKDIR /app/backend
# Ensure pkg-config and ssl are available
RUN apt-get update && apt-get install -y pkg-config libssl-dev
# Build
RUN cargo build --release

# 2. Runtime Stage (Python + Rust Binary)
FROM python:3.10-slim-bookworm
WORKDIR /app

# Install system dependencies
# libssl is needed for the rust binary to talk to Gemini API (HTTPS)
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Rust binary from builder
# We place it exactly where start_app.py expects it: backend/target/release/backend
COPY --from=builder /app/backend/target/release/backend /app/backend/target/release/backend
# Also copy the data file (index.json) which is in backend/data
COPY backend/data /app/backend/data
# Copy the static data code? No, binary is compiled.
# But start_app.py expects "backend" directory structure for Cwd.

# Copy Python application
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Render sets PORT environment variable. Streamlit needs to listen on this.
# start_app.py is updated to handle this but we should expose 8501 just in case
EXPOSE 8501

# Run the orchestration script
CMD ["python", "start_app.py"]

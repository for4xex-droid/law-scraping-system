# Use a single image that has Python, and we will install Rust.
# This avoids multi-stage complexity and ensures paths line up exactly as they do in local dev.
FROM python:3.10-slim-bookworm

WORKDIR /app

# Install system dependencies
# curl/build-essential for installing Rust
# pkg-config/libssl-dev for building dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy entire project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Build Rust backend
# We build it here so checking "cargo run" in start_app.py will find the binary or just compile fast.
# Actually, let's just pre-build it so start_app.py runs fast.
WORKDIR /app/backend
RUN cargo build --release
WORKDIR /app

# Expose Streamlit port
EXPOSE 8501

# Run the orchestration script using Unbuffered output to see logs
ENV PYTHONUNBUFFERED=1
CMD ["python", "start_app.py"]


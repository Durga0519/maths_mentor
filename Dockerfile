FROM python:3.10-slim

WORKDIR /app

# System dependencies for EasyOCR, OpenCV, Whisper, and audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --upgrade pip

# Install torch CPU first (easyocr depends on it)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install easyocr separately to ensure it works
RUN pip install --no-cache-dir easyocr

# Install openai-whisper
RUN pip install --no-cache-dir openai-whisper

# Install remaining dependencies
RUN pip install --no-cache-dir \
    streamlit>=1.35 \
    langchain>=0.2 \
    langgraph>=0.1 \
    sentence-transformers>=2.7 \
    faiss-cpu>=1.8 \
    sympy>=1.12 \
    python-dotenv>=1.0 \
    pydantic>=2.0 \
    numpy>=1.26 \
    pandas>=2.2 \
    requests>=2.31 \
    scikit-learn>=1.4

# Copy all project files
COPY . .

# Expose Streamlit port (HF Spaces requires 7860)
EXPOSE 7860

ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["streamlit", "run", "app/app.py", "--server.port=7860", "--server.address=0.0.0.0"]
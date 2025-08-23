# Dockerfile multi-stage pour SCALAR Treasury Dashboard
# Image de production optimisée avec Redis

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Installation dépendances système pour compilation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copie requirements et installation
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONPATH=/app/src
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Création utilisateur non-root
RUN useradd --create-home --shell /bin/bash scalar

# Installation dépendances runtime
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie des dépendances Python depuis builder
COPY --from=builder /root/.local /home/scalar/.local

# Copie du code application
WORKDIR /app
COPY --chown=scalar:scalar . .

# Configuration Streamlit
RUN mkdir -p /home/scalar/.streamlit
COPY --chown=scalar:scalar docker/streamlit_config.toml /home/scalar/.streamlit/config.toml

# Switch vers utilisateur non-root
USER scalar

# Ajout du PATH pour les packages utilisateur
ENV PATH=/home/scalar/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Exposition du port Streamlit
EXPOSE 8501

# Point d'entrée
CMD ["streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

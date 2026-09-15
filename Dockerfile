FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt
# Clonamos solo el código de referencia de los agentes, no como librería pesada
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/SakanaAI/Darwin-Godel-Machine.git darwin_core --depth 1
RUN git clone https://github.com/noahshinn/reflexion.git reflexion_core --depth 1
COPY..
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 120

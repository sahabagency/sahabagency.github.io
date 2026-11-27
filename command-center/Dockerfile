FROM python:3.12-slim
WORKDIR /center
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
COPY runtime/requirements.txt runtime/requirements.txt
RUN pip install --no-cache-dir -r runtime/requirements.txt
COPY index.html scheduled-agents.js runtime.js intelligence.js content-factory.js sw.js manifest.webmanifest icon.svg ./
COPY runtime/server.py runtime/media.py runtime/
ENV CENTER_DATA=/data CENTER_HOSTED=1
CMD ["sh","-c","exec uvicorn runtime.server:app --host 0.0.0.0 --port ${PORT:-8000}"]

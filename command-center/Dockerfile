FROM python:3.12-slim
WORKDIR /center
COPY runtime/requirements.txt runtime/requirements.txt
RUN pip install --no-cache-dir -r runtime/requirements.txt
COPY index.html runtime.js sw.js manifest.webmanifest icon.svg ./
COPY runtime/server.py runtime/server.py
ENV CENTER_DATA=/data
CMD ["sh","-c","exec uvicorn runtime.server:app --host 0.0.0.0 --port ${PORT:-8000}"]

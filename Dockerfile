# CSP GPS Complaints – one image for both the dashboard and the twice-daily report.
# Private data is NOT baked in: input/, output/, data/, logs/ and .env are mounted by docker-compose.yml.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Kolkata \
    HOME=/tmp

# tzdata: report times in IST · tesseract: reads text inside screenshots (OCR, optional at run time)
RUN apt-get update \
 && apt-get install -y --no-install-recommends tzdata tesseract-ocr curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p input output data logs && chmod -R a+rwX input output data logs

EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8501/_stcore/health || exit 1

CMD ["python", "-m", "streamlit", "run", "dashboard/app.py", \
     "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", \
     "--browser.gatherUsageStats=false"]

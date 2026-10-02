# Første fase: Installer Python pakker i en separat mappe.
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Anden fase: Kun det nødvendige følger med til det endelige image.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /install /usr/local

# Flask kører som almindelig bruger inde i containeren.
RUN useradd --create-home --uid 10001 appuser
COPY --chown=appuser:appuser app.py x.py ./
COPY --chown=appuser:appuser public ./public
USER appuser
EXPOSE 5000

# Udviklingsserver til lokal skoleopgave; genindlæser Python ved ændringer.
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000", "--debug"]

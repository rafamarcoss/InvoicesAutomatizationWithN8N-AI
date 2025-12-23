FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
	gcc \
	libjpeg-dev \
	zlib1g-dev \
	&& rm -rf /var/lib/apt/lists/* 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5002
CMD ["python", "app.py"]

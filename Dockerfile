FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache build-base wget tar p7zip

COPY install_snap7.sh /app

RUN chmod +x /app/install_snap7.sh

RUN /app/install_snap7.sh

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8082

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082"]

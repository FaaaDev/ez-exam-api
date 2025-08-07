FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x wait-for-it.sh

EXPOSE 8000

CMD ["uvicorn", "app.main_v2:app", "--host", "0.0.0.0", "--port", "8000"]


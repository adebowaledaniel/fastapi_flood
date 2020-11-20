FROM python:3.7-slim-buster
LABEL maintainer="csaybar -- Copernicus Master in Digital Earth (CDE)"

RUN apt-get update && apt-get install -y python3-dev build-essential

RUN mkdir -p /usr/src/

COPY requirements.txt .
COPY ee_token.py .

RUN pip3 install -r requirements.txt
RUN python3 ee_token.py

COPY . .

EXPOSE 5000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5000", "app:app"]
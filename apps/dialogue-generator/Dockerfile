FROM python:3.12

LABEL maintainer="Tib <tib@zuru.com>"

WORKDIR /app

EXPOSE 5400

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5400

CMD ["python", "app.py"]
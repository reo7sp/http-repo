FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FILES_ROOT=/files
VOLUME /files
EXPOSE 8080
CMD ["python", "http_repo/app.py"]
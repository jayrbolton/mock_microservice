FROM python:3.7-alpine

COPY requirements.txt /server/requirements.txt
WORKDIR /server

# Install dependencies
RUN apk --update add make
RUN apk --update add --virtual build-dependencies python-dev build-base && \
    pip install --upgrade pip && \
    pip install --upgrade --no-cache-dir -r requirements.txt && \
    apk del build-dependencies

# Run the app
COPY . /server
CMD ["python", "server.py"]

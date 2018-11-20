FROM python:3.7-alpine

# Install pip dependencies
COPY requirements.txt /server/requirements.txt
WORKDIR /server
RUN apk --update add --virtual build-dependencies python-dev build-base && \
    pip install --upgrade pip && \
    pip install --upgrade --no-cache-dir -r requirements.txt && \
    apk del build-dependencies

# Run the server
COPY . /server
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=development
ENV FLASK_APP=server.py
CMD ["flask", "run", "--host=0.0.0.0"]

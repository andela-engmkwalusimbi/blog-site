FROM python:3-alpine
LABEL Name=blogsite Version=0.0.1
CMD mkdir -p /var/www/src
WORKDIR /var/www/src
COPY . /var/www/src
RUN pip install -r requirements.txt
EXPOSE 8000
FROM python:3.9-alpine
RUN mkdir /duplicati_exporter
RUN apk add --no-cache --virtual .build-deps alpine-sdk linux-headers
COPY ./src /duplicati_exporter
RUN cd /duplicati_exporter && pip install --no-cache-dir -r requirements.txt
RUN apk del .build-deps
EXPOSE 5000
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
CMD cd /duplicati_exporter && python -m flask run

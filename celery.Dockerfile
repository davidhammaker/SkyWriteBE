FROM python:3.9-buster
ENV PYTHONUNBUFFERED=1
ENV DB_ENGINE=django.db.backends.postgresql
RUN useradd celery_user
WORKDIR /code
COPY . .
RUN mkdir /var/log/celery
RUN mkdir /var/log/supervisord
RUN mv supervisord.conf /etc/supervisord.conf
RUN pip install -r requirements.txt
CMD ["supervisord"]

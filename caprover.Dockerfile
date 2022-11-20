# syntax=docker/dockerfile:1
FROM python:3.9-buster
ENV PYTHONUNBUFFERED=1
ENV DB_ENGINE=django.db.backends.postgresql
ARG DB_HOST
COPY ./docker_utils/web /code/utils
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
RUN python manage.py collectstatic --no-input
CMD ["gunicorn", "--env", "DJANGO_SETTINGS_MODULE=sky_write_django.settings", "sky_write_django.wsgi", "--bind", "0.0.0.0:8000", "--workers", "4"]

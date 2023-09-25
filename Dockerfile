FROM node:16
COPY static/ /static/
RUN cd /static && npm ci && cd ..
FROM python:3.9
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=0 /static /app/static
COPY ./ /app
WORKDIR /app
RUN python manage.py collectstatic --noinput
STOPSIGNAL SIGINT
CMD "./entrypoint.sh"
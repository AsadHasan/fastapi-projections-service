FROM nginx/unit:1.23.0-python3.9
COPY config.json /docker-entrypoint.d/config.json
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements/prod.txt

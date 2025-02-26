# init_tables/Dockerfile

FROM bitnami/spark:3.3.2
USER root

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY init_tables.sh /app/init_tables.sh
RUN chmod +x /app/init_tables.sh

CMD ["/app/init_tables.sh"]
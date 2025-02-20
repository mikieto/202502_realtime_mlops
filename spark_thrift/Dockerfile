FROM bitnami/spark:3.5.3

ENV DELTA_VERSION="3.3.0"

USER root
RUN apt-get update && apt-get install -y maven && rm -rf /var/lib/apt/lists/*
RUN useradd -m -d /home/spark -u 1001 -U spark
RUN mkdir -p /home/spark/.ivy2 && chown -R spark:spark /home/spark
RUN mkdir -p /app && chown -R spark:spark /app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER spark
ENV HOME=/home/spark
WORKDIR /app

COPY pom.xml /app/pom.xml
RUN mvn dependency:copy-dependencies -DoutputDirectory=/app/jars
RUN ls -l /app/jars

ENTRYPOINT ["/app/entrypoint.sh"]



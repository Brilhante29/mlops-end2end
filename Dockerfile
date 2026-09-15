FROM apache/airflow:slim-3.3.1-python3.12@sha256:d060a79d6763fa7b47a6ad5e4dc563d402285635c51a6cf2507eb7bfc42d4a49

USER root
RUN apt-get update && apt-get upgrade --yes && rm -rf /var/lib/apt/lists/*
USER airflow

ARG AIRFLOW_VERSION=3.3.1

COPY requirements.txt /tmp/portfolio-requirements.txt
RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    -r /tmp/portfolio-requirements.txt \
    && python -m pip check

WORKDIR /opt/portfolio

COPY pyproject.toml README.md ./
COPY src ./src
COPY dags ./dags
COPY tests ./tests

ENV PYTHONPATH=/opt/portfolio/src \
    PYTHONUNBUFFERED=1 \
    AIRFLOW_HOME=/tmp/mlops-end2end/airflow \
    MLOPS_RUNTIME_DIR=/tmp/mlops-end2end

ENTRYPOINT ["python", "-m", "mlops_end2end.runner"]
CMD ["benchmark"]

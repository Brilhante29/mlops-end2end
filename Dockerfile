FROM apache/airflow:slim-3.3.0-python3.12@sha256:16a6aeb38e865627e3f8e96ab0ef82d5de215153b3d8f9f5878a480136a96582

ARG AIRFLOW_VERSION=3.3.0

COPY requirements.txt /tmp/portfolio-requirements.txt
RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    -r /tmp/portfolio-requirements.txt

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


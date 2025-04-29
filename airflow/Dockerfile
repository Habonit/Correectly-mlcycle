FROM python:3.10-slim AS base
LABEL authors="paradeigma"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AIRFLOW_HOME=/usr/local/airflow
WORKDIR $AIRFLOW_HOME

# 시스템 의존성 설치
RUN apt-get update && \
    apt-get install -y gcc libc-dev vim curl && \
    rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------
# 1단계: requirements 설치용 빌더 이미지
# --------------------------------------------------------
FROM base AS builder

RUN python -m venv .venv
ENV PATH="$AIRFLOW_HOME/.venv/bin:$PATH"

# airflow 내 requirements만 복사
COPY airflow/requirements.txt .

# airflow 관련 의존성 설치
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "import flask_session; print('✅ flask_session import OK')"

# --------------------------------------------------------
# 2단계: 실행 이미지
# --------------------------------------------------------
FROM base AS runner

# 가상환경 복사
COPY --from=builder $AIRFLOW_HOME/.venv .venv
ENV PATH="$AIRFLOW_HOME/.venv/bin:$PATH"

# Airflow 환경에서 사용할 PYTHONPATH 설정
ENV PYTHONPATH=${PROJECT_PATH}

# DAG 및 entrypoint 복사
WORKDIR /usr/local/airflow
COPY airflow/dags/ ./dags/
COPY airflow/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["./entrypoint.sh"]

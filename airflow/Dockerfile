# ===== Base =====
FROM python:3.10-slim AS base
ARG PROJECT_PATH
ARG VENV_PATH
ENV PROJECT_PATH=${PROJECT_PATH}
ENV PYTHONPATH=${PROJECT_PATH}
ENV VENV_PATH=${VENV_PATH}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="${VENV_PATH}/bin:$PATH"

WORKDIR ${PROJECT_PATH}

RUN apt-get update && apt-get install -y \
    gcc libc-dev vim curl openssh-client \
 && rm -rf /var/lib/apt/lists/*

# ===== Builder =====
FROM base AS builder
WORKDIR ${PROJECT_PATH}

RUN python -m venv ${VENV_PATH}
COPY airflow/requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "import flask_session; print('✅ flask_session import OK')"

# ===== Runner =====
FROM base AS runner
WORKDIR ${PROJECT_PATH}

COPY --from=builder ${VENV_PATH} ${VENV_PATH}
COPY airflow/dags/ airflow/dags/
COPY airflow/entrypoint.sh airflow/entrypoint.sh
RUN chmod +x airflow/entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["airflow/entrypoint.sh"]

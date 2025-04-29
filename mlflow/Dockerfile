# === 1단계: 의존성 설치용 빌더 이미지 ===
FROM python:3.10-slim AS builder
LABEL authors="paradeigma"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/mlflow/.venv
WORKDIR /mlflow

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y gcc libc-dev && rm -rf /var/lib/apt/lists/*

# 가상환경 생성
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# mlflow requirements 복사 및 설치
COPY mlflow/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "import mlflow; print('✅ mlflow OK')"

# === 2단계: 실행용 이미지 ===
FROM python:3.10-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/mlflow/.venv
WORKDIR /mlflow

# 가상환경 복사
COPY --from=builder /mlflow/.venv .venv
COPY --from=builder /mlflow/requirements.txt .

ENV PYTHONPATH=${PROJECT_PATH}

ENV PATH="$VENV_PATH/bin:$PATH"

EXPOSE 5000

ENTRYPOINT ["sh", "-c", "mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri \"$MLFLOW_BACKEND_STORE_URI\" --default-artifact-root \"$MLFLOW_DEFAULT_ARTIFACT_ROOT\""]

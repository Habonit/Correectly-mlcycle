#!/bin/bash
# DB 마이그레이션 (중복 방지용 + 안정성 보강)
airflow db upgrade || airflow db migrate

# 관리자 계정 생성 (실패해도 계속 진행)
airflow users create \
    --username "${AIRFLOW_ADMIN_USERNAME:-admin}" \
    --password "${AIRFLOW_ADMIN_PASSWORD:-admin}" \
    --firstname "${AIRFLOW_ADMIN_FIRSTNAME:-Admin}" \
    --lastname "${AIRFLOW_ADMIN_LASTNAME:-User}" \
    --role Admin \
    --email "${AIRFLOW_ADMIN_EMAIL:-admin@example.com}" || true

# 역할에 따라 실행 분기
if [[ "$AIRFLOW_ROLE" == "webserver" ]]; then
    echo "🚀 웹서버 실행 중..."
    exec airflow webserver -p 8080
elif [[ "$AIRFLOW_ROLE" == "scheduler" ]]; then
    echo "🕒 스케줄러 실행 중..."
    exec airflow scheduler
else
    echo "❌ 실행할 역할(AIRFLOW_ROLE)을 지정하세요: webserver 또는 scheduler"
    exit 1
fi

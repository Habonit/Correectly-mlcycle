# Correctly
[![Airflow](https://img.shields.io/badge/Airflow-2.x-blue?logo=apache-airflow)](https://airflow.apache.org/)
[![MLflow](https://img.shields.io/badge/MLflow-2.x-lightgrey?logo=mlflow)](https://mlflow.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)](https://www.docker.com/)

이 레포지토리는 Airflow, MLflow, PostgreSQL을 활용한 실용적인 MLOps 파이프라인 예제를 담고 있습니다. 각 프로젝트에서 필요한 모델을 훈련하고, 데이터 전처리부터 학습, 로깅까지의 과정을 Airflow DAG를 통해 자동화합니다. 모든 구성 요소는 Docker로 컨테이너화되어 재현 가능하게 연결되어 있으며, 경량화된 MLOps 템플릿으로 활용할 수 있습니다.

---

# 실행 방법

```bash
# 1. 레포지토리 클론
git clone https://github.com/Habonit/Correectly-mlcycle.git

# 2. 프로젝트 디렉토리로 이동
cd Correectly-mlcycle

# 3. 환경변수 설정
# openai API 키 포함한 .env 복사
cp .env.example .env

# 4. 도커 컴포즈 실행
docker compose up -d --build

# 5. 샘플 데이터 삽입
docker exec -it airflow bash
python -m src.text_generation.inits
```
---

# 프로젝트 개요
이 프로젝트는 영어 문장을 고쳐주는 챗봇 모델(Correctly)을 훈련시키는 전체 사이클을 자동화하는 데 초점을 맞췄습니다.

사용자로부터 수집된 데이터를 기반으로 자연스러운 교정 문장을 생성하는 모델을 학습하며,

데이터 생성 → 전처리 → 모델 훈련 → 로그 기록까지를 하나의 파이프라인으로 묶었습니다.

전반적인 흐름은 Supervised Fine-tuning(SFT) 중심으로 구성되었습니다.

# 구성 요소 요약
| 구성 요소                     | 설명                                     |
| ------------------------- | -------------------------------------- |
| **Airflow**               | DAG 기반으로 데이터 생성, 테스트, 훈련을 자동화          |
| **MLflow**                | 훈련 중 발생한 로그 및 메트릭 기록용 (로그 시각화 및 비교 지원) |
| **PostgreSQL + pgvector** | 텍스트 데이터 및 벡터 임베딩 저장                    |
| **Train Container**       | 외부 GPU 서버에서 SSH로 학습 스크립트 실행 (예: A100)  |

---
# 주요 기능
## 데이터 생성 자동화
- 엑셀 기반 데이터 → 스키마 매핑된 YAML 포맷 변환

- 프롬프트 예시 데이터 생성 → GPT 테스트 → DB 저장

- PythonOperator로 수행

### 모델 훈련 자동화
- 외부 서버(A100 등)에서 학습 스크립트 실행

- SSHOperator를 활용해 Airflow → GPU 서버로 명령 전송

- 학습은 PyTorch 기반 SFT 방식으로 수행

# 직면한 한계
## 네트워크 연결과 MLflow
MLflow를 사용하려면 외부 GPU 서버에서 MLflow 서버에 접근 가능해야 합니다.

그러나 Docker Compose는 기본적으로 bridge 네트워크를 사용하고, 이는 외부 접근에 부적합합니다.

특히 WSL 환경에서는 포트 포워딩이나 접근 경로 설정이 복잡하여, 로그 연동이 구조적으로 제한되었습니다.

## SSHOperator의 구조적 제약
SSH는 단방향 통신이며 상태 저장이 불가능합니다.

장기 훈련 중 세션이 끊기면 재연결이나 상태 추적이 불가능하여 자동화 신뢰성이 떨어집니다.

KubernetesPodOperator 같은 컨테이너 기반 오퍼레이터가 이상적이지만, 사이드 프로젝트 범위를 넘어서 도입하지 않았습니다.

## 스크립트 우선의 구조 필요
Airflow를 쓰기 위해선 스크립트 단위 모듈화가 선행되어야 합니다.

로직이 꼬여 있거나 의존성이 많을 경우 Airflow 도입은 오히려 역효과입니다.

자동화의 핵심은 Airflow가 아닌 모듈화된 함수와 로직 설계라는 점을 확인했습니다.

# 결론
| 항목           | 요약                                                   |
| ------------ | ---------------------------------------------------- |
| 데이터 자동화    | YAML 기반 구성으로 쉽게 확장 가능                                |
| 훈련 파이프라인   | Airflow + SSHOperator를 통해 자동 트리거 수행                  |
| MLflow 연동 | 외부 네트워크 접근성 문제로 완전한 통합은 어려움                          |
| 훈련 자동화 한계 | Vast.ai와 같은 외부 GPU 환경에서는 반자동화로 설계                    |
| 구조적 교훈    | RDB 대신 MongoDB + VectorDB, Airflow보다는 스크립트 우선 설계가 핵심 |


# 향후 개선 방향
- Kubernetes 기반 오퍼레이터 도입으로 외부 훈련 컨테이너 안정화

- MLflow Tracking 서버를 Public Endpoint로 구성하여 외부 접근 안정화

- MongoDB + Chroma 등 구조적으로 유연한 스토리지 구성 고려

---

# 관련 Velog 포스트

| 제목 | 요약 | 링크 |
|------|------|------|
| Correctly 프로젝트 소개 | 프로젝트 시작 배경, 기술 스택 및 목표 정리 | [링크](https://velog.io/@paradeigma/MLOPS-%EC%8B%A4%EC%8A%B5-2.-Correctly-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-0-%EC%86%8C%EA%B0%9C-%EB%B0%8F-%EA%B8%B0%EC%88%A0-%EC%8A%A4%ED%83%9D) |
| Correctly 중간 점검 | 프로젝트 중간 점검 시 어떤 피드백과 개선이 있었는지 정리 | [링크](https://velog.io/@paradeigma/Correctly-%EC%A4%91%EA%B0%84-%EC%A0%90%EA%B2%80) |
| Airflow Operator 종류 | 다양한 오퍼레이터와 SSHOperator 선택 이유 | [링크](https://velog.io/@paradeigma/Airflow-operator) |
| SSH 통신의 불안정성 | SSHOperator가 갖는 구조적 한계와 실시간 자동화의 부적합성 | [링크](https://velog.io/@paradeigma/ssh-%ED%86%B5%EC%8B%A0%EC%9D%98-%EB%B6%88%EC%95%88%EC%A0%95%EC%84%B1) |
| 컨테이너 안에서 도커 사용 방식 | Docker-in-Docker vs Docker Socket 방식 비교 | [링크](https://velog.io/@paradeigma/%EC%BB%A8%ED%85%8C%EC%9D%B4%EB%84%88-%EC%95%88%EC%97%90%EC%84%9C-%EB%8F%84%EC%BB%A4-%EC%82%AC%EC%9A%A9-2%EA%B0%80%EC%A7%80-%EB%B0%A9%EC%8B%9D) |
| Bridge 네트워크의 한계 | 외부 노드에서 MLflow에 접근하기 어려운 이유와 해결 시도 | [링크](https://velog.io/@paradeigma/MLOPS-%EC%8B%A4%EC%8A%B5-6.-Correctly-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-%EB%82%9C%EA%B4%80-4-Bridge-%EB%84%A4%ED%8A%B8%EC%9B%8C%ED%81%AC%EC%9D%98-%ED%95%9C%EA%B3%84) |

---
# 참고 자료

📄 [Correctly 프로젝트 마무리 발표 자료 (PPTX)](https://github.com/Habonit/Correectly-mlcycle/raw/main/docs/Correctly-프로젝트%20마무리-김경호(MLOPS).pptx)

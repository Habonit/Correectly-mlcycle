from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.providers.ssh.operators.ssh import SSHOperator

from src.utils.logger import setup_logger
from src.utils.load_yaml import load_yaml

from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import subprocess
import os

# 환경 설정
load_dotenv()
log_level = os.getenv("LOG_LEVEL", "DEBUG")
logger = setup_logger(log_level)
project_path = Path(os.getenv('PROJECT_PATH'))

def transfer_data(**kwargs):
    dag_conf = kwargs.get('dag_run').conf if kwargs.get('dag_run') else {}
    id = dag_conf["id"]
    local_ip = dag_conf["local_ip"]
    local_port = dag_conf["local_port"]
    
    remote_key = dag_conf["remote_key"]
    remote_ip = dag_conf["remote_ip"]
    remote_port = dag_conf["remote_port"]
    remote_user = dag_conf["remote_user"]
    remote_workdir = dag_conf["remote_workdir"]
    
    train_data = dag_conf['train_data']
    val_data = dag_conf['val_data']

    train_model = dag_conf['model']
    batch_size = dag_conf['batch_size']
    num_epoch = dag_conf['num_epoch']
    save_total_limit = dag_conf['save_total_limit']
    
    local_dir = f"{project_path}/data/{id}"
    local_train_path = f"{local_dir}/{train_data}"
    local_val_path = f"{local_dir}/{val_data}"
    
    remote_dir = f"{remote_workdir}/data/{id}"
    remote_train_path = f"{remote_dir}/{train_data}"
    remote_val_path = f"{remote_dir}/{val_data}"
    
    logger.info(f"[transfer_data] Creating remote directory: {remote_dir}")
    mkdir_cmd = [
        "ssh", "-p", str(remote_port),
        "-i", str(remote_key),
        f"{remote_user}@{remote_ip}",
        f"mkdir -p {remote_dir}"
    ]
    subprocess.run(mkdir_cmd, check=True)
    
    logger.info(f"[transfer_data] Transferring train file to remote: {remote_train_path}")
    scp_train_cmd = [
        "scp", "-P", str(remote_port), "-i", str(remote_key),
        local_train_path,
        f"{remote_user}@{remote_ip}:{remote_train_path}"
    ]
    subprocess.run(scp_train_cmd, check=True)
    
    logger.info(f"[transfer_data] Transferring val file to remote: {remote_val_path}")
    scp_val_cmd = [
        "scp", "-P", str(remote_port), "-i", str(remote_key),
        local_val_path,
        f"{remote_user}@{remote_ip}:{remote_val_path}"
    ]
    subprocess.run(scp_val_cmd, check=True)

# DAG 정의
with DAG(
    dag_id="correction_script_model_train",
    start_date=datetime(2025, 5, 8),
    schedule_interval=None,
    catchup=False,
    description="1) 데이터 전송 → 2) 모델 훈련",
    tags=["correction_script", "train_table"],
    params={
        "id":"7883",
        "train_data":"train_corpus.json",
        "val_data":"val_corpus.json",
        "local_ip":None,
        "local_port":None,
        "remote_key":"/root/.ssh/id_rsa",
        "remote_ip":"80.188.223.202",
        "remote_port":"13196",
        "remote_user":"root",
        "remote_workdir":"/workspace/Correectly-mlcycle",
        "model":"google/gemma-3-1b-it",
        "batch_size":8,
        "num_epoch":3,
        "save_total_limit":1,
    }
) as dag:

    t1 = PythonOperator(
        task_id="transfer_data",
        python_callable=transfer_data,
        provide_context=True
    )
    # TODO: AIRFLOW로부터 변수를 받아오는 것이 아닌 기본값을 사용하는 구조로 움직입니다.
    # TODO: SSH 방식으로 하는 것은 매우 제한적인 환경에서 해야합니다. 
    # TODO: 폐쇄망 구조에서 dockeroperator로 하는 것이 가장 이상적입니다.    
    ssh_hook = SSHHook(
        remote_host=dag.params["remote_ip"],
        port=int(dag.params["remote_port"]),
        username=dag.params["remote_user"],
        key_file=dag.params["remote_key"],
    )

    t2 = SSHOperator(
        task_id="model_train",
        ssh_hook=ssh_hook,
        command="""
        bash -c '
        export PYTHONPATH={{ params.remote_workdir }} && \
        cd {{ params.remote_workdir }} && \
        nohup /venv/main/bin/python train/train_sft.py \
        --train_json data/{{ params.id }}/{{ params.train_data }} \
        --test_json data/{{ params.id }}/{{ params.val_data }} \
        --report_json data/{{ params.id }}/report.json \
        --model_name "{{ params.model }}" \
        --output_dir data/{{ params.id }}/model \
        --batch_size {{ params.batch_size }} \
        --num_epochs {{ params.num_epoch }} \
        --save_total_limit {{ params.save_total_limit }} \
        > data/{{ params.id }}/train.log 2>&1 &

        echo "✅ Training started in background"
        '
        """,
        do_xcom_push=False,
    )

    t1 >> t2

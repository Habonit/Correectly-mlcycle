from airflow import DAG
from airflow.operators.python import PythonOperator

from src.utils.logger import setup_logger

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
    
def model_train(**kwargs):
    
    logger.info("test 중")

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
        "remote_key":"root/.ssh/id_rsa",
        "remote_ip":"192.165.134.27",
        "remote_port":"12649",
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

    t2 = PythonOperator(
        task_id="model_train",
        python_callable=model_train,
        provide_context=True
    )

    t1 >> t2

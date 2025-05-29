#!/bin/bash

# Exit on error
set -e

# 설정 변수, 이걸 airflow의 변수로 주게 될 것. 
# ID값은 모델 이름과 식별 번호로 붙일 것
# CURRENT_PATH는 학습시킬 곳의 
ID="7883"
TRAIN_WORKSPACE="/workspace/Correectly-mlcycle"
MODEL_NAME="google/gemma-3-1b-it"
BATCH_SIZE=8
NUM_EPOCHS=3
SAVE_TOTAL_LIMIT=2

# 경로
TRAIN_JSON="$TRAIN_WORKSPACE/data/$ID/train_corpus.json"
TEST_JSON="$TRAIN_WORKSPACE/data/$ID/val_corpus.json"
REPORT_JSON="$TRAIN_WORKSPACE/data/$ID/report.json"
OUTPUT_DIR="$TRAIN_WORKSPACE/data/$ID/model"

echo "[INFO] Starting fine-tuning with model: $MODEL_NAME"
echo "[INFO] Training data: $TRAIN_JSON"
echo "[INFO] Test data: $TEST_JSON"
echo "[INFO] Report: $REPORT_JSON"
echo "[INFO] Output directory: $OUTPUT_DIR"
echo "[INFO] CUDA visible devices: $CUDA_VISIBLE_DEVICES"

mkdir -p $OUTPUT_DIR

python train_sft.py \
  --train_json "$TRAIN_JSON" \
  --test_json "$TEST_JSON"   \
  --report_json "$REPORT_JSON" \
  --model_name "$MODEL_NAME" \
  --output_dir "$OUTPUT_DIR" \
  --batch_size "$BATCH_SIZE" \
  --num_epochs "$NUM_EPOCHS" \
  --save_total_limit "$SAVE_TOTAL_LIMIT" | tee "$OUTPUT_DIR/train.log"

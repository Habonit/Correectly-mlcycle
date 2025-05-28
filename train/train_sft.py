import argparse
import json
import torch
import shutil
import sys
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments
)
from trl import SFTTrainer
from loguru import logger
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_json", type=str, required=True)
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--batch_size", type=int, required=True)
    parser.add_argument("--num_epochs", type=int, required=True)
    parser.add_argument("--save_total_limit", type=int, required=True)
    return parser.parse_args()

def load_raw_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def make_sft_data(raw_data):
    result = []
    for item in raw_data:
        instruction = item['instruction']
        input_text = item['input']
        prompt = f"{instruction}\n{input_text}"
        chosen = item['output']
        result.append({'input': prompt, 'target': chosen})
    return result

def preprocess(example):
    input_enc = tokenizer(example["input"], truncation=True, max_length=1536)
    target_enc = tokenizer(example["target"], truncation=True, max_length=1536)
    return {
        "input_ids": input_enc["input_ids"],
        "attention_mask": input_enc["attention_mask"],
        "labels": target_enc["input_ids"]
    }

def main():
    args = parse_args()
    global tokenizer

    logger.info(f"Loading model: {args.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, use_fast=True, token=HF_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(args.model_name, torch_dtype=torch.float16, token=HF_TOKEN).to("cuda")

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.resize_token_embeddings(len(tokenizer))
        logger.info(f"[Tokenizer] pad_token was None. Set to eos_token: {tokenizer.pad_token}")
    else:
        logger.info(f"[Tokenizer] pad_token already set: {tokenizer.pad_token}")

    raw_data = load_raw_data(args.train_json)
    sft_records = make_sft_data(raw_data)
    dataset = Dataset.from_list(sft_records)
    split_dataset = dataset.train_test_split(test_size=0.2, seed=42)

    train_dataset = split_dataset["train"].map(preprocess, remove_columns=["input", "target"])
    eval_dataset = split_dataset["test"].map(preprocess, remove_columns=["input", "target"])

    total_train_steps = len(train_dataset) // args.batch_size * args.num_epochs
    logging_steps = max(1, total_train_steps // (args.num_epochs * 2))
    save_steps = logging_steps

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        num_train_epochs=args.num_epochs,
        bf16=True,
        logging_strategy="steps",
        logging_steps=logging_steps,
        save_strategy="steps",
        save_steps=save_steps,
        eval_strategy="steps",
        eval_steps=logging_steps,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        save_total_limit=args.save_total_limit,
        report_to="none",
        logging_dir=f"{args.output_dir}/logs"
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )

    trainer.train()

    logger.info("Saving model...")
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    
    shutil.make_archive(f"{'/'.join(args.output_dir.split('/')[:-1])}/best_model", 'zip', args.output_dir)

if __name__ == "__main__":
    main()

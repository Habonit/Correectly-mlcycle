#!/bin/bash

echo "[1] Removing stopped containers..."
docker container prune --force

echo "[2] Removing unused images..."
docker image prune -a --force

echo "[3] Removing unused volumes..."
docker volume prune --force

echo "[4] Removing unused networks..."
docker network prune --force

echo "[5] Removing build cache..."
docker builder prune -a --force

echo "[✅] Docker clean-up complete (running containers are untouched)."

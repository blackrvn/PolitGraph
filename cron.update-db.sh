#!/bin/bash

cd ~/politgraph/ || exit 1

LOG=~/politgraph/"$(date '+%Y%m%d-%H%M').log"
{
  echo "$GITHUB_TOKEN" | docker login ghcr.io -u blackrvn --password-stdin
  docker compose build update
  docker compose run --rm update --active --threshold 0.4 --n-neighbors 3
  echo "cronjob ran"
} >> "$LOG" 2>&1
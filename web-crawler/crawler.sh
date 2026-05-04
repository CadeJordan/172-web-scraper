#!/usr/bin/env bash
# Part A web crawler launcher (Unix/Linux/macOS)
# Intended usage (after implementation):
#   ./crawler.sh <seed-File> <num-pages> <hops-away> <output-dir> [optional domain filter args]
# Example:
#   ./crawler.sh data/seed.txt 10000 6 output/html

#!/bin/bash
# Usage: ./crawler.sh <seed_file> <max_pages> <max_depth> <output_dir>
SEED_FILE=${1:-seeds.txt}
MAX_PAGES=${2:-10000}
MAX_DEPTH=${3:-6}
OUTPUT_DIR=${4:-crawled_pages}

scrapy crawl tech_news \
  -a seed_file=$SEED_FILE \
  -a max_pages=$MAX_PAGES \
  -a max_depth=$MAX_DEPTH \
  -s OUTPUT_DIR=$OUTPUT_DIR
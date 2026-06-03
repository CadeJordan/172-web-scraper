#!/usr/bin/env bash

OUTPUT_DIR=${1:-output/html}
INDEX_DIR=${2:-index}

python3 -c "from indexer import build_index; build_index('$OUTPUT_DIR', '$INDEX_DIR')"

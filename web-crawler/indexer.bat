@echo off

set OUTPUT_DIR=%1
set INDEX_DIR=%2

if "%OUTPUT_DIR%"=="" set OUTPUT_DIR=output\html
if "%INDEX_DIR%"=="" set INDEX_DIR=index

python -c "from indexer import build_index; build_index(r'%OUTPUT_DIR%', r'%INDEX_DIR%')"

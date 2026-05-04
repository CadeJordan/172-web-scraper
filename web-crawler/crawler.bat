@echo off
REM Part A web crawler launcher (Windows)
REM Intended usage (after implementation):
REM   crawler.bat ^<seed-File^> ^<num-pages^> ^<hops-away^> ^<output-dir^> [optional domain filter args]
REM Example:
REM   crawler.bat data\seed.txt 10000 6 output\html

scrapy crawl tech_news ^
  -a seed_file=%1 ^
  -a max_pages=%2 ^
  -a max_depth=%3 ^
  -s OUTPUT_DIR=%4
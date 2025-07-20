@echo off
pip install -r requirements.txt
cls
python init_mysql.py
cls
uvicorn main:app --reload
pause
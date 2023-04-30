@echo off

REM activate virtual environment
call ..\env\Scripts\activate.bat

REM delay for 2 seconds
ping 127.0.0.1 -n 2 > nul

REM start Django development server
python manage.py runserver 5000

REM delay for 2 second
ping 127.0.0.1 -n 2 > nul

REM open page in default web browser
start chrome http://127.0.0.1:5000

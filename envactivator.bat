@echo off
echo Activating virtual environment...
call B:\Upwork\DjangoWebserver\.env\Scripts\activate.bat
echo Virtual environment activated.

echo Starting Django server...
cd B:\Upwork\DjangoWebserver\RenukaSoft
python manage.py runserver

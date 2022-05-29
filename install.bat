@echo off

echo Only continue if python is installed and added to path
pause

echo Installing dependencies...
pip install --upgrade -r requirements.txt

echo Running builder...
python builder.py

pause
exit
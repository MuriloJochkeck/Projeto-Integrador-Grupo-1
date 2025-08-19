@echo off
echo Desinstalando dependências...
pip uninstall -y flask psycopg2 hashlib flask_cors werkzeug
echo.
echo Todas as dependências foram desinstaladas!
pause

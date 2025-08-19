@echo off
echo Desinstalando dependências...
pip uninstall -y flask flask_sqlalchemy flask_cors werkzeug
echo.
echo Todas as dependências foram desinstaladas!
pause

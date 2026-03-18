@echo off
chcp 65001 > nul

REM Este script chama o script Python de build e mantem a janela aberta.

python setup_build.py

pause

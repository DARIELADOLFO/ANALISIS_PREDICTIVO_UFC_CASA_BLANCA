@echo off
title Oraculo UFC Freedom 250
color 0C

echo ==================================================
echo   INICIANDO SISTEMA PREDICTIVO UFC - VISION METRICS
echo ==================================================
echo.

:: Cambia al directorio donde tienes tu proyecto
cd /d "C:\Users\darie\Downloads\CIENCIA DE DATOS\ML_UFC"

:: Ejecuta la aplicacion de Streamlit
streamlit run app_ufc.py

pause
@echo off
rem Marque les retraits magasin comme prets dans Shopify des que le bon de
rem livraison est valide dans Odoo. Planifie toutes les 15 minutes
rem (tache "Teatower - Retrait pret Shopify").
rem
rem Le journal est ecrit HORS du depot : il contient des noms de clients et ce
rem depot est public.
setlocal
set DOSSIER=%LOCALAPPDATA%\Teatower
if not exist "%DOSSIER%" mkdir "%DOSSIER%"
set LOG=%DOSSIER%\retrait_pret.log
echo. >> "%LOG%"
echo ---- %DATE% %TIME% >> "%LOG%"
"C:\Program Files\LibreOffice\program\python.exe" "%~dp0shopify_retrait_pret.py" --apply >> "%LOG%" 2>&1

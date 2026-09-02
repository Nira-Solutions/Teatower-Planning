@echo off
REM Import quotidien des visites terrain : Slack #merchandiser -> Odoo.
REM Photos + bon de commande + recap en NOTE INTERNE + tag [VISITE] (pool).
REM Planifie par la tache Windows "Teatower - Visites merchandiser (soir)".
REM Lance via run_hidden.vbs pour ne pas ouvrir de fenetre de console.
cd /d "C:\Users\FlowUP\OneDrive\Teatower"

REM --depuis = aujourd'hui. Le script est idempotent : une visite deja importee
REM n'est pas re-postee (tag [VISITE] deja present sur la fiche).
for /f %%d in ('powershell -NoProfile -Command "(Get-Date).ToString('yyyy-MM-dd')"') do set JOUR=%%d

echo. >> scripts\reports\slack_visites.log
echo ===== %DATE% %TIME% (depuis %JOUR%) ===== >> scripts\reports\slack_visites.log
"C:\Program Files\LibreOffice\program\python.exe" scripts\slack_photos_vers_odoo.py --depuis %JOUR% --apply >> scripts\reports\slack_visites.log 2>&1

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

REM Urgences televente J+1 (REGLES 16) : responsable absent a la visite ->
REM appel de Vanessa le jour ouvre suivant. La page televente est regeneree
REM dans le clone planning (il porte les pools a jour), sur la SEMAINE DEJA
REM PUBLIEE, puis publiee (GitHub Pages).
set LOG=C:\Users\FlowUP\OneDrive\Teatower\scripts\reports\slack_visites.log
cd /d "C:\Users\FlowUP\OneDrive\Teatower-Planning"
git pull -q --rebase --autostash >> "%LOG%" 2>&1
"C:\Program Files\LibreOffice\program\python.exe" scripts\televente_urgences.py >> "%LOG%" 2>&1
"C:\Program Files\LibreOffice\program\python.exe" scripts\build_televente_page.py --semaine-actuelle >> "%LOG%" 2>&1
git add televente\index.html data\televente_urgences.json >> "%LOG%" 2>&1
git commit -q -m "Televente : urgences J+1 responsable absent (auto %JOUR%)" televente\index.html data\televente_urgences.json >> "%LOG%" 2>&1
git push -q >> "%LOG%" 2>&1

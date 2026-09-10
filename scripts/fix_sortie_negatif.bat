@echo off
REM Garde-fou quotidien TT/Sortie : resorbe le stock negatif de la zone de sortie
REM et relance la reservation des livraisons bloquees.
REM Planifie par la tache Windows "Teatower - Garde-fou TT-Sortie" (via run_hidden.vbs).
cd /d "C:\Users\FlowUP\OneDrive\Teatower"
"C:\Program Files\LibreOffice\program\python.exe" scripts\fix_sortie_negatif.py --apply >> scripts\reports\fix_sortie_negatif.log 2>&1

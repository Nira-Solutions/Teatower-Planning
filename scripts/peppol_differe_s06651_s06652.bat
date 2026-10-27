@echo off
REM Envoi Peppol differe INV/2026/05004 (S06651) + INV/2026/05005 (S06652), facturees le 27/10/2026.
REM Tache Windows "Teatower - Peppol differe S06651-S06652" (02/11 18:00, rattrapage 03/11 08:00).
cd /d "C:\Users\FlowUP\OneDrive\Teatower"
"C:\Program Files\LibreOffice\program\python.exe" scripts\peppol_envoi_differe.py INV/2026/05004 INV/2026/05005 --apply >> scripts\reports\peppol_differe.log 2>&1

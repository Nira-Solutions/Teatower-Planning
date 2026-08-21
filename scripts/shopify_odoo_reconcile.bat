@echo off
REM Garde-fou quotidien Shopify -> Odoo : detecte et reimporte les commandes perdues.
REM Planifie par la tache Windows "Teatower - Reconciliation Shopify-Odoo".
cd /d "C:\Users\FlowUP\OneDrive\Teatower"
"C:\Program Files\LibreOffice\program\python.exe" scripts\shopify_odoo_reconcile.py >> scripts\reports\shopify_reconcile.log 2>&1

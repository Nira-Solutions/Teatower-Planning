@echo off
cd /d "%~dp0"
echo ============================================================
echo  Teatower Cockpit Bridge  -  http://127.0.0.1:8765
echo ============================================================

REM --- Odoo (par defaut : creds Teatower deja embarques dans le code) ---
REM set ODOO_URL=https://tea-tree.odoo.com
REM set ODOO_DB=tsc-be-tea-tree-main-18515272
REM set ODOO_USER=nicolas.raes@teatower.com
REM set ODOO_PASSWORD=xxxxxxxx

REM --- Shopify (decommenter + remplir pour activer la vue E-commerce live) ---
REM set SHOPIFY_SHOP=teatower.myshopify.com
REM set SHOPIFY_TOKEN=shpat_xxxxxxxxxxxxxxxx

pip install --quiet fastapi uvicorn pydantic 2>nul
python cockpit_bridge.py
pause

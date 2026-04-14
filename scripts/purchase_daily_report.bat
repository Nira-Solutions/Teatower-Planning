@echo off
cd /d "C:\Users\FlowUP\Downloads\Claude\Claude\Teatower"
python scripts\purchase_daily_report.py >> purchase\cron.log 2>&1

"""Publish catalog.json + QR code into gms-catalog/."""
import json, datetime as dt, pathlib, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT=pathlib.Path(__file__).parent
catalog=json.load(open(ROOT/"_gms_catalog.json",encoding="utf-8"))

# strip image fields, keep slim JSON
slim=[{k:v for k,v in r.items() if k!="image_1920"} for r in catalog]

out={
    "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "source": "Odoo tea-tree.odoo.com — réappro orderpoint GMS ∪ ventes 12m clients GMS/Canal GMS",
    "count": len(slim),
    "products": slim,
}
out_path=ROOT/"gms-catalog"/"catalog.json"
out_path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"wrote {out_path} ({len(slim)} products, {out_path.stat().st_size} bytes)")

# QR code
URL="https://nira-solutions.github.io/Teatower-Planning/gms-catalog/"
try:
    import qrcode
except ImportError:
    print("installing qrcode…")
    subprocess.check_call([sys.executable,"-m","pip","install","qrcode[pil]","-q"])
    import qrcode

qr=qrcode.QRCode(version=None,error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=12,border=2)
qr.add_data(URL); qr.make(fit=True)
img=qr.make_image(fill_color="#2d5a3d",back_color="white").convert("RGB")
qr_path=ROOT/"gms-catalog"/"qr-catalog-gms.png"
img.save(qr_path)
print(f"QR -> {qr_path} (URL: {URL})")

src = open("build_c0196_v3.py", encoding="utf-8").read().split("\n")
head = "\n".join(src[:372])
head = head.replace('LAV = "#8B7BB8"', '''LAV = "#8B7BB8"
import json
CFG = json.load(open(sys.argv[3], encoding="utf-8"))[sys.argv[4]]
FAM = {
    "corail":  ("#EC8475", "#D9624F", "#F6B3A8", "#FFF8F2"),
    "sauge":   ("#C5D3A8", "#6F8752", "#E3EAD2", "#33402A"),
    "rooibos": ("#C24F4C", "#8F2F2E", "#E69A97", "#FFF8F2"),
    "marine":  ("#5A6584", "#3A4362", "#A9B1C7", "#FFF8F2"),
}
CORAL, CORALD, CORALL, WHITE = FAM[CFG["family"]]''', 1)
head = head.replace('"""C0196 Coffret Cacahuète 2026 — version « Panier de grand-maman ».', '"""Coffret 10 sachets (gabarit Giftbox 2026) — générateur commun aux 8 références GMS.\nUsage : gen_box.py <out> <logo.svg> <boxes.json> <clé>', 1)
out = head + open("gen_parts/ingredients.py", encoding="utf-8").read() + open("gen_parts/pages.py", encoding="utf-8").read()
open("gen_box.py", "w", encoding="utf-8").write(out); print("gen_box ok")

"""Analyse Amazon processing summary - classify errors by type and SKU."""
import re
from collections import Counter, defaultdict

src = './data/Teatower_Amazon_FBA_Ready-processing-summary1305261056.txt'

errors_by_code = Counter()
errors_by_type = Counter()
errors_by_sku = defaultdict(list)
sample_msgs = defaultdict(list)
total_lines = 0
header_ok = 0

# Caracteres problematiques mentionnes
bad_chars = Counter()

with open(src, encoding='utf-8') as f:
    for i, line in enumerate(f):
        total_lines += 1
        if i < 5:
            continue
        parts = line.rstrip('\r\n').split('\t')
        if len(parts) < 5:
            continue
        rec, sku, code, etype, msg = parts[0], parts[1], parts[2], parts[3], parts[4]
        if not code:
            continue
        errors_by_code[code] += 1
        errors_by_type[etype] += 1
        errors_by_sku[sku].append((code, etype, msg[:120]))
        if len(sample_msgs[code]) < 3:
            sample_msgs[code].append((sku, msg[:200]))
        # Extract bad byte values
        m = re.search(r"valeur non valide (0x[0-9a-fA-F]+)", msg)
        if m:
            bad_chars[m.group(1)] += 1

print(f"Lignes summary total : {total_lines}")
print(f"\n=== Erreurs par code ===")
for code, n in errors_by_code.most_common():
    print(f"  {code} : {n} occurrences")

print(f"\n=== Erreurs par type ===")
for t, n in errors_by_type.most_common():
    print(f"  {t} : {n}")

print(f"\n=== Octets problematiques ===")
for byte, n in bad_chars.most_common():
    print(f"  {byte} : {n} occurrences")

print(f"\n=== Echantillons par code d'erreur ===")
for code, samples in sample_msgs.items():
    print(f"\n--- Code {code} ---")
    for sku, msg in samples:
        print(f"  SKU={sku!r} : {msg}")

# SKU uniquement avec erreurs fatales (Error vs Attention)
sku_status = {}
for sku, errs in errors_by_sku.items():
    if not sku:
        continue
    types = [e[1] for e in errs]
    if any('Erreur' in t for t in types):
        sku_status[sku] = 'ERROR'
    else:
        sku_status[sku] = 'WARNING_ONLY'

n_error = sum(1 for s in sku_status.values() if s == 'ERROR')
n_warn = sum(1 for s in sku_status.values() if s == 'WARNING_ONLY')
print(f"\nSKU distincts avec erreur : {n_error}")
print(f"SKU distincts avec warnings seuls : {n_warn}")

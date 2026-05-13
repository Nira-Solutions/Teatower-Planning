"""Convert Amazon FBA xlsx template to tab-delimited .txt (UTF-8) for Seller Central upload."""
import openpyxl
import csv

SRC = './data/Teatower_Amazon_FBA_Ready.xlsx'
DST = './data/Teatower_Amazon_FBA_Ready.txt'
SHEET = 'Amazon FBA - FR'

wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
ws = wb[SHEET]

rows_written = 0
non_empty = 0
with open(DST, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(
        f,
        delimiter='\t',
        quoting=csv.QUOTE_MINIMAL,
        lineterminator='\r\n',
    )
    for row in ws.iter_rows(values_only=True):
        cells = []
        for v in row:
            if v is None:
                cells.append('')
            else:
                s = str(v)
                # Amazon tab-delimited: no embedded tabs/newlines in fields
                s = s.replace('\t', ' ').replace('\r', ' ').replace('\n', ' ')
                cells.append(s)
        while cells and cells[-1] == '':
            cells.pop()
        w.writerow(cells)
        rows_written += 1
        if any(c.strip() for c in cells):
            non_empty += 1

print(f'rows_written={rows_written} non_empty_rows={non_empty}')
print(f'output: {DST}')

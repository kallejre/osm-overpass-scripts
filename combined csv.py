import os, csv
files=os.listdir(r"C:\Python\history")
lines=[]
for fn in files:
    with open(r"C:\Python\history\\"+fn, encoding='utf8') as f:
        for ln in f.readlines():
            lines.append(fn[5:-4]+','+ln)
l2=dict()
for l in csv.reader(lines):
    try:
        date,iso,name,rb,wr=l
    except ValueError:
        print("Problem with", l)
    if date not in l2:
        l2[date] = dict()
    if iso not in l2[date]:
        l2[date][iso]=int(rb)
countries = list(sorted(l2[min(l2)]))
with open(r"C:\Python\history.csv",'w', newline='', encoding='utf8') as f:
    f.write('\ufeff')  # Excel utf8 compatibility
    csvf=csv.writer(f, delimiter=";")
    csvf.writerow(['Date']+countries)
    for date in sorted(l2):
        row=[date]
        for country in countries:
            # '' is default value when key is not found
            row.append(l2[date].get(country, ''))
        csvf.writerow(row)

import scraperwiki, urllib2
import lxml 
import re
import requests
import calendar

def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def fetch_record(url):
    f = requests.get(url)
    pdf = scraperwiki.pdftoxml(f.content)
    root = lxml.etree.fromstring(pdf)
    texts = root.xpath("//text") 
    rows = {}
    for text in texts:
        top = int(text.xpath("./@top")[0]) / 10 * 10
        left = int(text.xpath("./@left")[0])
        value = text.text.strip()
        if top not in rows:
            rows[top] = []
        rows[top].append(value)
    rows_sorted = [rows[key] for key in sorted(rows.keys())]
    first_row = rows_sorted[0][0]
    words = first_row.split(" ")
    month = list(calendar.month_name).index(words[-2])
    if month == 0:
        raise Exception("Cannot parse month")
    year = int(words[-1])

    rows_sorted = rows_sorted[1:-1]
    header = [convert(s) for s in rows_sorted[0]]
    num_rows = len(header)
    for i in range(1, len(rows_sorted)):
        row = rows_sorted[i]
        k = num_rows - len(row)
        if k > 0:
            padding = [""] * k
            rows_sorted[i] = padding + rows_sorted[i]
    for i in range(1, len(rows_sorted)):
        if len(rows_sorted[i][0]) == 0:
            rows_sorted[i][0] = rows_sorted[i - 1][0]

        d = {"year": year, "month": month}
        for j in range(0, len(header)):
            d[header[j]] = rows_sorted[i][j]
        scraperwiki.sqlite.save(unique_keys=['year', 'month', 'district'], data=d)
        print d


fetch_record('http://www.edb.gov.hk/attachment/en/student-parents/sch-info/sch-vacancy-situation/primary-sch/Primary_E.pdf')

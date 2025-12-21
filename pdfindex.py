#!/usr/bin/python3
import pymupdf
import regex
import sys

theoremRegexes = [
    '^([A-Z][a-zA-Z\\/]+) ([0-9]+(\\.[0-9]+)*) +(\\([^)]+\\))',
    '^([A-Z][a-zA-Z\\/]+) ([0-9]+(\\.[0-9]+)*) +((\\([^)]+\\)[ .\n])?)',
    '^([A-Z][a-zA-Z\\/]+) ([0-9]+(\\.[0-9]+)*) *',
]
theoremRegexesCompiled = [regex.compile(x) for x in theoremRegexes]

def matchTheoremRegex(x):
    for line in x.split("\n"):
        for tr in theoremRegexesCompiled:
            for match in tr.findall(line):
                yield match

bookmarks = {}

availableKinds = [
  'lemma', 
  'theorem', 
  'satz', 
  'bemerkung', 
  'definition', 
  'beispiel', 
  'korollar', 
  'folgerung', 
  'behauptung', 
  'notation', 
  'remark', 
  'programm', 
  'beispiele', 
  'hilfssatz', 
  'algorithmus', 
  'aufgabe'
]


s = set()
def loadBookmarks(filename):
    fname = filename.split('/')[-1].removesuffix('.pdf')
    doc = pymupdf.open(filename)
    i = 0
    for page in doc.pages():
        i += 1
        text = page.get_text().encode('ascii', 'ignore').decode('ascii')
        for match in matchTheoremRegex(text):
            kind = match[0]
            index = match[1]
            if kind.split('/')[0].lower() not in availableKinds:
                print(f'[{fname}] unknown kind: {kind} ({index})', file=sys.stderr)
                continue
            title = match[3].strip().strip('()').strip().replace('\n', '') if len(match) > 3 else ""
            k = index + kind.lower()
            if k not in s:
                s.add(k)
                yield [index, kind, title, i]
    doc.close()

if len(sys.argv) == 1:
    print(f'usage: {sys.argv[0]} [-mn] <pdf files...>')

availableFlags = 'mn'
flags = ''
for a in sys.argv[1:]:
    if a[0] == '-':
        for f in a[1:]:
            if f not in availableFlags:
                print(f'unknown flag: {f}')
                sys.exit(1)
            flags += f

filenames = filter(lambda x: x[0] != '-', sys.argv[1:])

bs = []
for filename in filenames:
    if filename[0] == '-':
        continue
    fname = filename.split('/')[-1].removesuffix('.pdf')
    n = 0
    page = 0
    i = 0
    for b in loadBookmarks(filename):
        n += 1
        (i, kind, title, page) = b
        bs.append([filename, f'{i}', page])
        if title != "":
            print(f'{i}. [{kind}. {title}]({filename}?p={page})')
        elif 'n' not in flags:
            print(f'{i}. [{kind}.]({filename}?p={page})')

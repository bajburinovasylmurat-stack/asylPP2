import re

def asik(n):
    a = n.split('_')
    return a[0] + ''.join(p.capitalize() for p in a[1:])

with open("/Users/asylmuratbaiburinov/Desktop/pp2_asyl/prac05/raw.txt", "r", encoding="utf-8") as file:
     t = file.read()

n = re.findall(r'\b[a-z]+_[a-z]+\b', t)

for w in n:
    print(asik(w))
import re

with open("/Users/asylmuratbaiburinov/Desktop/pp2_asyl/prac05/raw.txt", "r", encoding="utf-8") as file:
    text = file.read()

m = re.findall("ab{2,3}", text)

for i in m:
    print(i)
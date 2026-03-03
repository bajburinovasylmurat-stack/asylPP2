import re

with open("/Users/asylmuratbaiburinov/Desktop/pp2_asyl/prac05/raw.txt", "r", encoding="utf-8") as file:
    t = file.read()

r = re.sub(r'[ ,.]', ':', t)

print(r)
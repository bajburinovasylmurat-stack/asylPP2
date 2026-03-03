import re

with open("/Users/asylmuratbaiburinov/Desktop/pp2_asyl/prac05/raw.txt", "r", encoding="utf-8") as file:
    t = file.read()

print(re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', t).lower())
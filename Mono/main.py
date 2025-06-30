import re
from pprint import pprint


file_path = 'mono.txt'
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()
jpg_files = re.findall(r'"([^"]+\.jpg)"', content)
print("Topilgan .jpg fayllar:")
for jpg in jpg_files:
    pprint(jpg)

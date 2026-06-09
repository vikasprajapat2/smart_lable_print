import os
for f in ['ui/settings.py', 'ui/dashboard.py']:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace("\\'", "'")

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

with open('init.sql', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("'../images/", "'../assets/images/")
with open('init.sql', 'w', encoding='utf-8') as f:
    f.write(content)
print('init.sql updated')

text=open('scripts/w33_universal_search.py','r',encoding='utf-8').read()
print('count', text.count('"""'))
for i,line in enumerate(text.splitlines(),1):
    if '"""' in line:
        print(i, line)

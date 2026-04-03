import re
c = open('docs/index.html', encoding='utf-8').read()
count = len(re.findall(r'1009', c))
print(f'Found {count} occurrences of 1009')
c = c.replace('1009/1009', '1177/1177')
c = c.replace('1009 checks', '1177 checks')
c = c.replace('1009 verified', '1177 verified')
c = c.replace('1009-row', '1177-row')
c = c.replace('to 1177 verified', 'to 1177 verified')  # already done
c = re.sub(r'>1009<', '>1177<', c)
# Also handle the "All ... 1009" with HTML tags
c = re.sub(r'1009\b', '1177', c)
open('docs/index.html', 'w', encoding='utf-8').write(c)
count2 = len(re.findall(r'1009', c))
print(f'Remaining: {count2}')

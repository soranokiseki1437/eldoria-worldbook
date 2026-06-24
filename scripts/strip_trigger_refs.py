import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# Pattern: remove all N## or N##.# 已触发/已完成 references from trigger conditions
# Match: , N##已触发  or  , N##.#已触发  or  N##已触发  etc.
patterns = [
    (r',?\s*N\d{2}[.\d]*已触发\s*', ''),   # , N26已触发
    (r',?\s*N\d{2}[.\d]*已完成\s*', ''),    # , N26已完成
    (r',?\s*N\d{2}[.\d]*已(?!触|完成)', ''), # , N26已... (other)
]

count = 0
for pat, repl in patterns:
    matches = len(re.findall(pat, c))
    c = re.sub(pat, repl, c)
    count += matches

# Clean up double commas or trailing commas before line breaks
c = re.sub(r',\s*,', ',', c)
c = re.sub(r',\s*\n', '\n', c)

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','w',encoding='utf-8') as f:
    f.write(c)

print(f'Removed {count} event-number trigger references')
print('All N##已触发 patterns stripped from trigger conditions.')

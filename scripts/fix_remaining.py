import re

with open('C:/Users/lx/Desktop/世界书/docs/05_事件系统.md','r',encoding='utf-8') as f:
    c = f.read()

# === Fix N12: Find exact text ===
idx = c.find('### 事件N12：丝袜与内衣')
end = c.find('```', c.find('情境:', idx))
chunk = c[idx:end]

print('=== N12 chunk ===')
for i, line in enumerate(chunk.split('\n')):
    if any(w in line for w in ['低语者', '可控', 'N10', 'N11', '失控', '凯尔', '商量']):
        print(f'  L{i}: {line.strip()[:120]}')

# === Fix N19: Find exact text ===
idx = c.find('### 事件N19：乔治的回礼')
end = c.find('```', c.find('情境:', idx))
chunk = c[idx:end]

print('\n=== N19 chunk ===')
for i, line in enumerate(chunk.split('\n')):
    if any(w in line for w in ['N15', 'N16', '乔治', '躲', '邀请', '设计', '按摩']):
        print(f'  L{i}: {line.strip()[:120]}')

# === Find N26 end pattern ===
print('\n=== N26/N27 boundaries ===')
n26 = c.find('### 事件N26：桌下之口')
n27 = c.find('### 事件N27：', n26+10)
print(f'N26 at {n26}, N27 at {n27}')
if n26 != -1 and n27 != -1:
    between = c[n26:n27]
    print(f'Between: {between[-100:]}')

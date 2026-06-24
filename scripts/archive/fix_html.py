import json

# 读取现有HTML
with open(r'C:\Users\lx\Desktop\世界书\visual\剧情时间线可视化.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 找到script标签的位置
script_pos = html.find('<script src="event_data.js"></script>')
if script_pos == -1:
    print('ERROR: Could not find script tag')
    exit(1)

# 在script标签后面插入app.js引用
insert_pos = script_pos + len('<script src="event_data.js"></script>')

# 构建新的HTML
new_html = html[:insert_pos] + '\n<script src="app.js"></script>' + html[insert_pos:]

# 写入
with open(r'C:\Users\lx\Desktop\世界书\visual\剧情时间线可视化.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print('Updated HTML to include app.js')

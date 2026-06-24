import os

# 读取现有HTML
with open(r'C:\Users\lx\Desktop\世界书\visual\剧情时间线可视化.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 找到<script>的位置（内联script开始）
script_pos = html.find('<script>')
if script_pos == -1:
    print('ERROR: Could not find inline script tag')
    exit(1)

# 删除从内联<script>到文件末尾的所有内容
new_html = html[:script_pos]

# 添加结束标签
new_html += '</body>\n</html>'

# 写入
with open(r'C:\Users\lx\Desktop\世界书\visual\剧情时间线可视化.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print('Fixed HTML structure')
print(f'File size: {len(new_html)} bytes')

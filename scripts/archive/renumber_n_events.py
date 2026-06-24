#!/usr/bin/env python3
"""Renumber N-series events in 05_事件系统.md to sequential N1-N58 order.
Uses temporary placeholder to avoid old→new number conflicts."""
import re

# Old → New mapping (only for events that change number)
RENUMBER = {
    30: 5, 31: 6, 59: 7, 46: 8, 49: 9,
    5: 10, 6: 11, 32: 12, 60: 13, 33: 14, 34: 15, 35: 16, 36: 17,
    19: 18, 21: 19, 22: 20, 51: 21, 52: 22,
    7: 23, 8: 24, 23: 25, 24: 26, 25: 27, 37: 28, 38: 29, 20: 30,
    11: 31, 12: 32, 15: 33, 53: 34, 54: 35, 55: 36, 56: 37,
    9: 38, 13: 39, 14: 40, 26: 41, 27: 42, 47: 43, 57: 44, 58: 45,
    28: 46, 29: 47, 62: 49, 63: 50, 64: 51, 65: 52, 66: 53, 67: 54,
    10: 55, 16: 56,
    17: 57, 18: 58,
}
# N1, N2, N3, N4, N48 stay unchanged

TARGET = r'C:\Users\lx\Desktop\世界书\docs\05_事件系统.md'

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# Phase 1: Replace old N-numbers with unique placeholder
# Use format: N_OLD_{num}_TO_NEW_{newnum}_
for old_num, new_num in sorted(RENUMBER.items(), reverse=True):
    placeholder = f'N___{old_num}___{new_num}___'
    # Match N followed by exact old number, not part of a larger number
    # Exclude other event prefixes: PN, EN, WN, GN, HN, RN, CN, SN
    # (?<![0-9A-Z]) means: not preceded by digit or uppercase letter (catches P in PN)
    pattern = rf'(?<![0-9A-Z])N{old_num}(?![0-9])'
    content = re.sub(pattern, placeholder, content)

# Phase 2: Replace all placeholders with final new numbers
for old_num, new_num in RENUMBER.items():
    placeholder = f'N___{old_num}___{new_num}___'
    content = content.replace(placeholder, f'N{new_num}')

# Write back
with open(TARGET, 'w', encoding='utf-8') as f:
    f.write(content)

print("Renumbering complete.")

# Verify
with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

found_headers = set()
for m in re.finditer(r'### 事件N(\d+)：', content):
    found_headers.add(int(m.group(1)))
print(f"  Found {len(found_headers)} N-event headers")
print(f"  Numbers: {sorted(found_headers)}")

# Check for any leftover placeholders
placeholders_left = re.findall(r'N___\d+___\d+___', content)
if placeholders_left:
    print(f"  WARNING: {len(placeholders_left)} placeholders remaining!")
else:
    print(f"  No leftover placeholders.")

# Check for old S-prefix events
s_headers = re.findall(r'### 事件S\d+', content)
if s_headers:
    print(f"  WARNING: {len(s_headers)} S-prefix headers found!")
else:
    print(f"  No S-prefix headers remaining.")

print("\nDone.")

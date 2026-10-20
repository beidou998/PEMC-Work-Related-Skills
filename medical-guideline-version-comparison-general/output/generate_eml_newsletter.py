"""
邮件版报告生成器 v3 - 智能切割 + Newsletter 宽版
将专门设计的邮件版 HTML 截图 → 智能切割（避开文字行）→ 打包为 EML

用法: python generate_eml_newsletter.py [邮件版HTML] [输出EML]
默认: NCCN_前列腺癌指南对比报告_V5vsV6_2026_邮件版.html

依赖: pip install Pillow numpy
"""
import os, sys, re, subprocess, math
import numpy as np
from PIL import Image
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ============ CONFIG ============
WIDTH = 800            # 邮件正文显示宽度(px) — 宽版 newsletter
DEVICE_SCALE = 2       # 2x 高清截图(实际1600px宽, 显示800px)
TARGET_SLICE_H = 2400  # 目标切片高度(2x像素)，实际切点会在此附近找空白行
SEARCH_RANGE = 400     # 在目标切点上下搜索空白行的范围(px)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
# ================================

# Input
html_file = sys.argv[1] if len(sys.argv) > 1 else 'NCCN_前列腺癌指南对比报告_V5vsV6_2026_邮件版.html'
eml_file = sys.argv[2] if len(sys.argv) > 2 else html_file.replace('.html', '.eml').replace('_邮件版', '_newsletter')

if not os.path.exists(html_file):
    print(f"ERROR: {html_file} not found")
    sys.exit(1)

print(f'📧 Newsletter EML 生成器 v3（智能切割）')
print(f'   源文件: {html_file}')
print(f'   宽度: {WIDTH}px (高清{DEVICE_SCALE}x)')
print()

# ---- Step 1: Edge headless 截全页 ----
print('[1/4] Edge headless 截图...')

# Read HTML and inject width constraint
with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

# Force container width for screenshot
html = html.replace(
    '<body>',
    f'<body style="width:{WIDTH}px; margin:0 auto; overflow:hidden; height:auto;">'
)
# Ensure .container matches width
html = re.sub(r'width:\s*800px', f'width:{WIDTH}px', html)

temp_html = '_screenshot_temp.html'
with open(temp_html, 'w', encoding='utf-8') as f:
    f.write(html)

abs_path = os.path.abspath(temp_html).replace('\\', '/')
url = f'file:///{abs_path}'
screenshot_path = '_full_page.png'

cmd = [
    EDGE, '--headless', '--disable-gpu', '--hide-scrollbars',
    f'--window-size={WIDTH},10000',  # 10000px 高窗口
    f'--force-device-scale-factor={DEVICE_SCALE}',
    f'--screenshot={os.path.abspath(screenshot_path)}',
    url
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

if not os.path.exists(screenshot_path):
    print(f"ERROR: 截图失败. stderr: {result.stderr[:300]}")
    sys.exit(1)

# ---- Step 2: 裁剪空白 + 智能切割 ----
print('[2/4] 智能切割...')
img = Image.open(screenshot_path)
full_w, full_h = img.size
print(f'  原始: {full_w}x{full_h}px')

arr = np.array(img)

# Trim bottom whitespace
bg_threshold = 245
row_has_content = np.any(arr[:, :, :3] < bg_threshold, axis=(1, 2))
last_row = full_h - 1
for r in range(full_h - 1, -1, -1):
    if row_has_content[r]:
        last_row = r
        break
content_h = min(last_row + 40, full_h)
print(f'  内容高度: {content_h}px (去除{full_h - content_h}px空白)')

img = img.crop((0, 0, full_w, content_h))
arr = arr[:content_h, :, :]

# Smart slicing: find "safe" cut rows (rows where all pixels are background-like)
# A "safe row" is one where the row is nearly uniform (background color)
def is_safe_row(row_idx):
    """Check if a row is safe to cut at (background/spacer area)"""
    if row_idx >= content_h:
        return False
    row = arr[row_idx, :, :3]
    # Row is safe if variance is very low (uniform color) and color is light
    mean_val = np.mean(row)
    std_val = np.std(row)
    return mean_val > 230 and std_val < 15

def find_safe_cut(target_y):
    """Find nearest safe cut point around target_y"""
    # Search in expanding circles from target
    for offset in range(0, SEARCH_RANGE):
        # Try below target first (prefer cutting lower)
        if target_y + offset < content_h and is_safe_row(target_y + offset):
            # Verify it's a multi-row safe zone (not just one pixel line)
            safe_count = sum(1 for dy in range(5) if is_safe_row(target_y + offset + dy))
            if safe_count >= 3:
                return target_y + offset
        # Try above target
        if target_y - offset > 0 and is_safe_row(target_y - offset):
            safe_count = sum(1 for dy in range(5) if is_safe_row(target_y - offset + dy))
            if safe_count >= 3:
                return target_y - offset
    # Fallback: cut at target anyway
    print(f'  ⚠️ 未找到安全切点 (y≈{target_y})，使用固定切割')
    return target_y

# Calculate cut points
n_target = math.ceil(content_h / TARGET_SLICE_H)
cut_points = [0]
for i in range(1, n_target):
    target_y = i * TARGET_SLICE_H
    if target_y >= content_h:
        break
    safe_y = find_safe_cut(target_y)
    cut_points.append(safe_y)
cut_points.append(content_h)

# Generate slices
slices = []
total_kb = 0
for i in range(len(cut_points) - 1):
    top = cut_points[i]
    bottom = cut_points[i + 1]
    if bottom - top < 50:  # skip tiny slices
        continue
    crop = img.crop((0, top, full_w, bottom))
    path = f'_slice_{i+1:02d}.png'
    crop.save(path, 'PNG', optimize=True)
    slices.append(path)
    sz = os.path.getsize(path) / 1024
    total_kb += sz
    print(f'  切片 {len(slices)}: y={top}-{bottom} (h={bottom-top}px, {sz:.0f}KB)')

img.close()
print(f'  合计: {len(slices)} 张, {total_kb:.0f}KB')

# ---- Step 3: 打包 EML ----
print(f'[3/4] 打包 EML...')

img_tags = []
for i, s in enumerate(slices):
    cid = f'slice{i+1:02d}'
    img_tags.append(
        f'<img src="cid:{cid}" width="{WIDTH}" '
        f'style="display:block;margin:0 auto;border:0;padding:0;" alt="">'
    )

email_body = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background-color:#f0f2f5;">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td align="center" style="padding:20px 0;">
<table width="{WIDTH}" cellpadding="0" cellspacing="0" border="0">
<tr><td style="font-size:0;line-height:0;padding:0;">
{''.join(img_tags)}
</td></tr></table>
</td></tr></table>
</body></html>'''

msg = MIMEMultipart('related')
msg['Subject'] = Header('NCCN前列腺癌指南对比报告 Version 5.2026 vs Version 6.2026', 'utf-8')
msg['X-Unsent'] = '1'
msg.attach(MIMEText(email_body, 'html', 'utf-8'))

for i, s in enumerate(slices):
    with open(s, 'rb') as f:
        data = f.read()
    mime_img = MIMEImage(data, _subtype='png')
    cid = f'slice{i+1:02d}'
    mime_img.add_header('Content-ID', f'<{cid}>')
    mime_img.add_header('Content-Disposition', 'inline', filename=f'{cid}.png')
    msg.attach(mime_img)

with open(eml_file, 'wb') as f:
    f.write(msg.as_bytes())

eml_kb = os.path.getsize(eml_file) / 1024

# ---- Step 4: Cleanup ----
print('[4/4] 清理临时文件...')
os.remove(temp_html)
os.remove(screenshot_path)
for s in slices:
    os.remove(s)

print()
print(f'✅ 完成!')
print(f'   输出: {eml_file} ({eml_kb:.0f}KB)')
print(f'   切图: {len(slices)} 张, 显示宽度 {WIDTH}px, 高清 {DEVICE_SCALE}x')
print(f'   智能切割: 在段落间隙处切割，避免切断文字')
print(f'   使用: 双击 .eml → Outlook 草稿 → 填收件人发送')

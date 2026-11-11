filepath = r"c:\Users\DEEPAK NG\OneDrive\Desktop\vegetable-quality-detection\frontend\dashboard.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    '<strong>${p.quality}</strong> &mdash; <span style="color:var(--muted);font-size:0.8rem;">',
    '<strong style="color:${qColor(p.quality)};font-weight:700;">${p.quality}</strong> &mdash; <span style="color:var(--muted);font-size:0.8rem;">'
)
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("dashboard.html quality colored")




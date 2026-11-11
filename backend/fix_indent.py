with open(r"c:\Users\DEEPAK NG\OneDrive\Desktop\vegetable-quality-detection\backend\app\services\prediction_service.py", "r") as f:
    lines = f.readlines()

# Fix line 209 (0-indexed: 208) - should have 4 spaces, not 8
# The _analyze_predict def line
for i, line in enumerate(lines):
    if "_analyze_predict(self, image_path" in line:
        lines[i] = "    def _analyze_predict(self, image_path: str) -> Dict[str, object]:\n"
        print(f"Fixed line {i+1}: {repr(lines[i])}")
        break

with open(r"c:\Users\DEEPAK NG\OneDrive\Desktop\vegetable-quality-detection\backend\app\services\prediction_service.py", "w") as f:
    f.writelines(lines)
print("File saved.")

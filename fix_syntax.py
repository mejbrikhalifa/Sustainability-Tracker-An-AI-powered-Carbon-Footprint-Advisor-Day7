#!/usr/bin/env python3
"""Fix the syntax error in app.py at line 1376"""

with open(r"c:\Disc D\Zied Guizani\Windsurf3\app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Fix line 1376 (index 1375) - replace the corrupted line
if 1375 < len(lines):
    # The line currently has: "                        try:`n                            if not df_ok_ci.empty:"
    # We need to split it into two proper lines
    lines[1375] = "                        try:\n"
    lines.insert(1376, "                            if not df_ok_ci.empty:\n")

# Write back
with open(r"c:\Disc D\Zied Guizani\Windsurf3\app.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Fixed syntax error at line 1376")

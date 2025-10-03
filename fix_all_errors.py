#!/usr/bin/env python3
"""Fix syntax errors in app.py"""

import re

with open(r"c:\Disc D\Zied Guizani\Windsurf3\app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Replace st.popander with st.popover (line ~479)
content = content.replace("st.popander(", "st.popover(")
print("✓ Fixed: st.popander → st.popover")

# Fix 2: Fix the corrupted line 1376 that has try:`n instead of try:\n
# The pattern looks like: "try:`n                            if not df_ok_ci.empty:"
content = content.replace("try:`n                            if not df_ok_ci.empty:", 
                         "try:\n                            if not df_ok_ci.empty:")
print("✓ Fixed: corrupted try statement at line 1376")

# Write back
with open(r"c:\Disc D\Zied Guizani\Windsurf3\app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ All fixes applied successfully!")

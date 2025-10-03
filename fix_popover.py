#!/usr/bin/env python3
"""Replace invalid st.popander with a version-safe fallback (popover if available, else expander)."""
from pathlib import Path

p = Path(r"c:\Disc D\Zied Guizani\Windsurf3\app.py")
text = p.read_text(encoding="utf-8")

needle = "with st.popander(\"Help\"):"  # current buggy line

if needle in text:
    replacement = (
        "# Help popover/expander with a short FAQ\n"
        "HelpContainer = st.popover if hasattr(st, \"popover\") else st.expander\n"
        "with HelpContainer(\"Help\"):\n"
    )
    lines = text.splitlines(keepends=True)
    out = []
    for line in lines:
        if line.strip().startswith("with st.popander(\"Help\"):"):
            indent = line[:len(line) - len(line.lstrip())]
            repl = "".join(indent + l for l in replacement.splitlines(True))
            out.append(repl)
        else:
            out.append(line)
    p.write_text("".join(out), encoding="utf-8")
    print("Replaced st.popander with version-safe HelpContainer block.")
else:
    print("No st.popander usage found.")

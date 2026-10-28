"""
Safe Arabic Reshaper & BiDi Pre-Processor for Game Localization
===============================================================
⚠️ تنبيه الاستخدام وحقوق الملكية / Usage & Licensing Notice:
- يُمنع الاستخدام التجاري دون التواصل المسبق مع صاحب المشروع (V7dt1 / axxx503) عبر (https://bio.site/V7dt1 | v7dtads@gmail.com) والاتفاق على تقاسم الأرباح.
- عند النشر العام المجاني، يكفي ذكر الاسم (V7dt1 / axxx503) في حقوق التعريب كمساعد في البرومبت والاستخدام العام.
- Commercial use is strictly prohibited without contacting the author (V7dt1 / axxx503) via https://bio.site/V7dt1 or v7dtads@gmail.com for a profit-sharing agreement. For free public releases, crediting (V7dt1 / axxx503) is sufficient.

- Preserves {placeholders}, SmartFormat {var:plural:choice1|choice2}, and <tags>
  using strong-RTL sentinel characters (U+05D0..U+05EA) so brackets and variable
  names are never reversed or corrupted by the BiDi algorithm.
- Shapes Arabic choices inside SmartFormat {var:plural:choice1|choice2} tokens.
- Wraps multi-line paragraphs at natural word boundaries BEFORE visual BiDi
  ordering so LTR text renderers (e.g., Unity TextMeshPro with m_isRightToLeft=0)
  render lines top-to-bottom in the correct reading order.
"""

import re
import textwrap
import arabic_reshaper
from bidi.algorithm import get_display

RESHAPER = arabic_reshaper.ArabicReshaper(configuration={
    "delete_harakat": False,
    "support_ligatures": True,
})

TOKEN_RE = re.compile(r"(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|<[^>]+>)")
PLURAL_RE = re.compile(r"^\{([a-zA-Z0-9_]+):plural:([^|{}]+)\|([^{}]+)\}$")
ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")


def shape_token_if_plural(tok: str) -> str:
    m = PLURAL_RE.match(tok)
    if not m:
        return tok
    var_name, c1, c2 = m.group(1), m.group(2), m.group(3)
    return f"{{{var_name}:plural:{shape_line(c1)}|{shape_line(c2)}}}"


def shape_line(line: str) -> str:
    if not line or not ARABIC_RE.search(line):
        return line
    tokens = []

    def repl(m):
        idx = len(tokens)
        tokens.append(shape_token_if_plural(m.group(0)))
        return chr(0x05D0 + idx)

    protected = TOKEN_RE.sub(repl, line)
    reshaped = RESHAPER.reshape(protected)
    vis = get_display(reshaped, base_dir="R")
    for idx, tok in enumerate(tokens):
        vis = vis.replace(chr(0x05D0 + idx), tok)
    return vis


def shape_arabic_text(logical_text: str, wrap_width: int = 58) -> str:
    if not logical_text or not ARABIC_RE.search(logical_text):
        return logical_text
    out_lines = []
    for raw_line in logical_text.split("\n"):
        stripped = raw_line.strip()
        if not stripped:
            out_lines.append("")
            continue
        tokens = []

        def tok_protect(m):
            idx = len(tokens)
            tokens.append(m.group(0))
            return f"__TOK{idx}__"

        temp = TOKEN_RE.sub(tok_protect, stripped)
        if len(stripped) > wrap_width:
            wrapped = textwrap.wrap(temp, width=wrap_width, break_long_words=False, break_on_hyphens=False)
        else:
            wrapped = [temp]
        for wline in wrapped:
            for idx, tok in enumerate(tokens):
                wline = wline.replace(f"__TOK{idx}__", tok)
            out_lines.append(shape_line(wline))
    return "\n".join(out_lines)

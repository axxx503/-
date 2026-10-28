"""
Arabic Font Merger & FreeType Validator for Game Localization
=============================================================
⚠️ تنبيه الاستخدام وحقوق الملكية / Usage & Licensing Notice:
- يُمنع الاستخدام التجاري دون التواصل المسبق مع صاحب المشروع (V7dt1 / axxx503) عبر (https://bio.site/V7dt1 | v7dtads@gmail.com) والاتفاق على تقاسم الأرباح.
- عند النشر العام المجاني، يكفي ذكر الاسم (V7dt1 / axxx503) في حقوق التعريب كمساعد في البرومبت والاستخدام العام.
- Commercial use is strictly prohibited without contacting the author (V7dt1 / axxx503) via https://bio.site/V7dt1 or v7dtads@gmail.com for a profit-sharing agreement. For free public releases, crediting (V7dt1 / axxx503) is sufficient.

Merges an OFL-licensed Arabic TrueType font (such as Tajawal) into a game's
existing Latin TrueType font(s) while:
1. Mapping all 36 isolated Arabic Presentation Forms-B codepoints (U+FE80..U+FEF1)
   to their corresponding base glyphs (U+0621..U+064A) so arabic_reshaper output
   never produces missing-glyph boxes.
2. Scaling Arabic glyph outlines and horizontal metrics (hmtx) proportionally to
   match the target font's unitsPerEm (UPM).
3. Verifying 100% glyph presence with FreeType (the exact rasterizer used by
   Unity TextMeshPro / TextCore, Godot, and Unreal Slate).
"""

import io
import freetype
import arabic_reshaper
from arabic_reshaper.letters import LETTERS_ARABIC, ISOLATED
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen


def merge_arabic_into_ttf(base_ttf_bytes: bytes, arabic_ttf_path: str, scale_factor: float = 1.15) -> bytes:
    base_tt = TTFont(io.BytesIO(base_ttf_bytes))
    ar_tt = TTFont(arabic_ttf_path)

    base_upm = base_tt["head"].unitsPerEm
    ar_upm = ar_tt["head"].unitsPerEm
    scale = (base_upm / float(ar_upm)) * scale_factor

    ar_cmap = dict(ar_tt.getBestCmap())
    # Ensure all isolated presentation forms in LETTERS_ARABIC map to their base isolated glyph
    for base_ch, forms in LETTERS_ARABIC.items():
        base_cp = ord(base_ch)
        if base_cp in ar_cmap:
            isol_str = forms[ISOLATED]
            if isol_str:
                isol_cp = ord(isol_str)
                if isol_cp not in ar_cmap:
                    ar_cmap[isol_cp] = ar_cmap[base_cp]

    target_cps = {}
    for cp, gname in ar_cmap.items():
        if (
            (0x0600 <= cp <= 0x06FF)
            or (0x0750 <= cp <= 0x077F)
            or (0x08A0 <= cp <= 0x08FF)
            or (0xFB50 <= cp <= 0xFDFF)
            or (0xFE70 <= cp <= 0xFEFF)
        ):
            target_cps[cp] = gname

    ar_glyph_set = ar_tt.getGlyphSet()
    base_glyf = base_tt["glyf"]
    base_hmtx = base_tt["hmtx"].metrics
    base_glyph_order = list(base_tt.getGlyphOrder())
    base_glyph_set_names = set(base_glyph_order)

    ar_to_base_gname = {}
    for cp, ar_gname in sorted(target_cps.items()):
        if ar_gname not in ar_to_base_gname:
            new_gname = f"ar_{ar_gname}"
            while new_gname in base_glyph_set_names:
                new_gname += "_"
            pen = TTGlyphPen(None)
            tpen = TransformPen(pen, (scale, 0, 0, scale, 0, 0))
            ar_glyph_set[ar_gname].draw(tpen)
            new_glyph = pen.glyph()
            new_glyph.recalcBounds(base_glyf)

            base_glyf[new_gname] = new_glyph
            ar_adv, ar_lsb = ar_tt["hmtx"].metrics[ar_gname]
            new_adv = int(round(ar_adv * scale))
            new_lsb = int(round(ar_lsb * scale))
            if hasattr(new_glyph, "xMin"):
                new_lsb = new_glyph.xMin
            base_hmtx[new_gname] = (new_adv, new_lsb)
            base_glyph_order.append(new_gname)
            base_glyph_set_names.add(new_gname)
            ar_to_base_gname[ar_gname] = new_gname

    base_tt.setGlyphOrder(base_glyph_order)
    base_tt["maxp"].numGlyphs = len(base_glyph_order)

    for table in base_tt["cmap"].tables:
        if table.isUnicode():
            for cp, ar_gname in target_cps.items():
                if table.format == 4 and cp > 0xFFFF:
                    continue
                table.cmap[cp] = ar_to_base_gname[ar_gname]

    out_buf = io.BytesIO()
    base_tt.save(out_buf)
    return out_buf.getvalue()


def verify_merged_font_with_freetype(ttf_bytes: bytes) -> list:
    """Returns a list of missing (codepoint, hex_str) across all Arabic contextual forms."""
    letters = [chr(cp) for cp in range(0x0621, 0x063B)] + [chr(cp) for cp in range(0x0640, 0x064B)]
    beh = "\u0628"
    lam = "\u0644"
    test_words = []
    for ch in letters:
        test_words.append(ch)
        test_words.append(ch + beh + ch + beh + ch)
    for alef in ["\u0627", "\u0623", "\u0625", "\u0622"]:
        test_words.append(lam + alef)
        test_words.append(beh + lam + alef)
    test_words.extend(["\u060c", "\u061b", "\u061f", "\u066a", "ABC", "123", "$100%"])
    reshaped_test = arabic_reshaper.reshape(" ".join(test_words))

    face = freetype.Face(io.BytesIO(ttf_bytes))
    face.set_char_size(48 * 64)
    missing = []
    for ch in set(reshaped_test):
        if ch == " ":
            continue
        gidx = face.get_char_index(ord(ch))
        if gidx == 0:
            missing.append((ord(ch), hex(ord(ch))))
        else:
            face.load_glyph(gidx, freetype.FT_LOAD_RENDER)
    return missing

---
name: arabic-game-localization
description: Autonomous end-to-end Arabic game localization skill for Google Antigravity IDE. Discovers game engines (Unity, Unreal, Godot, GameMaker, Ren'Py, custom), backs up originals with SHA-256 verification, merges OFL Arabic fonts with full isolated/connected Presentation Forms-B coverage, shapes RTL/BiDi Arabic while protecting {placeholders} and <tags>, translates full inventories in context, localizes in-game graphical posters, and builds reversible lightweight install/uninstall packages.
---

# Arabic Game Localization Skill (`arabic-game-localization`)

> **⚠️ تنبيه الاستخدام وحقوق الملكية (Usage & Licensing Notice)**:
> - **يُمنع الاستخدام التجاري** لهذا الإطار أو المهارة أو البرومبت دون التواصل المسبق مع صاحب المشروع (`V7dt1` / `axxx503`) عبر حسابات التواصل الاجتماعي (https://bio.site/V7dt1) أو الإيميل (`v7dtads@gmail.com`) وإعلامه بالموضوع للاتفاق على **تقاسم الأرباح**.
> - **عند النشر العام (غير التجاري)**: يكفي ويُشترط **ذكر اسم صاحب المشروع (`V7dt1` / `axxx503`) في حقوق التعريب** (وفي ملف `README_AR.txt` داخل الحزمة) كمساعد في البرومبت ومساعد في الاستخدام العام.

Use this skill whenever the user asks to localize/translate a video game into Arabic (`تعريب لعبة`), fix disconnected/reversed Arabic letters in a game, merge Arabic glyphs into game fonts, or build an Arabic localization patch.

## Mandatory 7-Phase Workflow

### Phase 1: Automatic Discovery & Safe Workspace
1. Verify access to the target game directory. Never claim inspection if the path is inaccessible.
2. Detect the engine, exact version, architecture (`x86` / `x86_64`), runtime (`Mono` / `IL2CPP` / `Pak` / `IoStore` / `PCK`), active localization system, and font assets from binary/file evidence.
3. Create an isolated workspace in `<scratch>/<game_name>_arabic` with a local Python virtual environment (`.venv`).
4. Record `SHA-256` hashes of all target original files in `backups/original_hashes.json` and copy clean originals to `backups/originals/` before any modification. Never touch user save directories.

### Phase 2: Engine-Specific Routing (Least Invasive Path)
- **Unity**: Inspect `StreamingAssets/aa` (`Addressables`), `resources.assets`, `sharedassets*.assets`, `Unity.Localization` `StringTable` MonoBehaviours, and `TMP_FontAsset` / `Font` objects.
  - Check `catalog.bin` for `m_Crc` values before modifying Addressables bundles.
  - If `resources.assets` strips custom MonoBehaviour TypeTrees (`obj.read_typetree()` fails), extract `obj.serialized_type.nodes` from a `TMP_FontAsset` inside an Addressables bundle and pass those nodes to `read_typetree(nodes)` / `save_typetree(tree, nodes)`.

### Phase 3: Intelligent Font Engineering
1. Select an OFL-licensed Arabic font matching the game's visual style (e.g., `Tajawal` under SIL OFL 1.1) unless the user attached a distributable font.
2. **Critical Isolated Presentation Forms-B Fix**:
   - Many Arabic fonts map isolated glyphs only to `U+0621..U+064A` and omit the 36 isolated codepoints in `U+FE80..U+FEF1` emitted by `arabic_reshaper`.
   - Always map all `LETTERS_ARABIC` `(isolated, initial, medial, final)` codepoints in `cmap`, falling back to `U+0621..U+064A` whenever `isolated` (`U+FE80..U+FEF1`) is absent from `cmap`.
3. Scale merged Arabic glyphs proportionally (`scale = 1.15 * (base_upm / arabic_upm)`) and verify `0` missing glyphs using `freetype-py` (`face.get_char_index(cp) != 0`) across all contextual forms, hamzas (`أ إ آ ؤ ئ ء`), and lam-alef ligatures (`لا لأ لإ لآ`).
4. Enable `m_IsMultiAtlasTexturesEnabled = 1` on static `TMP_FontAsset` objects or link dynamic fallback font assets.

### Phase 4: Early In-Game Rendering Proof
1. Before translating the full inventory, inject a representative 30–60 string Arabic test build covering connected letters, mixed Arabic + Latin + numbers, multi-line wrapping, `{placeholders}`, and UI buttons.
2. Keep logical Arabic (`logical_ar`) strictly separate from shaped/visual display Arabic (`display_ar`).
3. **Token-Safe Shaping & Line Wrapping**:
   - When the game engine renders LTR (`m_isRightToLeft = 0`) without native HarfBuzz shaping:
     1. Wrap long paragraphs into lines at natural word boundaries first (protecting `{...}` and `<...>` tokens so they are never split).
     2. Shape inner choices of `SmartFormat` plural expressions `{var:plural:choice1|choice2}` individually.
     3. Replace each `{...}` placeholder and `<...>` tag with a temporary strong-RTL sentinel character (`chr(0x05D0 + idx)`) before calling `arabic_reshaper.reshape()` and `bidi.algorithm.get_display(..., base_dir="R")`, then restore the original token.
4. Launch the game or inspect `Player.log` to confirm `0` missing-character warnings and `0` bundle load errors.

### Phase 5: Complete Contextual Localization
1. Extract the full string inventory (`extracted/master_inventory.json`) with stable IDs, table names, contexts, and placeholder lists.
2. Establish a unified glossary (`reports/glossary.json`) before translating batches.
3. Translate 100% of strings into natural, context-aware Modern Standard Arabic (`logical_ar`), preserving speaker voice, humor, and 100% of `{...}` / `<...>` placeholders.
4. Localize editable graphical text/posters using `Pillow` and visually inspect the result with `read_file` before injecting into `Texture2D` objects.

### Phase 6 & 7: Verification & Lightweight Reversible Package
1. Validate 100% translation coverage, 0 placeholder mismatches, 0 missing FreeType glyphs, and clean `UnityPy` re-opening of all modified bundles.
2. Build a beginner-friendly `package/` containing:
   - `Install-Arabic.bat` & `Install-Arabic.ps1`
   - `Uninstall-Arabic.bat` & `Uninstall-Arabic.ps1`
   - `README_AR.txt` & font license (`OFL.txt`)
   - Object-level patch payload (`payload/font_objects_patch.json.gz` + localized string/asset bundles) rather than redistributing multi-hundred-MB proprietary game archives.
3. Test clean install, re-install/update, and full uninstall (verifying restored `SHA-256` hashes match `original_hashes.json` 100%) before declaring completion.

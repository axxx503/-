# تقرير إنجاز تعريب لعبة over the hill

> [!CAUTION]
> **⚠️ تنبيه الاستخدام وحقوق الملكية**: يُمنع استخدام هذا المشروع أو البرومبت أو الأدوات بشكل تجاري. في حال الرغبة بالاستخدام التجاري، يجب التواصل المسبق عبر حسابات التواصل الاجتماعي (https://bio.site/V7dt1) أو الإيميل (`v7dtads@gmail.com`) وإعلام صاحب المشروع (`V7dt1` / `axxx503`) للاتفاق على **تقاسم الأرباح**. أما عند النشر العام المجاني، فيكفي **ذكر اسم (`V7dt1` / `axxx503`) في التعريب** كمساعد في البرومبت والاستخدام العام.

## 1. معلومات اللعبة والمحرك (المؤكدة من الفحص الفعلي)
- **اسم اللعبة**: `over the hill` (المطور والناشر: `Funselektor Labs Inc.`)
- **مسار اللعبة**: `C:\Program Files (x86)\Steam\steamapps\common\over the hill`
- **المحرك والإصدار**: **Unity `6000.0.75f1 (26349cd2a5c8)`**
- **المعمارية والمنصة**: `StandaloneWindows64` (`x86_64`) — **IL2CPP** (`GameAssembly.dll`)
- **نظام النصوص والترجمة**: `Unity.Localization` عبر حزم `Addressables` مع `TextMeshPro` (`FunTextTMP`).

---

## 2. البصمات الرقمية للملفات الأصلية (SHA-256)
| الملف | المسار النسبي داخل اللعبة | SHA-256 الأصلي |
|---|---|---|
| `resources.assets` | `over the hill_Data\resources.assets` | `168CD3E8894F57E925B5204678F4EEFB5C14A1A12A1335EFF1537DC67B428941` |
| `ui_assets_all...bundle` | `over the hill_Data\StreamingAssets\aa\StandaloneWindows64\ui_assets_all_2301a0cc01bcb1fde33af05146facb2b.bundle` | `DEBCD14E01BBC9196B360D022956AE332E7BD107EF5BA1C7522BC0B62A95166C` |
| `localization-string-tables-english(en)_assets_all.bundle` | `over the hill_Data\StreamingAssets\aa\StandaloneWindows64\localization-string-tables-english(en)_assets_all.bundle` | `688493C81410A6A76A29A2327CEEBD4EB205BA57E9AE230B2E72FA9DEDAAC154` |
| `localization-assets-shared_assets_all.bundle` | `over the hill_Data\StreamingAssets\aa\StandaloneWindows64\localization-assets-shared_assets_all.bundle` | `96A13F08876307FC27AB94C63ABDA3605985CC2F77E97FDFE77D7208EA579E7D` |

---

## 3. هندسة الخطوط والعرض العربي
- **الخط المختار**: عائلة خط **Tajawal** (`Regular`, `Medium`, `Bold`, `ExtraBold`, `Black`) المرخصة برخصة **SIL Open Font License 1.1** الحرة (`OFL.txt`).
- **معالجة المحارف والأشكال**:
  - دمج محارف العربية وأشكال الربط (`Arabic Presentation Forms-A & B`) بما فيها الأشكال المنفصلة الـ 36 (`U+FE80..U+FEF1`) والهمزات (`أ إ آ ؤ ئ ء`) وتراكيب لام ألف (`لا لأ لإ لآ`) مع الحفاظ الكامل على الحروف اللاتينية والأرقام والرموز في جميع ملفات الخطوط الـ 13 داخل اللعبة.
  - تفعيل `m_IsMultiAtlasTexturesEnabled = 1` وربط `m_FallbackFontAssetTable` في أصول `TMP_FontAsset`.
  - الاحتفاظ بالنص العربي المنطقي (`logical_ar`) منفصلاً عن نص العرض المشكّل والمرتب بصرياً (`display_ar`) في `extracted/master_inventory.json` مع حماية المتغيرات `{...}` والوسوم `<...>` وتقسيم الأسطر الطويلة عند حدود الكلمات الطبيعية.

---

## 4. إحصائيات التعريب الشامل
- **إجمالي السلاسل النصية المعربة والمحقونة**: **1,499 / 1,499 (100%)**:
  - جدول `Universal_en`: **16 / 16** (100%)
  - جدول `Menus_en`: **604 / 604** (100%)
  - جدول `Dialogues_en`: **217 / 217** (100% — يشمل كامل التدريب وحوارات الميكانيكي ومشاهد الأحلام الـ 48)
  - جدول `Content_en`: **662 / 662** (100% — يشمل جميع المركبات وقصصها الساخرة، الترقيات، الإكسسوارات، الأبواق، الأدوات، الحيوانات، الطقس، وجميع معالم كندا والجزائر)
- **الصور والملصقات المعربة داخل اللعبة**:
  - `Canada_English`: معرب بصرياً إلى **«جبال فالهالا / كندا»**
  - `Algeria_English`: معرب بصرياً إلى **«الجزائر»**
- **أخطاء المتغيرات أو الوسوم**: **0**
- **الحروف الناقصة في الخطوط (FreeType & Player.log)**: **0**

---

## 5. حزمة التثبيت والإزالة (`package\`)
- المسار: `C:\Users\m2233\.gemini\antigravity\scratch\over_the_hill_arabic\package`
- الحجم الكلي للحزمة: **~3.8 ميجابايت فقط** (تعتمد على باتش كائنات محدد دون إعادة توزيع أرشيفات اللعبة الضخمة).
- تشمل:
  - `Install-Arabic.bat` و `Install-Arabic.ps1`
  - `Uninstall-Arabic.bat` و `Uninstall-Arabic.ps1`
  - `README_AR.txt` و `OFL.txt`
  - `payload\` و `tools\apply_patch.py`


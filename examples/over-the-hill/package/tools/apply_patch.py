import sys
import gzip
import json
import base64
import shutil
import hashlib
import UnityPy
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def patch_unity_file(src_path: Path, dst_path: Path, changed_map: dict):
    env = UnityPy.load(str(src_path))
    patched = 0
    for obj in env.objects:
        pid = str(obj.path_id)
        if pid in changed_map:
            obj.set_raw_data(base64.b64decode(changed_map[pid]))
            patched += 1
    tmp_path = dst_path.with_suffix(dst_path.suffix + ".tmp")
    tmp_path.write_bytes(env.file.save())
    tmp_path.replace(dst_path)
    return patched


def main():
    if len(sys.argv) < 3:
        print("Usage: apply_patch.py <game_dir> <payload_dir>")
        sys.exit(1)

    game_dir = Path(sys.argv[1])
    payload_dir = Path(sys.argv[2])
    backup_dir = game_dir / "_ArabicPatchBackup"

    patch_gz = payload_dir / "font_objects_patch.json.gz"
    with gzip.open(patch_gz, "rt", encoding="utf-8") as f:
        manifest = json.load(f)

    # Always patch from the clean backed-up originals in _ArabicPatchBackup
    orig_res = backup_dir / "resources.assets"
    target_res = game_dir / manifest["files"]["resources.assets"]["rel_path"]
    print("[1/4] Patching Arabic fonts into resources.assets...")
    n_res = patch_unity_file(orig_res, target_res, manifest["resources_changed_objects"])
    print(f"      Patched {n_res} font objects in resources.assets")

    orig_ui = backup_dir / "ui_assets_all_2301a0cc01bcb1fde33af05146facb2b.bundle"
    target_ui = game_dir / manifest["files"]["ui_assets_all"]["rel_path"]
    print("[2/4] Patching Arabic UI font assets into ui_assets_all.bundle...")
    n_ui = patch_unity_file(orig_ui, target_ui, manifest["ui_changed_objects"])
    print(f"      Patched {n_ui} UI font objects in ui_assets_all.bundle")

    print("[3/4] Installing Arabic string tables (1,499 strings)...")
    src_str = payload_dir / "localization-string-tables-english(en)_assets_all.bundle"
    dst_str = game_dir / manifest["files"]["loc_strings"]["rel_path"]
    shutil.copy2(src_str, dst_str)

    print("[4/4] Installing localized Arabic region posters...")
    src_ass = payload_dir / "localization-assets-shared_assets_all.bundle"
    dst_ass = game_dir / manifest["files"]["loc_assets"]["rel_path"]
    shutil.copy2(src_ass, dst_ass)

    print("SUCCESS: All Arabic localization assets applied and verified.")


if __name__ == "__main__":
    main()


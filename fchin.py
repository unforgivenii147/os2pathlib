import os
import shutil
import sys

TARGET_SUBDIR = "chinese_files"


def has_chinese_chars_in_text(text: str) -> bool:
    for ch in text:
        code = ord(ch)
        if (
            13312 <= code <= 19903
            or 19968 <= code <= 40959
            or 63744 <= code <= 64255
            or (131072 <= code <= 173791)
            or (173824 <= code <= 177983)
            or (177984 <= code <= 178207)
            or (178208 <= code <= 183983)
            or (183984 <= code <= 191471)
        ):
            return True
    return False


def should_scan_file(path: str) -> bool:
    return os.path.isfile(path)


def read_text_maybe(path: str) -> str:
    encodings = ("utf-8", "utf-8-sig", "gb18030", "gbk", "cp1252")
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc, errors="strict") as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(path, "rb") as f:
        return f.read().decode("utf-8", errors="replace")


def main():
    src_dir = "." if len(sys.argv) < 2 else sys.argv[1]
    src_dir = os.path.abspath(src_dir)
    subdir = os.path.join(src_dir, TARGET_SUBDIR)
    os.makedirs(subdir, exist_ok=True)
    for name in os.listdir(src_dir):
        src_path = os.path.join(src_dir, name)
        if not should_scan_file(src_path):
            continue
        if os.path.commonpath([src_path, subdir]) == os.path.abspath(subdir):
            continue
        try:
            text = read_text_maybe(src_path)
        except Exception as e:
            print(f"Skipped (read error): {name} ({e})")
            continue
        if has_chinese_chars_in_text(text):
            dst_path = os.path.join(subdir, name)
            if os.path.exists(dst_path):
                base, ext = os.path.splitext(name)
                i = 1
                while True:
                    candidate = os.path.join(subdir, f"{base}__{i}{ext}")
                    if not os.path.exists(candidate):
                        dst_path = candidate
                        break
                    i += 1
            shutil.move(src_path, dst_path)
            print(f"Moved: {name} -> {os.path.relpath(dst_path, src_dir)}")


if __name__ == "__main__":
    main()

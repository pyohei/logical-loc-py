import os
import shutil
from datetime import datetime
from pathlib import Path


def count_code_lines(src_dir, exclude_dirs=[], exclude_files=[], ext_list=[]):
    # Create tmp directory if not exists
    repository_name = os.path.basename(src_dir)
    dir_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{repository_name}"
    dest_dir = os.path.join(Path(".").resolve(), "repos", dir_name)
    print(dest_dir)
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir)

    # Get target file paths
    target_files = []
    for root, dirs, files in os.walk(src_dir):
        # 除外ディレクトリの除外
        for exclude_dir in exclude_dirs:
            if exclude_dir in dirs:
                dirs.remove(exclude_dir)

        for file in files:
            _, ext = os.path.splitext(file)
            # 拡張子が対象外の場合、コピーしない
            if ext not in ext_list:
                continue

            # 除外ファイルの除外
            if file in exclude_files:
                continue
            target_files.append(os.path.join(root, file))

    file_lines = []
    fixed = 0
    total = 0
    # Copy each target file to dest_dir
    for file_path in target_files:
        size = os.path.getsize(file_path)
        with open(file_path, "r") as f:
            # Exclude empty and comment lines
            lines = [line for line in f.readlines()]
        new_lines = []
        is_comment = False
        code_comment = False
        code_str = ""
        is_fixed = False
        for org_line in lines:
            line = org_line.strip()

            # ラインコメントアウトを無視
            if len(line) == 0 or line.startswith("#") or line.startswith("//"):
                is_fixed = True
                continue

            if code_comment:
                if code_str in line:
                    code_str = ""
                    code_comment = False
                new_lines.append(org_line)
                continue

            # 複数行コメントアウト
            if not is_comment:
                if line.startswith("/*"):
                    if "*/" in line:
                        is_fixed = True
                        continue
                    commnet_str = "*/"
                    is_comment = True
                elif line.startswith('"""'):
                    if line.count('"""') >= 2:
                        is_fixed = True
                        continue
                    commnet_str = '"""'
                    is_comment = True
                elif line.startswith("'''"):
                    if line.count("'''") >= 2:
                        is_fixed = True
                        continue
                    commnet_str = "'''"
                    is_comment = True
                elif line.startswith("'''"):
                    if line.count("'''") >= 2:
                        is_fixed = True
                        continue
                    commnet_str = "'''"
                    is_comment = True
                elif '"""' in line:
                    code_comment = True
                    code_str = '"""'
                elif "'''" in line:
                    code_comment = True
                    code_str = "'''"
                elif line.startswith("<!--"):
                    if "-->" in line:
                        is_fixed = True
                        continue
                    commnet_str = "-->"
                    is_comment = True

                if is_comment:
                    is_fixed = True
                    continue

            if is_comment:
                if commnet_str in line:
                    is_comment = False
                is_fixed = True
                continue

            new_lines.append(org_line)

        if size and is_fixed:
            fixed += 1
        total += len(new_lines)
        file_lines.append((file_path, len(new_lines), is_fixed))

        dest_file_path = os.path.join(dest_dir, file_path.lstrip("/"))
        os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
        with open(dest_file_path, mode="w", encoding="utf-8") as f:
            f.write("".join(new_lines))

    result_dir = os.path.join(Path(".").resolve(), "results")
    result_file = os.path.join(result_dir, f"{dir_name}.txt")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    with open(result_file, "w") as f:
        for line in file_lines:
            f.write(f"{line[0]}, {line[1]},  {line[2]}" + "\n")
    print(f"TOTAL: {total}, FIXED: {fixed}")


if __name__ == "__main__":
    import argparse
    import configparser
    import json

    parser = argparse.ArgumentParser(description="Count code lines")
    parser.add_argument("source", help="Repository path")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read("config.ini")

    default = config["DEFAULT"]
    exclude_dirs = eval(default["EXCLUDE_DIRS"])
    exclude_files = eval(default["EXCLUDE_FILES"])
    ext_list = eval(default["EXT_LIST"])

    print(f"START: {args.source}")
    count_code_lines(args.source, exclude_dirs, exclude_files, ext_list)
    print("END")

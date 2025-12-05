# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tqdm",
#     "python-dotenv",
# ]
# ///

import shutil
import os
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

def flatten_directory_files(source_path, dest_path):
    """
    指定ディレクトリ以下を再帰的に探索し、
    階層構造をファイル名に反映させて1箇所にコピーします。
    """
    source_dir = Path(source_path)
    dest_dir = Path(dest_path)

    # 1. ソースディレクトリの確認
    if not source_dir.exists():
        print(f"[エラー] 元のディレクトリが見つかりません: {source_dir}")
        return

    if source_dir.resolve() == dest_dir.resolve():
        print(f"[エラー] 元のディレクトリと出力先が同じです: {source_dir}")
        return

    # 2. 出力先の作成
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 対象拡張子 (必要に応じて追加してください)
    target_extensions = {'.xlsx', '.xls', '.pptx', '.ppt'}

    print("ファイル一覧をスキャン中... (ファイル数によっては数秒かかります)")

    # 3. 【事前スキャン】総数を確定させる
    # tqdmで正確なバーを出すために、イテレータではなく一度リストにします
    files_to_process = []
    skipped_files = []

    # rglob('*') は日本語ファイル名も深い階層もすべて取得します
    for p in source_dir.rglob('*'):
        if p.is_file():
            if p.suffix.lower() in target_extensions:
                files_to_process.append(p)
            else:
                skipped_files.append(p)

    total_files = len(files_to_process)
    print(f"スキャン完了: 対象ファイル {total_files} 件")
    print("-" * 40)

    if total_files == 0:
        print("対象ファイルが見つかりませんでした。終了します。")
        return

    # 4. 【本処理】プログレスバー付きでコピー実行
    success_count = 0
    error_count = 0
    seen_filenames = set()

    for file_path in tqdm(files_to_process, desc="Copying", unit="file"):
        try:
            # 相対パスを取得 (例: dir1/dir2/file.xlsx)
            relative_path = file_path.relative_to(source_dir)

            # フォルダ区切りをアンダースコアに変換 (例: dir1_dir2_file.xlsx)
            new_filename = "_".join(relative_path.parts)

            # 出力先パスの生成（衝突時は連番を付与）
            base_name = new_filename
            counter = 1
            dest_file_path = dest_dir / new_filename

            while new_filename in seen_filenames or dest_file_path.exists():
                # 拡張子を分離
                stem = Path(base_name).stem
                suffix = Path(base_name).suffix
                new_filename = f"{stem}_{counter}{suffix}"
                dest_file_path = dest_dir / new_filename
                counter += 1

            seen_filenames.add(new_filename)

            # コピー実行 (移動したい場合は shutil.move に変更)
            shutil.copy2(file_path, dest_file_path)
            success_count += 1

        except Exception as e:
            # エラー時はバーを崩さずにログ出力
            tqdm.write(f"[エラー] {file_path.name}: {e}")
            error_count += 1

    print("-" * 40)
    print(f"処理完了: 成功 {success_count} 件 / 失敗 {error_count} 件")
    print(f"保存先: {dest_dir}")

    if skipped_files:
        print("-" * 40)
        print("【スキップされたファイル一覧】(拡張子対象外)")
        for p in skipped_files:
            print(f"{p}")

# ==========================================
# 設定エリア
# ==========================================

# .env から設定を読み込み
load_dotenv()

# 1. 元のファイルが入っているディレクトリ
SOURCE_DIR = os.getenv("SOURCE_DIR")

# 2. まとめたファイルを保存するディレクトリ
DEST_DIR = os.getenv("DEST_DIR")

if __name__ == "__main__":
    if not SOURCE_DIR or not DEST_DIR:
        print("[エラー] .env ファイルに SOURCE_DIR と DEST_DIR を設定してください。")
    else:
        flatten_directory_files(SOURCE_DIR, DEST_DIR)

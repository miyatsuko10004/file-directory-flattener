# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tqdm",
# ]
# ///

import shutil
from pathlib import Path
from tqdm import tqdm  # 進捗バー表示用

def flatten_directory_files(source_path, dest_path):
    """
    指定ディレクトリ以下の特定ファイルを、階層構造を含んだファイル名にリネームして
    1つのフォルダに集約します。
    """
    # パスオブジェクトに変換
    source_dir = Path(source_path)
    dest_dir = Path(dest_path)

    # ソースディレクトリが存在しない場合は終了
    if not source_dir.exists():
        print(f"エラー: 元のディレクトリが見つかりません -> {source_dir}")
        return

    # 出力先ディレクトリがない場合は作成
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 対象とする拡張子のリスト
    target_extensions = {'.xlsx', '.xls', '.pptx', '.ppt'}

    print("ファイル一覧を取得中...")

    # 事前にファイルリストを作成（tqdmで総数を表示するため）
    # rglob('*') で全階層を探索
    target_files = []
    for p in source_dir.rglob('*'):
        if p.is_file() and p.suffix.lower() in target_extensions:
            target_files.append(p)

    print(f"処理対象: {len(target_files)} 件のファイルが見つかりました。")
    print(f"出力先: {dest_dir}")
    print("-" * 30)

    # tqdmを使ってループ処理（descでバーの左に文字を表示、unitで単位を表示）
    for file_path in tqdm(target_files, desc="Processing", unit="file"):
        try:
            # ソースディレクトリからの相対パスを取得 (例: sub/folder/data.xlsx)
            relative_path = file_path.relative_to(source_dir)
            
            # フォルダ階層をアンダースコアで結合してファイル名化
            # 例: sub/folder/data.xlsx -> sub_folder_data.xlsx
            new_filename = "_".join(relative_path.parts)
            
            # 出力先のフルパス
            dest_file_path = dest_dir / new_filename

            # 【実行】コピー処理
            # ※ 元ファイルを消して移動したい場合は shutil.move に変更してください
            shutil.copy2(file_path, dest_file_path)

        except Exception as e:
            # エラーが起きても止まらずに表示だけして次へ
            tqdm.write(f"[エラー] {file_path.name}: {e}")

    print("-" * 30)
    print("すべての処理が完了しました。")

# ==========================================
# 設定エリア (ここを書き換えてください)
# ==========================================

# 1. 元のファイルが入っているディレクトリ (絶対パス推奨)
SOURCE_DIR = r"C:\Users\Target_User\Documents\Project_Files"

# 2. まとめたファイルを保存するディレクトリ
DEST_DIR = r"C:\Users\Target_User\Documents\Project_Flattened"

if __name__ == "__main__":
    flatten_directory_files(SOURCE_DIR, DEST_DIR)

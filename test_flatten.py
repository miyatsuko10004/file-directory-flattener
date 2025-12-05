import shutil
from pathlib import Path
import pytest
from flatten import flatten_directory_files

@pytest.fixture
def source_dir(tmp_path):
    d = tmp_path / "source"
    d.mkdir()
    return d

@pytest.fixture
def dest_dir(tmp_path):
    d = tmp_path / "dest"
    # dest_dir is created by the function, but we define the path here
    return d

def test_flatten_basic(source_dir, dest_dir):
    # Setup: Create nested files
    (source_dir / "dir1").mkdir()
    (source_dir / "dir1" / "file1.xlsx").touch()
    (source_dir / "dir2").mkdir()
    (source_dir / "dir2" / "sub").mkdir()
    (source_dir / "dir2" / "sub" / "file2.pptx").touch()
    
    # Execute
    flatten_directory_files(source_dir, dest_dir)
    
    # Verify
    assert (dest_dir / "dir1_file1.xlsx").exists()
    assert (dest_dir / "dir2_sub_file2.pptx").exists()

@pytest.fixture
def log_file_path(tmp_path, monkeypatch):
    p = tmp_path / "test.log"
    monkeypatch.setenv("LOG_FILE", str(p))
    return p

def test_flatten_skip_extension(source_dir, dest_dir, log_file_path):
    # Setup: Create file with ignored extension
    (source_dir / "file.txt").touch()
    (source_dir / "file.xlsx").touch()
    
    # Execute
    flatten_directory_files(source_dir, dest_dir)
    
    # Verify
    assert not (dest_dir / "file.txt").exists()
    assert (dest_dir / "file.xlsx").exists()
    
    # Check logs for skipped file
    assert log_file_path.exists()
    content = log_file_path.read_text(encoding="utf-8")
    assert "file.txt" in content

def test_flatten_collision(source_dir, dest_dir):
    # Setup: Create files that map to same name
    # source/dir1/file.xlsx -> dir1_file.xlsx
    # source/dir1_file.xlsx -> dir1_file.xlsx
    (source_dir / "dir1").mkdir()
    (source_dir / "dir1" / "file.xlsx").touch()
    (source_dir / "dir1_file.xlsx").touch()
    
    # Execute
    flatten_directory_files(source_dir, dest_dir)
    
    # Verify
    # Both files should exist, one with original name and one with _1 suffix
    files = list(dest_dir.glob("*.xlsx"))
    assert len(files) == 2, "Should have exactly 2 files"
    filenames = {f.name for f in files}
    assert filenames == {"dir1_file.xlsx", "dir1_file_1.xlsx"}, \
        f"Expected dir1_file.xlsx and dir1_file_1.xlsx, got {filenames}"

def test_flatten_source_not_exists(tmp_path, log_file_path):
    source = tmp_path / "non_existent"
    dest = tmp_path / "dest"
    
    flatten_directory_files(source, dest)
    
    assert log_file_path.exists()
    content = log_file_path.read_text(encoding="utf-8")
    assert "[エラー] 元のディレクトリが見つかりません" in content

def test_flatten_source_equals_dest(source_dir, log_file_path):
    flatten_directory_files(source_dir, source_dir)
    
    assert log_file_path.exists()
    content = log_file_path.read_text(encoding="utf-8")
    assert "[エラー] 元のディレクトリと出力先が同じです" in content

def test_flatten_custom_extensions(source_dir, dest_dir, monkeypatch):
    # Setup: Create files with various extensions
    (source_dir / "file.custom").touch()
    (source_dir / "file.xlsx").touch()
    
    # Set environment variable to only include .custom
    monkeypatch.setenv("TARGET_EXTENSIONS", ".custom")
    
    # Execute
    flatten_directory_files(source_dir, dest_dir)
    
    # Verify
    assert (dest_dir / "file.custom").exists()
    assert not (dest_dir / "file.xlsx").exists()

def test_flatten_logging(source_dir, dest_dir, log_file_path):
    # Setup: Create a file
    (source_dir / "file.xlsx").touch()
    
    # Execute
    flatten_directory_files(source_dir, dest_dir)
    
    # Verify log file exists and contains content
    assert log_file_path.exists()
    content = log_file_path.read_text(encoding="utf-8")
    assert "スキャン完了" in content or "Copying" in content or "処理完了" in content

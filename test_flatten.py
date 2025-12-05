import shutil
from pathlib import Path
import pytest
import logging
from flatten import flatten_directory_files

@pytest.fixture
def test_logger():
    logger = logging.getLogger("test_flatten")
    logger.setLevel(logging.INFO)
    # Ensure propagation so caplog can catch it
    logger.propagate = True
    return logger

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

def test_flatten_skip_extension(source_dir, dest_dir, log_file_path, monkeypatch):
    # Setup: Set explicit target extensions
    monkeypatch.setenv("TARGET_EXTENSIONS", ".xlsx")

    # Setup: Create file with ignored extension
    (source_dir / "file.txt").touch()
    (source_dir / "file.xlsx").touch()
    
    # Execute
    flatten_directory_files(source_dir, dest_dir)
    
    # Verify
    assert not (dest_dir / "file.txt").exists()
    assert (dest_dir / "file.xlsx").exists()

def test_flatten_same_directory(source_dir, caplog, test_logger):
    # Setup: source and dest are the same
    flatten_directory_files(source_dir, source_dir, logger=test_logger)
    
    # Verify error log
    assert "元のディレクトリと出力先が同じです" in caplog.text

def test_flatten_source_not_exists(tmp_path, caplog, test_logger):
    # Setup: non-existent source
    non_existent = tmp_path / "non_existent"
    dest = tmp_path / "dest"
    
    flatten_directory_files(non_existent, dest, logger=test_logger)
    
    # Verify error log
    assert "元のディレクトリが見つかりません" in caplog.text

def test_flatten_no_files(source_dir, dest_dir, caplog, test_logger, monkeypatch):
    # Ensure no environment variable interferes
    monkeypatch.delenv("TARGET_EXTENSIONS", raising=False)
    
    # Setup: empty source directory (or only ignored files)
    (source_dir / "file.txt").touch()
    
    # Execute with default extensions (txt is ignored)
    flatten_directory_files(source_dir, dest_dir, logger=test_logger)
    
    # Verify info log
    assert "対象ファイルが見つかりませんでした" in caplog.text

def test_flatten_copy_error(source_dir, dest_dir, monkeypatch, caplog, test_logger):
    # Setup: Create a valid file
    (source_dir / "file.xlsx").touch()
    
    # Mock shutil.copy2 to raise an exception
    def mock_copy2(_src, _dst):
        raise PermissionError("Mocked permission error")
    
    monkeypatch.setattr(shutil, "copy2", mock_copy2)
    
    # Ensure deterministic extensions
    monkeypatch.setenv("TARGET_EXTENSIONS", ".xlsx")
    
    # Execute
    flatten_directory_files(source_dir, dest_dir, logger=test_logger)
    
    # Verify error log and counts
    assert "Mocked permission error" in caplog.text
    assert "処理完了: 成功 0 件 / 失敗 1 件" in caplog.text
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

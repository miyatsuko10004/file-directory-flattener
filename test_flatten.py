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

def test_flatten_skip_extension(source_dir, dest_dir, capsys):
    # Setup: Create file with ignored extension
    (source_dir / "file.txt").touch()
    (source_dir / "file.xlsx").touch()
    
    # Execute
    flatten_directory_files(source_dir, dest_dir)
    
    # Verify
    assert not (dest_dir / "file.txt").exists()
    assert (dest_dir / "file.xlsx").exists()
    
    # Check logs for skipped file
    captured = capsys.readouterr()
    assert "file.txt" in captured.out

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
    # One should be dir1_file.xlsx, the other dir1_file_1.xlsx
    assert (dest_dir / "dir1_file.xlsx").exists()
    assert (dest_dir / "dir1_file_1.xlsx").exists()

def test_flatten_source_not_exists(tmp_path, capsys):
    source = tmp_path / "non_existent"
    dest = tmp_path / "dest"
    
    flatten_directory_files(source, dest)
    
    captured = capsys.readouterr()
    assert "[エラー] 元のディレクトリが見つかりません" in captured.out

def test_flatten_source_equals_dest(source_dir, capsys):
    flatten_directory_files(source_dir, source_dir)
    
    captured = capsys.readouterr()
    assert "[エラー] 元のディレクトリと出力先が同じです" in captured.out

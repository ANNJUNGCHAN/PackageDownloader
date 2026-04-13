"""
압축 서비스
- 단일 zip 압축
- 분할 압축
"""

import zipfile
import os
from pathlib import Path
from datetime import datetime


def compress_single(output_dir: str, archive_name: str = None) -> str:
    """
    단일 zip 압축

    Args:
        output_dir: 압축할 폴더 경로
        archive_name: 압축 파일명 (없으면 자동 생성)

    Returns:
        생성된 압축 파일 경로
    """
    output_path = Path(output_dir)

    if not archive_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{output_path.name}_{timestamp}.zip"

    zip_path = output_path.parent / archive_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in output_path.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(output_path.parent)
                zf.write(file, arcname)

    return str(zip_path)


def compress_split(output_dir: str, split_size_mb: int = 200, archive_name: str = None) -> list[str]:
    """
    분할 압축

    Args:
        output_dir: 압축할 폴더 경로
        split_size_mb: 분할 크기 (MB)
        archive_name: 압축 파일명 (없으면 자동 생성)

    Returns:
        생성된 압축 파일 경로 목록
    """
    output_path = Path(output_dir)
    split_size = split_size_mb * 1024 * 1024  # MB to bytes

    if not archive_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{output_path.name}_{timestamp}"

    # 먼저 단일 zip 생성
    temp_zip = output_path.parent / f"{archive_name}_temp.zip"

    with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in output_path.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(output_path.parent)
                zf.write(file, arcname)

    # 분할 필요 여부 확인
    zip_size = temp_zip.stat().st_size

    if zip_size <= split_size:
        # 분할 불필요 - 이름 변경 후 반환
        final_zip = output_path.parent / f"{archive_name}.zip"
        temp_zip.rename(final_zip)
        return [str(final_zip)]

    # 분할 압축
    result_files = []
    part_num = 1

    with open(temp_zip, "rb") as f:
        while True:
            chunk = f.read(split_size)
            if not chunk:
                break

            if part_num == 1:
                part_name = f"{archive_name}.zip"
            else:
                part_name = f"{archive_name}.z{part_num - 1:02d}"

            part_path = output_path.parent / part_name
            with open(part_path, "wb") as pf:
                pf.write(chunk)

            result_files.append(str(part_path))
            part_num += 1

    # 임시 파일 삭제
    temp_zip.unlink()

    return result_files


def format_size(bytes: int) -> str:
    """용량을 읽기 쉬운 형식으로"""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes / (1024 * 1024 * 1024):.2f} GB"


def compress_output(output_dir: str, split_size_mb: int = None) -> list[str]:
    """
    출력물 압축 (메인 함수)

    Args:
        output_dir: 압축할 폴더 경로
        split_size_mb: 분할 크기 (MB), None이면 단일 압축

    Returns:
        생성된 압축 파일 경로 목록
    """
    print("\n[압축 생성]")

    if split_size_mb:
        files = compress_split(output_dir, split_size_mb)
        if len(files) > 1:
            print(f"  분할 압축 완료 ({len(files)}개 파일)")
        else:
            print(f"  압축 완료 (분할 불필요)")
    else:
        files = [compress_single(output_dir)]
        print(f"  압축 완료")

    for f in files:
        size = Path(f).stat().st_size
        print(f"  - {Path(f).name} ({format_size(size)})")

    return files


# 테스트
if __name__ == "__main__":
    import tempfile
    import shutil

    # 테스트 폴더 생성
    test_dir = Path(tempfile.mkdtemp()) / "test_output"
    test_dir.mkdir()
    (test_dir / "packages").mkdir()
    (test_dir / "packages" / "test1.whl").write_text("test content 1")
    (test_dir / "packages" / "test2.whl").write_text("test content 2")
    (test_dir / "install.sh").write_text("#!/bin/bash\necho test")
    (test_dir / "requirements.txt").write_text("requests\nclick")

    print("테스트 폴더:", test_dir)

    # 단일 압축 테스트
    print("\n[단일 압축 테스트]")
    result = compress_output(str(test_dir))
    print("결과:", result)

    # 정리
    for f in result:
        Path(f).unlink()

    # 분할 압축 테스트 (작은 크기로)
    print("\n[분할 압축 테스트]")
    result = compress_split(str(test_dir), split_size_mb=1)  # 1MB로 테스트
    print("결과:", result)

    # 정리
    shutil.rmtree(test_dir.parent)

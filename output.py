"""
출력물 생성 서비스
- 설치 스크립트 생성
- requirements.txt 복사
- 결과 리포트 생성
"""

import shutil
from pathlib import Path
from datetime import datetime

from env import Environment
from download import DownloadResult


def generate_install_script(output_dir: str, env: Environment):
    """설치 스크립트 생성"""
    output_path = Path(output_dir)

    # Linux용 install.sh
    sh_content = """#!/bin/bash
pip install --no-index --find-links="./packages" -r requirements.txt
"""
    sh_path = output_path / "install.sh"
    sh_path.write_text(sh_content, encoding="utf-8")

    # Windows용 install.bat
    bat_content = """@echo off
pip install --no-index --find-links="./packages" -r requirements.txt
pause
"""
    bat_path = output_path / "install.bat"
    bat_path.write_text(bat_content, encoding="utf-8")

    print(f"  install.sh 생성 OK")
    print(f"  install.bat 생성 OK")


def copy_requirements(src_path: str, output_dir: str):
    """requirements.txt 복사"""
    src = Path(src_path)
    dst = Path(output_dir) / "requirements.txt"

    shutil.copy(src, dst)
    print(f"  requirements.txt 복사 OK")


def get_total_size(output_dir: str) -> int:
    """다운로드된 파일 총 용량 (bytes)"""
    packages_dir = Path(output_dir) / "packages"
    if not packages_dir.exists():
        packages_dir = Path(output_dir)

    total = 0
    for f in packages_dir.glob("*.whl"):
        total += f.stat().st_size
    return total


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


def generate_report(
    output_dir: str,
    env: Environment,
    result: DownloadResult,
    elapsed_seconds: float
) -> str:
    """결과 리포트 생성"""
    output_path = Path(output_dir)
    packages_dir = output_path / "packages"

    # 패키지 파일 목록
    whl_files = list(packages_dir.glob("*.whl")) if packages_dir.exists() else list(output_path.glob("*.whl"))
    total_size = sum(f.stat().st_size for f in whl_files)

    # 리포트 내용
    report = f"""# 패키지 다운로드 리포트

## 환경 정보
- 환경 이름: {env.name}
- OS: {env.os}
- Python: {env.python}
- 플랫폼: {env.platforms[0]}
- ABI: {env.abi}

## 다운로드 결과
- 생성 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 소요 시간: {elapsed_seconds:.1f}초
- 총 패키지: {len(whl_files)}개
- 총 용량: {format_size(total_size)}

## 성공 ({len(result.success)}개)
"""
    for pkg in result.success:
        report += f"- {pkg}\n"

    if result.failed:
        report += f"\n## 실패 ({len(result.failed)}개)\n"
        for pkg, err in result.failed:
            report += f"- {pkg}: {err}\n"

    report += f"\n## 다운로드된 파일 ({len(whl_files)}개)\n"
    for f in sorted(whl_files, key=lambda x: x.name):
        report += f"- {f.name} ({format_size(f.stat().st_size)})\n"

    # 파일로 저장
    report_path = output_path / "report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"  report.md 생성 OK")

    return report


def generate_outputs(output_dir: str, packages: list[str]):
    """간단한 출력물 생성 (UI용)"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Linux용 install.sh
    sh_content = """#!/bin/bash
pip install --no-index --find-links="./packages" -r requirements.txt
"""
    (output_path / "install.sh").write_text(sh_content, encoding="utf-8")

    # Windows용 install.bat
    bat_content = """@echo off
pip install --no-index --find-links="./packages" -r requirements.txt
pause
"""
    (output_path / "install.bat").write_text(bat_content, encoding="utf-8")

    # requirements.txt 생성
    req_content = "\n".join(packages)
    (output_path / "requirements.txt").write_text(req_content, encoding="utf-8")


def generate_all_outputs(
    output_dir: str,
    env: Environment,
    result: DownloadResult,
    requirements_path: str,
    elapsed_seconds: float
):
    """모든 출력물 생성"""
    output_path = Path(output_dir)

    # packages 폴더로 whl 파일 이동
    packages_dir = output_path / "packages"
    packages_dir.mkdir(exist_ok=True)

    for whl in output_path.glob("*.whl"):
        shutil.move(str(whl), str(packages_dir / whl.name))

    print("\n[출력물 생성]")
    generate_install_script(output_dir, env)
    copy_requirements(requirements_path, output_dir)
    generate_report(output_dir, env, result, elapsed_seconds)

    print(f"\n[완료] 출력 위치: {output_dir}")
    print(f"  - packages/     : 패키지 파일들")
    print(f"  - install.sh    : Linux 설치 스크립트")
    print(f"  - install.bat   : Windows 설치 스크립트")
    print(f"  - requirements.txt")
    print(f"  - report.md     : 다운로드 리포트")

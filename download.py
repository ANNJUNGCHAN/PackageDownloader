"""
패키지 다운로드 서비스
"""

import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from env import Environment


@dataclass
class DownloadResult:
    """다운로드 결과"""
    success: list[str] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)  # (패키지명, 에러)
    skipped: list[str] = field(default_factory=list)


def parse_requirements(file_path: str) -> list[str]:
    """requirements.txt 파싱"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"파일 없음: {file_path}")

    packages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 빈 줄, 주석 무시
            if not line or line.startswith("#"):
                continue
            # 환경 마커 제거 (예: package ; sys_platform == 'win32')
            pkg = line.split(";")[0].strip()
            if pkg:
                packages.append(pkg)

    return packages


def build_pip_command(
    packages: list[str],
    env: Environment,
    output_dir: str,
    no_deps: bool = False
) -> list[str]:
    """pip download 명령 생성"""
    cmd = [
        sys.executable, "-m", "pip", "download",
        "--dest", output_dir,
        "--python-version", env.python.replace(".", ""),
        "--implementation", "cp",
        "--abi", env.abi,
        "--only-binary=:all:",
    ]

    # 플랫폼 태그 추가
    for platform in env.platforms:
        cmd.extend(["--platform", platform])

    if no_deps:
        cmd.append("--no-deps")

    cmd.extend(packages)
    return cmd


def run_pip_download(cmd: list[str], quiet: bool = False) -> tuple[bool, str]:
    """pip download 실행"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0:
            return True, result.stdout
        return False, result.stderr
    except Exception as e:
        return False, str(e)


def download_packages(
    env: Environment,
    requirements_path: str,
    output_dir: str,
    retry: int = 2
) -> DownloadResult:
    """
    패키지 다운로드 (2단계 전략)

    1단계: --no-deps로 각 패키지 개별 다운로드
    2단계: 의존성 포함 전체 다운로드
    """
    result = DownloadResult()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # requirements.txt 파싱
    packages = parse_requirements(requirements_path)
    if not packages:
        return result

    print(f"\n[다운로드 시작]")
    print(f"  환경: {env.name} ({env.os}, Python {env.python})")
    print(f"  플랫폼: {env.platforms[0]}")
    print(f"  패키지 수: {len(packages)}")
    print(f"  출력: {output_dir}")
    print("-" * 50)

    # 1단계: 개별 패키지 다운로드 (--no-deps)
    print("\n[1단계] 개별 패키지 다운로드...")
    for i, pkg in enumerate(packages, 1):
        print(f"  ({i}/{len(packages)}) {pkg}", end=" ")

        success = False
        for attempt in range(retry + 1):
            cmd = build_pip_command([pkg], env, output_dir, no_deps=True)
            ok, msg = run_pip_download(cmd, quiet=True)

            if ok:
                print("OK")
                result.success.append(pkg)
                success = True
                break
            elif attempt < retry:
                print(f"재시도({attempt + 1})...", end=" ")

        if not success:
            print("FAIL")
            result.failed.append((pkg, msg.split("\n")[-2] if msg else "Unknown error"))

    # 2단계: 의존성 다운로드
    print("\n[2단계] 의존성 다운로드...")
    cmd = build_pip_command(packages, env, output_dir, no_deps=False)
    ok, msg = run_pip_download(cmd)

    if ok:
        print("  의존성 다운로드 완료 OK")
    else:
        print("  일부 의존성 다운로드 실패 (무시하고 계속)")

    # 결과 출력
    print("\n" + "=" * 50)
    print(f"[결과]")
    print(f"  성공: {len(result.success)}")
    print(f"  실패: {len(result.failed)}")

    if result.failed:
        print("\n[실패 목록]")
        for pkg, err in result.failed:
            print(f"  - {pkg}: {err[:50]}")

    return result


def download_packages_with_callback(
    env: Environment,
    packages: list[str],
    output_dir: str,
    retry: int = 2,
    on_progress=None,  # (current, total, pkg_name, status) -> None
    on_message=None,   # (message) -> None
    should_cancel=None  # () -> bool
) -> DownloadResult:
    """
    콜백 지원 패키지 다운로드

    Args:
        on_progress: 진행률 콜백 (현재, 총개수, 패키지명, 상태)
        on_message: 메시지 콜백
        should_cancel: 취소 여부 확인 콜백
    """
    result = DownloadResult()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not packages:
        return result

    total = len(packages)

    if on_message:
        on_message(f"다운로드 시작: {total}개 패키지")

    # 1단계: 개별 패키지 다운로드 (--no-deps)
    if on_message:
        on_message("[1단계] 개별 패키지 다운로드...")

    for i, pkg in enumerate(packages, 1):
        # 취소 확인
        if should_cancel and should_cancel():
            if on_message:
                on_message("다운로드 취소됨")
            break

        if on_progress:
            on_progress(i, total, pkg, "downloading")

        success = False
        for attempt in range(retry + 1):
            cmd = build_pip_command([pkg], env, output_dir, no_deps=True)
            ok, msg = run_pip_download(cmd, quiet=True)

            if ok:
                result.success.append(pkg)
                success = True
                if on_progress:
                    on_progress(i, total, pkg, "OK")
                break
            elif attempt < retry:
                if on_message:
                    on_message(f"  {pkg} 재시도({attempt + 1})...")

        if not success:
            error_msg = msg.split("\n")[-2] if msg else "Unknown error"
            result.failed.append((pkg, error_msg))
            if on_progress:
                on_progress(i, total, pkg, "FAIL")

    # 취소되지 않았으면 2단계 실행
    if not (should_cancel and should_cancel()):
        # 2단계: 의존성 다운로드
        if on_message:
            on_message("[2단계] 의존성 다운로드...")

        cmd = build_pip_command(packages, env, output_dir, no_deps=False)
        ok, msg = run_pip_download(cmd)

        if on_message:
            if ok:
                on_message("의존성 다운로드 완료")
            else:
                on_message("일부 의존성 다운로드 실패 (무시)")

    return result


# 테스트
if __name__ == "__main__":
    from env import EnvironmentService

    # 테스트 환경 생성
    svc = EnvironmentService()
    svc.create("test-dl", "ubuntu-22.04", "3.12")
    env = svc.get("test-dl")

    # 테스트 requirements.txt 생성
    test_req = Path("test_requirements.txt")
    test_req.write_text("requests\nclick\n")

    # 다운로드 테스트
    result = download_packages(env, str(test_req), "./test_packages")

    # 정리
    test_req.unlink()
    svc.delete("test-dl")

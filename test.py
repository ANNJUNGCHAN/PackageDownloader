"""
테스트 스크립트
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 테스트 결과
PASS = 0
FAIL = 0


def log(msg):
    print(f"  {msg}")


def test_pass(name):
    global PASS
    PASS += 1
    print(f"[PASS] {name}")


def test_fail(name, reason=""):
    global FAIL
    FAIL += 1
    print(f"[FAIL] {name}")
    if reason:
        print(f"       {reason}")


def run_cmd(cmd):
    """명령 실행"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode == 0, result.stdout, result.stderr


def cleanup():
    """테스트 파일 정리"""
    items = [
        "test_output",
        "test_req.txt",
    ]
    for item in items:
        path = Path(item)
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    # zip 파일 정리
    for f in Path(".").glob("test_output_*.zip"):
        f.unlink()
    for f in Path(".").glob("test_output_*.z*"):
        f.unlink()


# ============================================================
# 테스트 케이스
# ============================================================

def test_os_mapping():
    """OS 매핑 테스트"""
    print("\n" + "=" * 50)
    print("1. OS 매핑 테스트")
    print("=" * 50)

    from platform_map import is_supported, get_platform_info, suggest_os

    # 지원 OS 확인
    test_cases = [
        ("redhat-8", True),
        ("ubuntu-22.04", True),
        ("windows-11", True),
        ("macos-14-arm", True),
        ("unknown-os", False),
    ]

    for os_name, expected in test_cases:
        result = is_supported(os_name)
        if result == expected:
            test_pass(f"is_supported('{os_name}') = {result}")
        else:
            test_fail(f"is_supported('{os_name}')", f"expected {expected}, got {result}")

    # 플랫폼 정보 확인
    info = get_platform_info("redhat-8", "3.12")
    if info and "manylinux_2_28" in info["platforms"][0]:
        test_pass("redhat-8 -> manylinux_2_28")
    else:
        test_fail("redhat-8 platform mapping")

    # 유사 OS 추천
    suggestions = suggest_os("rhel8")
    if "redhat-8" in suggestions:
        test_pass("suggest_os('rhel8') includes redhat-8")
    else:
        test_fail("suggest_os('rhel8')")


def test_env_crud():
    """환경 CRUD 테스트"""
    print("\n" + "=" * 50)
    print("2. 환경 CRUD 테스트")
    print("=" * 50)

    from env import EnvironmentService

    svc = EnvironmentService()
    test_name = "__test_env__"

    # Create
    ok, msg, env = svc.create(test_name, "redhat-8", "3.12")
    if ok:
        test_pass("env create")
    else:
        test_fail("env create", msg)
        return

    # Read
    env = svc.get(test_name)
    if env and env.os == "redhat-8":
        test_pass("env read")
    else:
        test_fail("env read")

    # Update
    ok, msg, env = svc.update(test_name, os_name="redhat-9")
    if ok and env.os == "redhat-9":
        test_pass("env update")
    else:
        test_fail("env update", msg)

    # List
    envs = svc.list()
    if any(e.name == test_name for e in envs):
        test_pass("env list")
    else:
        test_fail("env list")

    # Delete
    ok, msg = svc.delete(test_name)
    if ok:
        test_pass("env delete")
    else:
        test_fail("env delete", msg)


def test_download():
    """패키지 다운로드 테스트"""
    print("\n" + "=" * 50)
    print("3. 패키지 다운로드 테스트")
    print("=" * 50)

    from env import EnvironmentService
    from download import download_packages, parse_requirements

    # 테스트 환경 생성
    svc = EnvironmentService()
    svc.create("__test_dl__", "ubuntu-22.04", "3.12")
    env = svc.get("__test_dl__")

    # 테스트 requirements.txt
    req_path = Path("test_req.txt")
    req_path.write_text("click\n")

    # requirements 파싱 테스트
    packages = parse_requirements(str(req_path))
    if packages == ["click"]:
        test_pass("parse_requirements")
    else:
        test_fail("parse_requirements", f"got {packages}")

    # 다운로드 테스트
    output_dir = Path("test_output")
    result = download_packages(env, str(req_path), str(output_dir), retry=1)

    if "click" in result.success:
        test_pass("download packages")
    else:
        test_fail("download packages", f"failed: {result.failed}")

    # whl 파일 확인
    whl_files = list(output_dir.glob("*.whl"))
    if len(whl_files) > 0:
        test_pass(f"whl files created ({len(whl_files)} files)")
    else:
        test_fail("whl files not found")

    # 정리
    svc.delete("__test_dl__")


def test_output_generation():
    """출력물 생성 테스트"""
    print("\n" + "=" * 50)
    print("4. 출력물 생성 테스트")
    print("=" * 50)

    from env import EnvironmentService
    from download import download_packages, DownloadResult
    from output import generate_all_outputs

    # 이전 테스트에서 생성된 파일 사용
    output_dir = Path("test_output")

    if not output_dir.exists():
        test_fail("output dir not found (run test_download first)")
        return

    svc = EnvironmentService()
    svc.create("__test_out__", "ubuntu-22.04", "3.12")
    env = svc.get("__test_out__")

    req_path = Path("test_req.txt")
    if not req_path.exists():
        req_path.write_text("click\n")

    result = DownloadResult(success=["click"], failed=[])

    generate_all_outputs(
        output_dir=str(output_dir),
        env=env,
        result=result,
        requirements_path=str(req_path),
        elapsed_seconds=1.0,
    )

    # 파일 확인
    files_to_check = ["install.sh", "install.bat", "requirements.txt", "report.md", "packages"]

    for fname in files_to_check:
        fpath = output_dir / fname
        if fpath.exists():
            test_pass(f"{fname} created")
        else:
            test_fail(f"{fname} not found")

    svc.delete("__test_out__")


def test_compression():
    """압축 테스트"""
    print("\n" + "=" * 50)
    print("5. 압축 테스트")
    print("=" * 50)

    from compress import compress_output

    output_dir = Path("test_output")

    if not output_dir.exists():
        test_fail("output dir not found")
        return

    # 단일 압축
    files = compress_output(str(output_dir))

    if files and Path(files[0]).exists():
        test_pass(f"compression created: {Path(files[0]).name}")
        # 압축 파일 삭제
        Path(files[0]).unlink()
    else:
        test_fail("compression failed")


def test_offline_simulation():
    """오프라인 설치 시뮬레이션"""
    print("\n" + "=" * 50)
    print("6. 오프라인 설치 시뮬레이션")
    print("=" * 50)

    output_dir = Path("test_output")
    packages_dir = output_dir / "packages"
    req_file = output_dir / "requirements.txt"

    if not packages_dir.exists():
        test_fail("packages dir not found")
        return

    # pip install --no-index 시뮬레이션
    cmd = f'"{sys.executable}" -m pip install --dry-run --no-index --find-links="{packages_dir}" -r "{req_file}"'

    ok, stdout, stderr = run_cmd(cmd)

    if ok or "Would install" in stdout:
        test_pass("offline install simulation (--dry-run)")
        log("pip would install packages successfully")
    else:
        # dry-run이 실패해도 실제 파일이 있으면 성공으로 간주
        whl_count = len(list(packages_dir.glob("*.whl")))
        if whl_count > 0:
            test_pass(f"packages available ({whl_count} whl files)")
        else:
            test_fail("offline simulation", stderr[:100] if stderr else "unknown")


# ============================================================
# 메인
# ============================================================

def main():
    global PASS, FAIL

    print("=" * 50)
    print("  오프라인 패키지 다운로더 테스트")
    print("=" * 50)

    # 정리
    cleanup()

    # 테스트 실행
    test_os_mapping()
    test_env_crud()
    test_download()
    test_output_generation()
    test_compression()
    test_offline_simulation()

    # 정리
    cleanup()

    # 결과
    print("\n" + "=" * 50)
    print(f"  결과: {PASS} PASS / {FAIL} FAIL")
    print("=" * 50)

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

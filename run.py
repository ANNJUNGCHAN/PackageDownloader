#!/usr/bin/env python3
"""
오프라인 패키지 다운로더 CLI
"""

import argparse
import sys

import time

from platform_map import print_os_list
from env import EnvironmentService
from download import download_packages
from output import generate_all_outputs
from compress import compress_output


def cmd_env_add(args):
    """환경 등록"""
    service = EnvironmentService()
    ok, msg, env = service.create(args.name, args.os, args.python)

    print(msg)
    if ok and env:
        print(f"  OS: {env.os}")
        print(f"  Python: {env.python}")
        print(f"  Platform: {env.platforms[0]}")


def cmd_env_list(args):
    """환경 목록"""
    service = EnvironmentService()
    envs = service.list()

    if not envs:
        print("등록된 환경이 없습니다.")
        return

    print(f"{'이름':<20} {'OS':<15} {'Python':<10} {'플랫폼'}")
    print("-" * 70)
    for env in envs:
        print(f"{env.name:<20} {env.os:<15} {env.python:<10} {env.platforms[0]}")


def cmd_env_show(args):
    """환경 상세"""
    service = EnvironmentService()
    env = service.get(args.name)

    if not env:
        print(f"환경 없음: {args.name}")
        return

    print(f"이름: {env.name}")
    print(f"OS: {env.os}")
    print(f"Python: {env.python}")
    print(f"플랫폼: {', '.join(env.platforms)}")
    print(f"ABI: {env.abi}")
    print(f"생성일: {env.created[:10]}")


def cmd_env_remove(args):
    """환경 삭제"""
    service = EnvironmentService()
    ok, msg = service.delete(args.name)
    print(msg)


def cmd_env_update(args):
    """환경 수정"""
    service = EnvironmentService()
    ok, msg, env = service.update(args.name, args.os, args.python)

    print(msg)
    if ok and env:
        print(f"  OS: {env.os}")
        print(f"  Python: {env.python}")
        print(f"  Platform: {env.platforms[0]}")


def cmd_os_list(args):
    """OS 목록"""
    print_os_list()


def cmd_download(args):
    """패키지 다운로드"""
    service = EnvironmentService()
    env = service.get(args.env)

    if not env:
        print(f"환경 없음: {args.env}")
        print("'python run.py env-list'로 등록된 환경을 확인하세요.")
        sys.exit(1)

    start_time = time.time()

    result = download_packages(
        env=env,
        requirements_path=args.requirements,
        output_dir=args.output,
        retry=args.retry,
    )

    elapsed = time.time() - start_time

    # 출력물 생성
    generate_all_outputs(
        output_dir=args.output,
        env=env,
        result=result,
        requirements_path=args.requirements,
        elapsed_seconds=elapsed,
    )

    # 압축 (옵션)
    if args.compress:
        compress_output(args.output, args.split)


def create_parser():
    """CLI 파서 생성"""
    parser = argparse.ArgumentParser(
        prog="pkgdown",
        description="오프라인 패키지 다운로더",
    )
    subs = parser.add_subparsers(dest="command", help="명령어")

    # env-add
    p = subs.add_parser("env-add", help="환경 등록")
    p.add_argument("name", help="환경 이름")
    p.add_argument("--os", required=True, help="OS (예: redhat-8)")
    p.add_argument("--python", required=True, help="Python 버전 (예: 3.12)")
    p.set_defaults(func=cmd_env_add)

    # env-list
    p = subs.add_parser("env-list", help="환경 목록")
    p.set_defaults(func=cmd_env_list)

    # env-show
    p = subs.add_parser("env-show", help="환경 상세")
    p.add_argument("name", help="환경 이름")
    p.set_defaults(func=cmd_env_show)

    # env-remove
    p = subs.add_parser("env-remove", help="환경 삭제")
    p.add_argument("name", help="환경 이름")
    p.set_defaults(func=cmd_env_remove)

    # env-update
    p = subs.add_parser("env-update", help="환경 수정")
    p.add_argument("name", help="환경 이름")
    p.add_argument("--os", help="새 OS (예: redhat-9)")
    p.add_argument("--python", help="새 Python 버전 (예: 3.11)")
    p.set_defaults(func=cmd_env_update)

    # os-list
    p = subs.add_parser("os-list", help="지원 OS 목록")
    p.set_defaults(func=cmd_os_list)

    # download
    p = subs.add_parser("download", help="패키지 다운로드")
    p.add_argument("env", help="환경 이름")
    p.add_argument("-r", "--requirements", default="./requirements.txt", help="requirements.txt 경로")
    p.add_argument("-o", "--output", default="./packages", help="출력 디렉토리")
    p.add_argument("--retry", type=int, default=2, help="재시도 횟수 (기본: 2)")
    p.add_argument("-c", "--compress", action="store_true", help="압축 파일 생성")
    p.add_argument("--split", type=int, default=None, help="분할 크기 MB (예: --split 200)")
    p.set_defaults(func=cmd_download)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()

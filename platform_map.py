"""
OS → 플랫폼 매핑 서비스
"""

from config import OS_PLATFORMS, OS_CATEGORIES, OS_KEYWORDS


def get_all_os() -> list[str]:
    """지원 OS 목록"""
    return list(OS_PLATFORMS.keys())


def is_supported(os_name: str) -> bool:
    """OS 지원 여부"""
    return os_name.lower() in OS_PLATFORMS


def get_platforms(os_name: str) -> list[str] | None:
    """OS → 플랫폼 태그"""
    return OS_PLATFORMS.get(os_name.lower())


def get_abi(python_version: str) -> str:
    """Python 버전 → ABI (3.12 → cp312)"""
    return f"cp{python_version.replace('.', '')}"


def get_platform_info(os_name: str, python_version: str) -> dict | None:
    """전체 플랫폼 정보"""
    platforms = get_platforms(os_name)
    if not platforms:
        return None

    return {
        "platforms": platforms,
        "abi": get_abi(python_version),
        "python_version": python_version.replace(".", ""),
    }


def suggest_os(input_os: str) -> list[str]:
    """유사 OS 추천"""
    input_lower = input_os.lower()

    for keyword, category in OS_KEYWORDS.items():
        if keyword in input_lower:
            if "arm" in input_lower and category == "macos":
                return OS_CATEGORIES.get("macos-arm", [])
            return OS_CATEGORIES.get(category, [])

    return get_all_os()


def print_os_list():
    """지원 OS 목록 출력"""
    print("\n[지원 OS 목록]")
    print("-" * 40)
    for category, os_list in OS_CATEGORIES.items():
        print(f"\n{category.upper()}:")
        for os_name in os_list:
            print(f"  {os_name}")

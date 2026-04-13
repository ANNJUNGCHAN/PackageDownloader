"""
OS 플랫폼 매핑 설정
"""

OS_PLATFORMS = {
    # RedHat 계열
    "redhat-7": ["manylinux2014_x86_64", "manylinux_2_17_x86_64"],
    "redhat-8": ["manylinux_2_28_x86_64", "manylinux2014_x86_64"],
    "redhat-9": ["manylinux_2_34_x86_64", "manylinux_2_28_x86_64"],
    "centos-7": ["manylinux2014_x86_64", "manylinux_2_17_x86_64"],
    "rocky-8": ["manylinux_2_28_x86_64", "manylinux2014_x86_64"],
    "rocky-9": ["manylinux_2_34_x86_64", "manylinux_2_28_x86_64"],

    # Debian 계열
    "ubuntu-18.04": ["manylinux_2_27_x86_64", "manylinux2014_x86_64"],
    "ubuntu-20.04": ["manylinux_2_31_x86_64", "manylinux_2_28_x86_64"],
    "ubuntu-22.04": ["manylinux_2_35_x86_64", "manylinux_2_28_x86_64"],
    "ubuntu-24.04": ["manylinux_2_39_x86_64", "manylinux_2_35_x86_64"],
    "debian-10": ["manylinux_2_28_x86_64", "manylinux2014_x86_64"],
    "debian-11": ["manylinux_2_31_x86_64", "manylinux_2_28_x86_64"],
    "debian-12": ["manylinux_2_36_x86_64", "manylinux_2_31_x86_64"],

    # Windows
    "windows-10": ["win_amd64"],
    "windows-11": ["win_amd64"],
    "windows-server-2019": ["win_amd64"],
    "windows-server-2022": ["win_amd64"],

    # macOS Intel
    "macos-12": ["macosx_12_0_x86_64", "macosx_11_0_x86_64"],
    "macos-13": ["macosx_13_0_x86_64", "macosx_12_0_x86_64"],
    "macos-14": ["macosx_14_0_x86_64", "macosx_13_0_x86_64"],

    # macOS ARM
    "macos-12-arm": ["macosx_12_0_arm64", "macosx_11_0_arm64"],
    "macos-13-arm": ["macosx_13_0_arm64", "macosx_12_0_arm64"],
    "macos-14-arm": ["macosx_14_0_arm64", "macosx_13_0_arm64"],
}

OS_CATEGORIES = {
    "redhat": ["redhat-7", "redhat-8", "redhat-9", "centos-7", "rocky-8", "rocky-9"],
    "debian": ["ubuntu-18.04", "ubuntu-20.04", "ubuntu-22.04", "ubuntu-24.04",
               "debian-10", "debian-11", "debian-12"],
    "windows": ["windows-10", "windows-11", "windows-server-2019", "windows-server-2022"],
    "macos": ["macos-12", "macos-13", "macos-14"],
    "macos-arm": ["macos-12-arm", "macos-13-arm", "macos-14-arm"],
}

OS_KEYWORDS = {
    "redhat": "redhat", "rhel": "redhat", "centos": "redhat", "rocky": "redhat", "alma": "redhat",
    "ubuntu": "debian", "debian": "debian", "mint": "debian",
    "win": "windows", "windows": "windows",
    "mac": "macos", "macos": "macos", "osx": "macos", "darwin": "macos",
}

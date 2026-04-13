# 지원 환경 목록

## 지원 OS

### RedHat 계열

| 입력값 | OS | glibc | 플랫폼 태그 |
|--------|-----|-------|------------|
| `redhat-7` | RHEL 7.x | 2.17 | manylinux2014_x86_64 |
| `redhat-8` | RHEL 8.x | 2.28 | manylinux_2_28_x86_64 |
| `redhat-9` | RHEL 9.x | 2.34 | manylinux_2_34_x86_64 |
| `centos-7` | CentOS 7.x | 2.17 | manylinux2014_x86_64 |
| `rocky-8` | Rocky Linux 8.x | 2.28 | manylinux_2_28_x86_64 |
| `rocky-9` | Rocky Linux 9.x | 2.34 | manylinux_2_34_x86_64 |

### Debian 계열

| 입력값 | OS | glibc | 플랫폼 태그 |
|--------|-----|-------|------------|
| `ubuntu-18.04` | Ubuntu 18.04 LTS | 2.27 | manylinux_2_27_x86_64 |
| `ubuntu-20.04` | Ubuntu 20.04 LTS | 2.31 | manylinux_2_31_x86_64 |
| `ubuntu-22.04` | Ubuntu 22.04 LTS | 2.35 | manylinux_2_35_x86_64 |
| `ubuntu-24.04` | Ubuntu 24.04 LTS | 2.39 | manylinux_2_39_x86_64 |
| `debian-10` | Debian 10 (Buster) | 2.28 | manylinux_2_28_x86_64 |
| `debian-11` | Debian 11 (Bullseye) | 2.31 | manylinux_2_31_x86_64 |
| `debian-12` | Debian 12 (Bookworm) | 2.36 | manylinux_2_36_x86_64 |

### Windows

| 입력값 | OS | 플랫폼 태그 |
|--------|-----|------------|
| `windows-10` | Windows 10 | win_amd64 |
| `windows-11` | Windows 11 | win_amd64 |
| `windows-server-2019` | Windows Server 2019 | win_amd64 |
| `windows-server-2022` | Windows Server 2022 | win_amd64 |

### macOS (Intel)

| 입력값 | OS | 플랫폼 태그 |
|--------|-----|------------|
| `macos-12` | macOS 12 Monterey | macosx_12_0_x86_64 |
| `macos-13` | macOS 13 Ventura | macosx_13_0_x86_64 |
| `macos-14` | macOS 14 Sonoma | macosx_14_0_x86_64 |

### macOS (Apple Silicon)

| 입력값 | OS | 플랫폼 태그 |
|--------|-----|------------|
| `macos-12-arm` | macOS 12 Monterey (M1/M2) | macosx_12_0_arm64 |
| `macos-13-arm` | macOS 13 Ventura (M1/M2) | macosx_13_0_arm64 |
| `macos-14-arm` | macOS 14 Sonoma (M1/M2/M3) | macosx_14_0_arm64 |

---

## 지원 Python 버전

| 버전 | ABI 태그 | 지원 상태 |
|------|---------|----------|
| 3.8 | cp38 | 지원 |
| 3.9 | cp39 | 지원 |
| 3.10 | cp310 | 지원 |
| 3.11 | cp311 | 지원 |
| 3.12 | cp312 | 지원 |

---

## 플랫폼 태그 설명

### manylinux 태그

Linux 패키지는 glibc 버전에 따라 호환성이 결정됩니다.

- `manylinux2014`: glibc 2.17 이상 (CentOS 7 기준)
- `manylinux_2_28`: glibc 2.28 이상 (RHEL 8 기준)
- `manylinux_2_31`: glibc 2.31 이상 (Ubuntu 20.04 기준)

**하위 호환성**: 높은 glibc 버전용 패키지는 낮은 버전 시스템에서 실행되지 않습니다.

예시:
- `manylinux_2_28` 패키지 → RHEL 7에서 실행 불가
- `manylinux2014` 패키지 → RHEL 8에서 실행 가능

### Windows 태그

- `win_amd64`: 64비트 Windows

### macOS 태그

- `macosx_X_Y_x86_64`: Intel Mac (x86_64)
- `macosx_X_Y_arm64`: Apple Silicon (M1/M2/M3)

---

## 플랫폼 태그 우선순위

도구는 여러 플랫폼 태그를 시도합니다. 일부 패키지는 특정 태그로만 배포되기 때문입니다.

예시 (redhat-8):
1. `manylinux_2_28_x86_64` (우선)
2. `manylinux2014_x86_64` (대체)

---

## OS 버전 선택 팁

### 정확한 버전을 모를 때

- **RHEL 8.x 계열** (8.0, 8.1, 8.2, ...) → `redhat-8` 사용
- **Ubuntu LTS** → 해당 LTS 버전 사용 (예: 22.04)
- **최신 버전이 목록에 없을 때** → 가장 가까운 낮은 버전 사용

### 호환성 우선

확실하지 않다면 낮은 glibc 버전을 선택하세요. 하위 호환성이 보장됩니다.

예시:
- RHEL 8.7 서버 → `redhat-8` (권장) 또는 `centos-7` (더 안전)

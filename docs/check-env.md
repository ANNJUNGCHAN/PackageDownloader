# 환경 확인 방법

패키지를 다운로드하기 전에, 폐쇄망 서버의 OS 버전과 Python 버전을 확인해야 합니다.

## Linux

### OS 버전 확인

```bash
# 방법 1: 대부분의 Linux 배포판
cat /etc/os-release
```

출력 예시:
```
NAME="Red Hat Enterprise Linux"
VERSION="8.2 (Ootpa)"
ID="rhel"
VERSION_ID="8.2"
```

```bash
# 방법 2: RedHat/CentOS 계열
cat /etc/redhat-release
```

출력 예시:
```
Red Hat Enterprise Linux release 8.2 (Ootpa)
```

```bash
# 방법 3: Ubuntu/Debian 계열
lsb_release -a
```

출력 예시:
```
Distributor ID: Ubuntu
Description:    Ubuntu 22.04.1 LTS
Release:        22.04
```

### 도구 입력값 매핑

| 확인 결과 | 입력값 |
|----------|--------|
| Red Hat 8.x | `redhat-8` |
| Red Hat 9.x | `redhat-9` |
| CentOS 7.x | `centos-7` |
| Rocky Linux 8.x | `rocky-8` |
| Rocky Linux 9.x | `rocky-9` |
| Ubuntu 20.04 | `ubuntu-20.04` |
| Ubuntu 22.04 | `ubuntu-22.04` |
| Debian 11 | `debian-11` |
| Debian 12 | `debian-12` |

---

## Windows

### OS 버전 확인

```cmd
# 방법 1: GUI
winver
```

또는

```cmd
# 방법 2: 명령 프롬프트
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
```

출력 예시:
```
OS Name:        Microsoft Windows 11 Pro
OS Version:     10.0.22621
```

### 도구 입력값 매핑

| 확인 결과 | 입력값 |
|----------|--------|
| Windows 10 | `windows-10` |
| Windows 11 | `windows-11` |
| Windows Server 2019 | `windows-server-2019` |
| Windows Server 2022 | `windows-server-2022` |

---

## macOS

### OS 버전 확인

```bash
sw_vers
```

출력 예시:
```
ProductName:    macOS
ProductVersion: 14.0
BuildVersion:   23A344
```

### 아키텍처 확인 (Intel vs Apple Silicon)

```bash
uname -m
```

| 결과 | 의미 |
|-----|------|
| `x86_64` | Intel Mac |
| `arm64` | Apple Silicon (M1/M2/M3) |

### 도구 입력값 매핑

| 확인 결과 | 입력값 |
|----------|--------|
| macOS 12 + Intel | `macos-12` |
| macOS 13 + Intel | `macos-13` |
| macOS 14 + Intel | `macos-14` |
| macOS 12 + Apple Silicon | `macos-12-arm` |
| macOS 13 + Apple Silicon | `macos-13-arm` |
| macOS 14 + Apple Silicon | `macos-14-arm` |

---

## Python 버전 확인

```bash
# Linux/macOS
python3 --version

# 또는
python --version
```

출력 예시:
```
Python 3.12.0
```

입력값: `3.12` (마이너 버전까지만)

---

## 아키텍처 확인

### Linux/macOS

```bash
uname -m
```

| 결과 | 의미 |
|-----|------|
| `x86_64` | 64비트 Intel/AMD |
| `aarch64` 또는 `arm64` | 64비트 ARM |

### Windows

```cmd
echo %PROCESSOR_ARCHITECTURE%
```

| 결과 | 의미 |
|-----|------|
| `AMD64` | 64비트 |

---

## 예시: 환경 등록

폐쇄망 서버에서 확인한 결과:
- OS: Red Hat Enterprise Linux 8.5
- Python: 3.12.0
- 아키텍처: x86_64

도구에 환경 등록:
```bash
python run.py env-add prod-server --os redhat-8 --python 3.12
```

> **참고**: 마이너 버전(8.5의 .5)은 무시하고 메이저 버전만 입력합니다.

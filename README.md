# 오프라인 패키지 다운로더 (pkgdown)

폐쇄망 환경을 위한 Python 패키지 다운로드 도구입니다.

## 이런 분들을 위한 도구입니다

- 인터넷이 안 되는 서버에 Python 패키지를 설치해야 하는 경우
- 여러 폐쇄망 환경에 동일한 패키지를 배포해야 하는 경우
- pip download 명령어의 복잡한 옵션을 매번 입력하기 번거로운 경우

## 주요 기능

- **OS 자동 매핑**: "redhat-8", "ubuntu-22.04" 같은 익숙한 이름만 입력하면 pip 플랫폼 태그 자동 변환
- **환경 저장**: 한 번 등록한 환경 설정을 재사용
- **의존성 자동 해결**: 하위 패키지까지 모두 다운로드
- **설치 스크립트 생성**: 폐쇄망에서 바로 실행 가능한 install.sh / install.bat 자동 생성
- **압축 지원**: 결과물을 zip으로 압축, 대용량 시 분할 압축

## 빠른 시작

### 1. 환경 등록

폐쇄망 서버의 OS와 Python 버전을 등록합니다.

```bash
python run.py env-add my-server --os redhat-8 --python 3.12
```

### 2. requirements.txt 작성

설치할 패키지 목록을 작성합니다.

```
requests
pandas
numpy
```

### 3. 패키지 다운로드

```bash
python run.py download my-server -r requirements.txt -o ./output
```

### 4. 결과물 확인

```
output/
├── packages/           # 패키지 파일들 (.whl)
├── install.sh          # Linux 설치 스크립트
├── install.bat         # Windows 설치 스크립트
├── requirements.txt    # 패키지 목록
└── report.md           # 다운로드 리포트
```

### 5. 폐쇄망에서 설치

결과물을 폐쇄망 서버로 복사한 후:

```bash
# Linux
./install.sh

# Windows
install.bat
```

## CLI 명령어

| 명령어 | 설명 |
|--------|------|
| `env-add` | 환경 등록 |
| `env-list` | 환경 목록 |
| `env-show` | 환경 상세 |
| `env-update` | 환경 수정 |
| `env-remove` | 환경 삭제 |
| `os-list` | 지원 OS 목록 |
| `download` | 패키지 다운로드 |

## 지원 환경

| OS | 버전 |
|----|------|
| RedHat/CentOS/Rocky | 7, 8, 9 |
| Ubuntu | 18.04, 20.04, 22.04, 24.04 |
| Debian | 10, 11, 12 |
| Windows | 10, 11, Server 2019/2022 |
| macOS | 12, 13, 14 (Intel/ARM) |

Python: 3.8 ~ 3.12

## 상세 문서

- [환경 확인 방법](docs/check-env.md) - OS, Python 버전 확인하는 방법
- [사용법 가이드](docs/usage.md) - CLI 명령어 상세 설명
- [폐쇄망 설치 가이드](docs/installation.md) - 폐쇄망에서 설치하는 방법
- [지원 환경 목록](docs/supported-os.md) - 지원 OS 및 플랫폼 태그
- [문제 해결](docs/troubleshooting.md) - FAQ 및 오류 해결

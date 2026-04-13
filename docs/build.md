# 빌드 및 배포 가이드

## 개요

이 문서는 오프라인 패키지 다운로더를 exe 파일로 빌드하고 배포하는 방법을 설명합니다.

---

## 사전 요구사항

### 필수 패키지 설치

```bash
pip install PyQt6 pyinstaller
```

---

## exe 파일 빌드

### 방법 1: spec 파일 사용 (권장)

```bash
pyinstaller --clean pkgdown.spec
```

### 방법 2: 직접 명령어 실행

```bash
pyinstaller --onefile --noconsole --name PkgDown ui.py
```

### 빌드 옵션 설명

| 옵션 | 설명 |
|------|------|
| `--onefile` | 단일 exe 파일로 생성 |
| `--noconsole` | 콘솔 창 숨김 (GUI 앱용) |
| `--name` | 출력 파일명 지정 |
| `--clean` | 이전 빌드 캐시 삭제 |

---

## 빌드 결과

빌드 완료 후 생성되는 파일:

```
packages/
├── dist/
│   └── PkgDown.exe    # 배포용 exe 파일
├── build/             # 빌드 임시 파일 (삭제 가능)
└── pkgdown.spec       # 빌드 설정 파일
```

### 파일 크기

- 약 35~40 MB (PyQt6 포함)

---

## 배포

### 단일 exe 배포

`dist/PkgDown.exe` 파일만 배포하면 됩니다.

사용자는 별도 설치 없이 exe 파일을 실행하여 프로그램을 사용할 수 있습니다.

### 배포 시 포함할 파일

| 파일 | 필수 | 설명 |
|------|-----|------|
| `PkgDown.exe` | O | 실행 파일 |
| `README.md` | X | 사용 설명서 (선택) |

---

## 실행 환경

### 지원 OS

- Windows 10 이상
- Windows Server 2019 이상

### 요구사항

- 인터넷 연결 (패키지 다운로드 시)
- 디스크 공간 (다운로드할 패키지 용량에 따라)

---

## 문제 해결

### exe 실행 시 바이러스 경고

일부 백신 프로그램이 PyInstaller로 만든 exe를 오탐지할 수 있습니다.

해결 방법:
1. 백신 프로그램에서 예외 등록
2. 코드 서명 인증서 적용 (유료)

### exe 실행이 느림

첫 실행 시 임시 폴더에 파일을 풀기 때문에 약간의 시간이 소요됩니다.

두 번째 실행부터는 빠르게 시작됩니다.

### 빌드 실패 시

```bash
# 캐시 삭제 후 재빌드
pyinstaller --clean pkgdown.spec

# 또는 수동으로 삭제
rm -rf build/ dist/ __pycache__/
```

---

## spec 파일 커스터마이징

### 아이콘 추가

```python
exe = EXE(
    ...
    icon='icon.ico',  # 아이콘 파일 경로
    ...
)
```

### 버전 정보 추가

```python
exe = EXE(
    ...
    version='version.txt',  # 버전 정보 파일
    ...
)
```

---

## 참고

- [PyInstaller 공식 문서](https://pyinstaller.org/)
- [PyQt6 공식 문서](https://www.riverbankcomputing.com/software/pyqt/)

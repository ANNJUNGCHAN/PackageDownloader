# 폐쇄망 설치 가이드

이 문서는 다운로드한 패키지를 폐쇄망 서버에 설치하는 방법을 설명합니다.

## 다운로드 결과물 구조

패키지 다운로드 후 생성되는 파일:

```
output/
├── packages/           # 패키지 파일들 (.whl)
│   ├── requests-2.31.0-py3-none-any.whl
│   ├── urllib3-2.0.4-py3-none-any.whl
│   └── ...
├── install.sh          # Linux 설치 스크립트
├── install.bat         # Windows 설치 스크립트
├── requirements.txt    # 패키지 목록
└── report.md           # 다운로드 리포트
```

### 각 파일 설명

| 파일 | 설명 |
|------|------|
| `packages/` | pip 패키지 파일(.whl)이 저장된 폴더 |
| `install.sh` | Linux/macOS에서 실행하는 설치 스크립트 |
| `install.bat` | Windows에서 실행하는 설치 스크립트 |
| `requirements.txt` | 설치할 패키지 목록 |
| `report.md` | 다운로드 결과 리포트 (성공/실패 목록, 용량 등) |

---

## 폐쇄망으로 파일 이동

### 방법 1: USB 드라이브 사용

1. 결과물 폴더 전체를 USB에 복사
2. 폐쇄망 서버에 USB 연결
3. 서버의 원하는 위치에 복사

### 방법 2: 압축 파일 사용

다운로드 시 `--compress` 옵션을 사용하면 zip 파일이 생성됩니다.

```bash
# 단일 압축
python run.py download my-server --compress

# 200MB 단위 분할 압축 (대용량인 경우)
python run.py download my-server --compress --split 200
```

생성되는 파일:
- 단일 압축: `output_20240115_120000.zip`
- 분할 압축: `output_20240115_120000.zip`, `output_20240115_120000.z01`, `output_20240115_120000.z02`, ...

### 방법 3: 네트워크 전송 (허용된 경우)

scp, sftp 등을 사용할 수 있는 경우:

```bash
scp -r ./output user@server:/path/to/destination
```

---

## 폐쇄망에서 설치

### Linux/macOS

```bash
# 1. 결과물 폴더로 이동
cd /path/to/output

# 2. 설치 스크립트 실행 권한 부여
chmod +x install.sh

# 3. 설치 실행
./install.sh
```

또는 직접 pip 명령 실행:

```bash
pip install --no-index --find-links="./packages" -r requirements.txt
```

### Windows

```cmd
# 1. 결과물 폴더로 이동
cd C:\path\to\output

# 2. 설치 스크립트 실행
install.bat
```

또는 직접 pip 명령 실행:

```cmd
pip install --no-index --find-links=".\packages" -r requirements.txt
```

---

## 가상환경에 설치

기존 환경에 영향을 주지 않으려면 가상환경을 사용합니다.

### Linux/macOS

```bash
# 1. 가상환경 생성
python3 -m venv myenv

# 2. 가상환경 활성화
source myenv/bin/activate

# 3. 패키지 설치
cd /path/to/output
./install.sh

# 4. 사용 후 비활성화
deactivate
```

### Windows

```cmd
# 1. 가상환경 생성
python -m venv myenv

# 2. 가상환경 활성화
myenv\Scripts\activate

# 3. 패키지 설치
cd C:\path\to\output
install.bat

# 4. 사용 후 비활성화
deactivate
```

---

## 설치 확인

### 설치된 패키지 목록 확인

```bash
pip list
```

### 특정 패키지 확인

```bash
pip show requests
```

### import 테스트

```bash
python -c "import requests; print(requests.__version__)"
```

---

## 문제 해결

### "No matching distribution found" 오류

원인: 플랫폼이 맞지 않는 패키지

해결:
1. 폐쇄망 서버의 OS와 Python 버전 재확인
2. 올바른 환경으로 패키지 다시 다운로드

### "Could not find a version that satisfies the requirement" 오류

원인: 의존성 패키지 누락

해결:
1. `report.md`에서 실패한 패키지 확인
2. 해당 패키지를 requirements.txt에 직접 추가 후 재다운로드

### 설치는 되었으나 import 오류

원인: 해당 패키지가 pure Python이 아니고, 다른 플랫폼용 바이너리인 경우

해결:
1. 아키텍처 확인 (`uname -m`)
2. 올바른 플랫폼으로 환경 재등록 후 다운로드

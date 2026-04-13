# 문제 해결

## 자주 발생하는 오류

### 1. "지원하지 않는 OS" 오류

```
지원하지 않는 OS: rhel8
추천: redhat-7, redhat-8, redhat-9, centos-7, rocky-8
```

**원인**: 입력한 OS 이름이 정확하지 않음

**해결**:
```bash
# 지원 OS 목록 확인
python run.py os-list

# 정확한 이름으로 입력
python run.py env-add my-server --os redhat-8 --python 3.12
```

---

### 2. "환경 없음" 오류

```
환경 없음: my-server
```

**원인**: 등록되지 않은 환경 이름 사용

**해결**:
```bash
# 등록된 환경 확인
python run.py env-list

# 환경 등록
python run.py env-add my-server --os redhat-8 --python 3.12
```

---

### 3. "파일 없음" 오류 (requirements.txt)

```
파일 없음: ./requirements.txt
```

**원인**: requirements.txt 파일이 없거나 경로가 잘못됨

**해결**:
```bash
# 파일 생성
echo "requests" > requirements.txt

# 또는 경로 지정
python run.py download my-server -r /path/to/requirements.txt
```

---

### 4. 패키지 다운로드 실패

```
[1단계] 개별 패키지 다운로드...
  (1/3) some-package 재시도(1)... 재시도(2)... FAIL
```

**원인**:
- 패키지가 해당 플랫폼을 지원하지 않음
- 패키지 이름 오타
- 네트워크 문제

**해결**:
1. 패키지 이름 확인 (PyPI에서 검색)
2. 해당 패키지가 플랫폼을 지원하는지 확인
3. 재시도 횟수 증가: `--retry 5`

---

### 5. 폐쇄망에서 "No matching distribution found"

```
ERROR: No matching distribution found for requests
```

**원인**: 다운로드한 패키지의 플랫폼이 서버와 맞지 않음

**해결**:
1. 폐쇄망 서버의 OS 버전 재확인
   ```bash
   cat /etc/os-release
   python3 --version
   uname -m
   ```
2. 올바른 환경으로 패키지 재다운로드

---

### 6. 폐쇄망에서 의존성 오류

```
ERROR: Could not find a version that satisfies the requirement urllib3
```

**원인**: 의존성 패키지가 누락됨

**해결**:
1. `report.md`에서 다운로드된 패키지 목록 확인
2. 누락된 패키지를 requirements.txt에 추가
3. 재다운로드

---

### 7. import 오류 (설치 후)

```python
>>> import numpy
ImportError: libopenblas.so.0: cannot open shared object file
```

**원인**: 시스템 라이브러리 누락 (C 확장 패키지의 경우)

**해결**:
- 시스템 관리자에게 필요한 라이브러리 설치 요청
- 또는 pure Python 대체 패키지 사용

---

## FAQ

### Q: 환경 설정은 어디에 저장되나요?

A: `~/.pkgdown/environments.json` 파일에 저장됩니다.

```bash
# Linux/macOS
cat ~/.pkgdown/environments.json

# Windows
type %USERPROFILE%\.pkgdown\environments.json
```

---

### Q: 이미 다운로드한 패키지를 다시 받지 않으려면?

A: pip이 자동으로 중복 파일을 스킵합니다. 같은 출력 폴더를 사용하면 됩니다.

---

### Q: 특정 버전의 패키지를 받으려면?

A: requirements.txt에 버전을 명시합니다.

```
requests==2.31.0
pandas>=2.0.0,<3.0.0
numpy~=1.24.0
```

---

### Q: 여러 환경용 패키지를 한 번에 받으려면?

A: 각 환경별로 따로 다운로드해야 합니다. 플랫폼별로 바이너리가 다르기 때문입니다.

```bash
python run.py download server-linux -o ./output-linux
python run.py download server-windows -o ./output-windows
```

---

### Q: 프록시 환경에서 사용하려면?

A: 환경 변수를 설정합니다.

```bash
# Linux/macOS
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080

# Windows
set HTTP_PROXY=http://proxy:8080
set HTTPS_PROXY=http://proxy:8080
```

---

### Q: 다운로드 속도가 느려요

A: pip의 기본 동작입니다. 패키지가 많으면 시간이 걸릴 수 있습니다.

진행 상황은 화면에 표시됩니다:
```
[1단계] 개별 패키지 다운로드...
  (1/50) requests OK
  (2/50) pandas OK
  ...
```

---

### Q: 지원하지 않는 OS를 사용해야 해요

A: 가장 가까운 OS를 선택하세요.

예시:
- AlmaLinux 8 → `rocky-8` 또는 `redhat-8`
- Oracle Linux 8 → `redhat-8`
- Linux Mint → `ubuntu-22.04` (기반 버전에 따라)

---

## 추가 도움

문제가 해결되지 않으면:
1. `report.md` 파일 내용 확인
2. 에러 메시지 전체 복사
3. OS, Python 버전 정보와 함께 문의

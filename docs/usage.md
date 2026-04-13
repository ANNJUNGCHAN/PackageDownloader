# 사용법 가이드

## 명령어 목록

```bash
python run.py <명령어> [옵션]
```

| 명령어 | 설명 |
|--------|------|
| `env-add` | 환경 등록 |
| `env-list` | 환경 목록 조회 |
| `env-show` | 환경 상세 조회 |
| `env-update` | 환경 수정 |
| `env-remove` | 환경 삭제 |
| `os-list` | 지원 OS 목록 |
| `download` | 패키지 다운로드 |

---

## env-add (환경 등록)

새로운 환경을 등록합니다.

```bash
python run.py env-add <환경이름> --os <OS> --python <버전>
```

### 옵션

| 옵션 | 필수 | 설명 | 예시 |
|------|-----|------|------|
| `<환경이름>` | O | 환경 식별자 (영문, 숫자, -, _) | `prod-server` |
| `--os` | O | 대상 OS | `redhat-8` |
| `--python` | O | Python 버전 | `3.12` |

### 예시

```bash
# RedHat 8 서버용 환경 등록
python run.py env-add prod-server --os redhat-8 --python 3.12

# Ubuntu 22.04 개발 환경 등록
python run.py env-add dev-ubuntu --os ubuntu-22.04 --python 3.11

# Windows 11 환경 등록
python run.py env-add my-windows --os windows-11 --python 3.12
```

---

## env-list (환경 목록)

등록된 모든 환경을 조회합니다.

```bash
python run.py env-list
```

### 출력 예시

```
이름                 OS              Python     플랫폼
----------------------------------------------------------------------
prod-server          redhat-8        3.12       manylinux_2_28_x86_64
dev-ubuntu           ubuntu-22.04    3.11       manylinux_2_35_x86_64
```

---

## env-show (환경 상세)

특정 환경의 상세 정보를 조회합니다.

```bash
python run.py env-show <환경이름>
```

### 예시

```bash
python run.py env-show prod-server
```

### 출력 예시

```
이름: prod-server
OS: redhat-8
Python: 3.12
플랫폼: manylinux_2_28_x86_64, manylinux2014_x86_64
ABI: cp312
생성일: 2024-01-15
```

---

## env-update (환경 수정)

등록된 환경의 설정을 수정합니다.

```bash
python run.py env-update <환경이름> [--os <OS>] [--python <버전>]
```

### 옵션

| 옵션 | 필수 | 설명 |
|------|-----|------|
| `--os` | X | 새 OS |
| `--python` | X | 새 Python 버전 |

### 예시

```bash
# OS만 변경
python run.py env-update prod-server --os redhat-9

# Python 버전만 변경
python run.py env-update prod-server --python 3.11

# 둘 다 변경
python run.py env-update prod-server --os redhat-9 --python 3.11
```

---

## env-remove (환경 삭제)

등록된 환경을 삭제합니다.

```bash
python run.py env-remove <환경이름>
```

### 예시

```bash
python run.py env-remove prod-server
```

---

## os-list (지원 OS 목록)

도구가 지원하는 OS 목록을 표시합니다.

```bash
python run.py os-list
```

### 출력 예시

```
[지원 OS 목록]
----------------------------------------

REDHAT:
  redhat-7
  redhat-8
  redhat-9
  centos-7
  rocky-8
  rocky-9

DEBIAN:
  ubuntu-18.04
  ubuntu-20.04
  ubuntu-22.04
  ubuntu-24.04
  ...
```

---

## download (패키지 다운로드)

등록된 환경에 맞는 패키지를 다운로드합니다.

```bash
python run.py download <환경이름> [옵션]
```

### 옵션

| 옵션 | 필수 | 기본값 | 설명 |
|------|-----|--------|------|
| `<환경이름>` | O | - | 등록된 환경 이름 |
| `-r`, `--requirements` | X | `./requirements.txt` | 패키지 목록 파일 |
| `-o`, `--output` | X | `./packages` | 출력 디렉토리 |
| `--retry` | X | `2` | 실패 시 재시도 횟수 |
| `-c`, `--compress` | X | - | 압축 파일 생성 |
| `--split` | X | - | 분할 압축 크기 (MB) |

### 예시

```bash
# 기본 사용
python run.py download prod-server

# requirements.txt 경로 지정
python run.py download prod-server -r ./my_requirements.txt

# 출력 디렉토리 지정
python run.py download prod-server -o ./my_output

# 압축 파일 생성
python run.py download prod-server --compress

# 200MB 단위로 분할 압축
python run.py download prod-server --compress --split 200

# 전체 옵션 사용
python run.py download prod-server \
    -r requirements.txt \
    -o ./output \
    --retry 3 \
    --compress \
    --split 200
```

---

## 전체 워크플로우 예시

```bash
# 1. 지원 OS 확인
python run.py os-list

# 2. 환경 등록
python run.py env-add my-server --os redhat-8 --python 3.12

# 3. 환경 확인
python run.py env-list

# 4. requirements.txt 작성
echo "requests" > requirements.txt
echo "pandas" >> requirements.txt

# 5. 패키지 다운로드
python run.py download my-server -r requirements.txt -o ./output --compress

# 6. 결과물 확인
ls -la ./output/
```

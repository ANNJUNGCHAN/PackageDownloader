"""
환경 관리 서비스
"""

import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional

from platform_map import is_supported, get_platform_info, suggest_os


CONFIG_DIR = Path.home() / ".pkgdown"
CONFIG_FILE = CONFIG_DIR / "environments.json"


@dataclass
class Environment:
    """환경 데이터"""
    name: str
    os: str
    python: str
    platforms: list[str]
    abi: str
    created: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Environment":
        return cls(**data)


class EnvironmentStore:
    """환경 저장소"""

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> dict[str, Environment]:
        if not CONFIG_FILE.exists():
            return {}
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {name: Environment.from_dict(env) for name, env in data.items()}

    def save_all(self, envs: dict[str, Environment]):
        data = {name: env.to_dict() for name, env in envs.items()}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get(self, name: str) -> Optional[Environment]:
        return self.load_all().get(name)

    def exists(self, name: str) -> bool:
        return self.get(name) is not None

    def save(self, env: Environment):
        envs = self.load_all()
        envs[env.name] = env
        self.save_all(envs)

    def delete(self, name: str) -> bool:
        envs = self.load_all()
        if name not in envs:
            return False
        del envs[name]
        self.save_all(envs)
        return True


class EnvironmentService:
    """환경 관리 서비스"""

    def __init__(self):
        self.store = EnvironmentStore()

    def create(self, name: str, os_name: str, python_version: str) -> tuple[bool, str, Optional[Environment]]:
        """환경 생성"""
        # 검증
        if error := self._validate_name(name):
            return False, error, None
        if self.store.exists(name):
            return False, f"이미 존재하는 환경: {name}", None
        if not is_supported(os_name):
            suggestions = suggest_os(os_name)[:5]
            return False, f"지원하지 않는 OS: {os_name}\n추천: {', '.join(suggestions)}", None
        if error := self._validate_python(python_version):
            return False, error, None

        # 생성
        info = get_platform_info(os_name, python_version)
        env = Environment(
            name=name,
            os=os_name.lower(),
            python=python_version,
            platforms=info["platforms"],
            abi=info["abi"],
            created=datetime.now().isoformat(),
        )
        self.store.save(env)
        return True, f"환경 '{name}' 등록 완료", env

    def list(self) -> list[Environment]:
        """환경 목록"""
        return list(self.store.load_all().values())

    def get(self, name: str) -> Optional[Environment]:
        """환경 조회"""
        return self.store.get(name)

    def delete(self, name: str) -> tuple[bool, str]:
        """환경 삭제"""
        if self.store.delete(name):
            return True, f"환경 '{name}' 삭제 완료"
        return False, f"환경 없음: {name}"

    def update(self, name: str, os_name: str = None, python_version: str = None) -> tuple[bool, str, Optional[Environment]]:
        """환경 수정"""
        env = self.store.get(name)
        if not env:
            return False, f"환경 없음: {name}", None

        # OS 변경
        new_os = os_name if os_name else env.os
        if os_name and not is_supported(os_name):
            suggestions = suggest_os(os_name)[:5]
            return False, f"지원하지 않는 OS: {os_name}\n추천: {', '.join(suggestions)}", None

        # Python 버전 변경
        new_python = python_version if python_version else env.python
        if python_version:
            if error := self._validate_python(python_version):
                return False, error, None

        # 플랫폼 정보 재계산
        info = get_platform_info(new_os, new_python)
        env.os = new_os.lower()
        env.python = new_python
        env.platforms = info["platforms"]
        env.abi = info["abi"]

        self.store.save(env)
        return True, f"환경 '{name}' 수정 완료", env

    def _validate_name(self, name: str) -> Optional[str]:
        if not name:
            return "환경 이름을 입력하세요"
        if len(name) > 50:
            return "환경 이름은 50자 이하"
        if not re.match(r"^[a-zA-Z0-9가-힣_\- ]+$", name):
            return "환경 이름은 영문, 숫자, 한글, 공백, -, _ 만 가능"
        return None

    def _validate_python(self, version: str) -> Optional[str]:
        if not re.match(r"^3\.(1[0-9]|[8-9])$", version):
            return "Python 버전: 3.8 ~ 3.19 (예: 3.12)"
        return None

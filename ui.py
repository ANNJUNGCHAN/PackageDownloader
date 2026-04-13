"""오프라인 패키지 다운로더 - PyQt UI"""
import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QStatusBar, QComboBox, QPushButton, QGroupBox, QMessageBox,
    QDialog, QLineEdit, QRadioButton, QButtonGroup, QFormLayout, QDialogButtonBox,
    QTextEdit, QFileDialog, QCheckBox, QSpinBox, QProgressBar, QListWidget,
    QListWidgetItem, QMenuBar, QMenu, QTextBrowser
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from pathlib import Path
import time

from env import EnvironmentService, Environment
from config import OS_CATEGORIES
from platform_map import get_platform_info
from download import download_packages_with_callback
from output import generate_outputs
from compress import compress_output


# OS 카테고리 표시명
OS_CATEGORY_NAMES = {
    "redhat": "RedHat 계열",
    "debian": "Ubuntu/Debian 계열",
    "windows": "Windows",
    "macos": "macOS (Intel)",
    "macos-arm": "macOS (Apple Silicon)",
}

# Python 버전 목록
PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]


class DownloadWorker(QThread):
    """다운로드 작업 스레드"""

    # 시그널 정의
    progress = pyqtSignal(int, int, str, str)  # current, total, package, status
    message = pyqtSignal(str)
    finished = pyqtSignal(dict)  # result dict

    def __init__(self, env, packages, output_dir, compress=False, split_size=0):
        super().__init__()
        self.env = env
        self.packages = packages
        self.output_dir = output_dir
        self.compress = compress
        self.split_size = split_size
        self._cancel = False

    def run(self):
        """다운로드 실행"""
        start_time = time.time()

        # 다운로드 실행
        result = download_packages_with_callback(
            env=self.env,
            packages=self.packages,
            output_dir=str(Path(self.output_dir) / "packages"),
            on_progress=lambda c, t, p, s: self.progress.emit(c, t, p, s),
            on_message=lambda m: self.message.emit(m),
            should_cancel=lambda: self._cancel
        )

        if self._cancel:
            self.finished.emit({"cancelled": True})
            return

        # 출력 파일 생성
        self.message.emit("설치 스크립트 생성 중...")
        generate_outputs(self.output_dir, self.packages)

        # 총 용량 계산
        pkg_dir = Path(self.output_dir) / "packages"
        whl_files = list(pkg_dir.glob("*.whl")) if pkg_dir.exists() else []
        total_size = sum(f.stat().st_size for f in whl_files)
        size_str = f"{total_size / 1024 / 1024:.1f} MB"

        elapsed = time.time() - start_time
        elapsed_str = f"{elapsed:.1f}초"

        # 리포트 생성
        self.message.emit("리포트 생성 중...")
        self.generate_report(result, whl_files, total_size, elapsed)

        # 압축 처리
        if self.compress:
            self.message.emit("압축 파일 생성 중...")
            compress_output(self.output_dir, split_size_mb=self.split_size if self.split_size > 0 else None)

        # 결과 반환
        self.finished.emit({
            "success": len(result.success),
            "fail": len(result.failed),
            "total_size": size_str,
            "elapsed": elapsed_str,
            "output_path": self.output_dir,
            "failed_list": result.failed,
        })

    def generate_report(self, result, whl_files, total_size, elapsed):
        """리포트 파일 생성"""
        from datetime import datetime

        def format_size(bytes):
            if bytes < 1024:
                return f"{bytes} B"
            elif bytes < 1024 * 1024:
                return f"{bytes / 1024:.1f} KB"
            else:
                return f"{bytes / (1024 * 1024):.1f} MB"

        report = f"""# 패키지 다운로드 리포트

## 환경 정보
- 환경 이름: {self.env.name}
- OS: {self.env.os}
- Python: {self.env.python}
- 플랫폼: {self.env.platforms[0]}

## 다운로드 결과
- 생성 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 소요 시간: {elapsed:.1f}초
- 총 패키지: {len(whl_files)}개
- 총 용량: {format_size(total_size)}

## 성공 ({len(result.success)}개)
"""
        for pkg in result.success:
            report += f"- {pkg}\n"

        if result.failed:
            report += f"\n## 실패 ({len(result.failed)}개)\n"
            for pkg, err in result.failed:
                report += f"- {pkg}: {err}\n"

        report += f"\n## 다운로드된 파일 ({len(whl_files)}개)\n"
        for f in sorted(whl_files, key=lambda x: x.name):
            report += f"- {f.name} ({format_size(f.stat().st_size)})\n"

        # 파일로 저장
        report_path = Path(self.output_dir) / "report.md"
        report_path.write_text(report, encoding="utf-8")

    def cancel(self):
        """다운로드 취소"""
        self._cancel = True


class EnvDialog(QDialog):
    """환경 등록/편집 다이얼로그"""

    def __init__(self, parent=None, edit_env=None):
        super().__init__(parent)
        self.edit_env = edit_env
        self.setWindowTitle("환경 편집" if edit_env else "환경 등록")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # 환경 이름
        form = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("영문, 숫자, 한글, 공백 사용 가능")
        if edit_env:
            self.name_input.setText(edit_env.name)
            self.name_input.setEnabled(False)
        form.addRow("환경 이름:", self.name_input)
        layout.addLayout(form)

        # OS 종류 선택 (라디오 버튼)
        os_group = QGroupBox("OS 종류")
        os_layout = QVBoxLayout(os_group)
        self.os_button_group = QButtonGroup(self)

        for i, (key, name) in enumerate(OS_CATEGORY_NAMES.items()):
            radio = QRadioButton(name)
            radio.setProperty("category", key)
            self.os_button_group.addButton(radio, i)
            os_layout.addWidget(radio)
            if i == 0:
                radio.setChecked(True)

        self.os_button_group.buttonClicked.connect(self.on_os_category_changed)
        layout.addWidget(os_group)

        # OS 버전 드롭다운
        version_form = QFormLayout()
        self.os_version_combo = QComboBox()
        version_form.addRow("OS 버전:", self.os_version_combo)
        layout.addLayout(version_form)

        # Python 버전 드롭다운
        python_form = QFormLayout()
        self.python_combo = QComboBox()
        self.python_combo.addItems(PYTHON_VERSIONS)
        self.python_combo.setCurrentText("3.12")
        self.python_combo.currentIndexChanged.connect(self.update_platform_preview)
        python_form.addRow("Python 버전:", self.python_combo)
        layout.addLayout(python_form)

        # 플랫폼 미리보기
        self.platform_label = QLabel("")
        self.platform_label.setStyleSheet("color: #0066cc; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(self.platform_label)

        # 버튼
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # 초기화
        self.on_os_category_changed()

        # 편집 모드 시 기존 값 설정
        if edit_env:
            self.set_edit_values(edit_env)

    def set_edit_values(self, env):
        """편집 모드 시 기존 값 설정"""
        # OS 카테고리 찾기
        for category, os_list in OS_CATEGORIES.items():
            if env.os in os_list:
                for btn in self.os_button_group.buttons():
                    if btn.property("category") == category:
                        btn.setChecked(True)
                        self.on_os_category_changed()
                        break
                break

        # OS 버전 설정
        idx = self.os_version_combo.findText(env.os)
        if idx >= 0:
            self.os_version_combo.setCurrentIndex(idx)

        # Python 버전 설정
        idx = self.python_combo.findText(env.python)
        if idx >= 0:
            self.python_combo.setCurrentIndex(idx)

    def on_os_category_changed(self):
        """OS 카테고리 변경 시 버전 목록 업데이트"""
        checked = self.os_button_group.checkedButton()
        if not checked:
            return

        category = checked.property("category")
        os_list = OS_CATEGORIES.get(category, [])

        self.os_version_combo.clear()
        self.os_version_combo.addItems(os_list)
        self.os_version_combo.currentIndexChanged.connect(self.update_platform_preview)
        self.update_platform_preview()

    def update_platform_preview(self):
        """플랫폼 태그 미리보기 업데이트"""
        os_name = self.os_version_combo.currentText()
        python_ver = self.python_combo.currentText()

        if os_name and python_ver:
            info = get_platform_info(os_name, python_ver)
            self.platform_label.setText(f"플랫폼 태그: {info['platforms'][0]}")

    def get_values(self):
        """입력된 값 반환"""
        return {
            "name": self.name_input.text().strip(),
            "os": self.os_version_combo.currentText(),
            "python": self.python_combo.currentText(),
        }


class ResultDialog(QDialog):
    """다운로드 결과 다이얼로그"""

    def __init__(self, parent=None, result=None):
        super().__init__(parent)
        self.result = result or {}
        self.setWindowTitle("다운로드 완료")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # 결과 아이콘/메시지
        success_count = self.result.get("success", 0)
        fail_count = self.result.get("fail", 0)
        total = success_count + fail_count

        if fail_count == 0:
            icon_text = "완료"
            icon_style = "color: green; font-size: 24px; font-weight: bold;"
        else:
            icon_text = "부분 완료"
            icon_style = "color: orange; font-size: 24px; font-weight: bold;"

        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet(icon_style)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # 통계 정보
        stats_group = QGroupBox("통계")
        stats_layout = QFormLayout(stats_group)

        stats_layout.addRow("총 패키지:", QLabel(f"{total}개"))
        stats_layout.addRow("성공:", QLabel(f"{success_count}개"))

        fail_label = QLabel(f"{fail_count}개")
        if fail_count > 0:
            fail_label.setStyleSheet("color: red;")
        stats_layout.addRow("실패:", fail_label)

        total_size = self.result.get("total_size", "0 MB")
        stats_layout.addRow("총 용량:", QLabel(total_size))

        elapsed = self.result.get("elapsed", "0초")
        stats_layout.addRow("소요 시간:", QLabel(elapsed))

        layout.addWidget(stats_group)

        # 출력 위치
        output_path = self.result.get("output_path", "")
        if output_path:
            path_layout = QHBoxLayout()
            path_layout.addWidget(QLabel("출력 위치:"))
            path_label = QLabel(output_path)
            path_label.setStyleSheet("color: #0066cc;")
            path_layout.addWidget(path_label)
            path_layout.addStretch()
            layout.addLayout(path_layout)

        # 버튼
        btn_layout = QHBoxLayout()

        self.btn_open_folder = QPushButton("폴더 열기")
        self.btn_open_folder.clicked.connect(self.open_folder)

        self.btn_open_report = QPushButton("리포트 보기")
        self.btn_open_report.clicked.connect(self.open_report)

        self.btn_close = QPushButton("확인")
        self.btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_open_folder)
        btn_layout.addWidget(self.btn_open_report)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    def open_folder(self):
        """폴더 열기"""
        import os
        import platform

        output_path = self.result.get("output_path", "")
        if output_path and Path(output_path).exists():
            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":
                os.system(f'open "{output_path}"')
            else:
                os.system(f'xdg-open "{output_path}"')

    def open_report(self):
        """리포트 보기"""
        import os
        import platform

        output_path = self.result.get("output_path", "")
        report_path = Path(output_path) / "report.md"

        if report_path.exists():
            if platform.system() == "Windows":
                os.startfile(str(report_path))
            elif platform.system() == "Darwin":
                os.system(f'open "{report_path}"')
            else:
                subprocess.run(["xdg-open", str(report_path)])
        else:
            QMessageBox.warning(self, "알림", "리포트 파일이 없습니다")


class HelpDialog(QDialog):
    """환경 확인 도움말 다이얼로그"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("환경 확인 도움말")
        self.setMinimumSize(550, 500)

        layout = QVBoxLayout(self)

        # 도움말 내용
        help_text = QTextBrowser()
        help_text.setOpenExternalLinks(True)
        help_text.setHtml(self.get_help_content())

        layout.addWidget(help_text)

        # 닫기 버튼
        btn_close = QPushButton("닫기")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def get_help_content(self):
        return """
<h2>환경 확인 방법</h2>
<p>패키지를 다운로드하기 전에, 폐쇄망 서버의 OS 버전과 Python 버전을 확인해야 합니다.</p>

<hr>

<h3>Linux</h3>
<h4>OS 버전 확인</h4>
<pre style="background-color: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 5px;">
# 방법 1: 대부분의 Linux 배포판
cat /etc/os-release

# 방법 2: RedHat/CentOS 계열
cat /etc/redhat-release

# 방법 3: Ubuntu/Debian 계열
lsb_release -a
</pre>

<h4>OS 입력값 매핑</h4>
<table border="1" cellpadding="5" style="border-collapse: collapse;">
<tr><th>확인 결과</th><th>입력값</th></tr>
<tr><td>Red Hat 8.x</td><td>redhat-8</td></tr>
<tr><td>Red Hat 9.x</td><td>redhat-9</td></tr>
<tr><td>CentOS 7.x</td><td>centos-7</td></tr>
<tr><td>Rocky Linux 8.x</td><td>rocky-8</td></tr>
<tr><td>Ubuntu 20.04</td><td>ubuntu-20.04</td></tr>
<tr><td>Ubuntu 22.04</td><td>ubuntu-22.04</td></tr>
<tr><td>Debian 11</td><td>debian-11</td></tr>
<tr><td>Debian 12</td><td>debian-12</td></tr>
</table>

<hr>

<h3>Windows</h3>
<h4>OS 버전 확인</h4>
<pre style="background-color: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 5px;">
# 방법 1: GUI
winver

# 방법 2: 명령 프롬프트
systeminfo | findstr /B /C:"OS Name"
</pre>

<h4>OS 입력값 매핑</h4>
<table border="1" cellpadding="5" style="border-collapse: collapse;">
<tr><th>확인 결과</th><th>입력값</th></tr>
<tr><td>Windows 10</td><td>windows-10</td></tr>
<tr><td>Windows 11</td><td>windows-11</td></tr>
<tr><td>Windows Server 2019</td><td>windows-server-2019</td></tr>
<tr><td>Windows Server 2022</td><td>windows-server-2022</td></tr>
</table>

<hr>

<h3>macOS</h3>
<h4>OS 버전 확인</h4>
<pre style="background-color: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 5px;">
sw_vers
</pre>

<h4>아키텍처 확인 (Intel vs Apple Silicon)</h4>
<pre style="background-color: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 5px;">
uname -m
</pre>
<ul>
<li><b>x86_64</b> → Intel Mac</li>
<li><b>arm64</b> → Apple Silicon (M1/M2/M3)</li>
</ul>

<h4>OS 입력값 매핑</h4>
<table border="1" cellpadding="5" style="border-collapse: collapse;">
<tr><th>확인 결과</th><th>입력값</th></tr>
<tr><td>macOS 12 + Intel</td><td>macos-12</td></tr>
<tr><td>macOS 13 + Intel</td><td>macos-13</td></tr>
<tr><td>macOS 14 + Intel</td><td>macos-14</td></tr>
<tr><td>macOS 12 + Apple Silicon</td><td>macos-12-arm</td></tr>
<tr><td>macOS 13 + Apple Silicon</td><td>macos-13-arm</td></tr>
<tr><td>macOS 14 + Apple Silicon</td><td>macos-14-arm</td></tr>
</table>

<hr>

<h3>Python 버전 확인</h3>
<pre style="background-color: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 5px;">
python3 --version
# 또는
python --version
</pre>
<p>예시 출력: <code>Python 3.12.0</code> → 입력값: <b>3.12</b></p>

<hr>

<h3>아키텍처 확인</h3>
<h4>Linux/macOS</h4>
<pre style="background-color: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 5px;">
uname -m
</pre>
<ul>
<li><b>x86_64</b> → 64비트 Intel/AMD</li>
<li><b>aarch64</b> 또는 <b>arm64</b> → 64비트 ARM</li>
</ul>

<h4>Windows</h4>
<pre style="background-color: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 5px;">
echo %PROCESSOR_ARCHITECTURE%
</pre>
<ul>
<li><b>AMD64</b> → 64비트</li>
</ul>

<hr>

<p><b>참고:</b> 마이너 버전(8.5의 .5)은 무시하고 메이저 버전만 입력합니다.</p>
"""


class MainWindow(QMainWindow):
    """메인 윈도우"""

    SETTINGS_FILE = Path.home() / ".pkgdown" / "ui_settings.json"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("오프라인 패키지 다운로더")
        self.setMinimumSize(600, 500)

        # 윈도우 아이콘 설정
        icon_path = Path(__file__).parent / "pkgdown.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # 다운로드 상태
        self.is_downloading = False

        # 서비스 초기화
        self.env_service = EnvironmentService()

        # 메뉴바
        self.create_menu_bar()

        # 중앙 위젯
        central = QWidget()
        self.setCentralWidget(central)

        # 메인 레이아웃
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 1. 환경 선택 영역
        env_group = QGroupBox("환경 선택")
        env_layout = QVBoxLayout(env_group)

        # 환경 선택 행
        env_select_layout = QHBoxLayout()
        self.env_combo = QComboBox()
        self.env_combo.setMinimumWidth(200)
        self.env_combo.currentIndexChanged.connect(self.on_env_changed)

        self.btn_add = QPushButton("추가")
        self.btn_edit = QPushButton("편집")
        self.btn_delete = QPushButton("삭제")

        self.btn_add.clicked.connect(self.on_add_env)
        self.btn_edit.clicked.connect(self.on_edit_env)
        self.btn_delete.clicked.connect(self.on_delete_env)

        env_select_layout.addWidget(QLabel("환경:"))
        env_select_layout.addWidget(self.env_combo)
        env_select_layout.addWidget(self.btn_add)
        env_select_layout.addWidget(self.btn_edit)
        env_select_layout.addWidget(self.btn_delete)
        env_select_layout.addStretch()

        # 환경 정보 표시
        self.env_info_label = QLabel("")
        self.env_info_label.setStyleSheet("color: #666; padding: 5px;")

        env_layout.addLayout(env_select_layout)
        env_layout.addWidget(self.env_info_label)

        # 2. 패키지 입력 영역
        pkg_group = QGroupBox("패키지 입력")
        pkg_layout = QVBoxLayout(pkg_group)

        # 파일 선택 행
        file_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("requirements.txt 파일 경로")
        self.file_path_input.setReadOnly(True)
        self.btn_browse = QPushButton("찾아보기")
        self.btn_browse.clicked.connect(self.on_browse_file)
        self.btn_clear_file = QPushButton("지우기")
        self.btn_clear_file.clicked.connect(self.on_clear_file)

        file_layout.addWidget(QLabel("파일:"))
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(self.btn_browse)
        file_layout.addWidget(self.btn_clear_file)

        # 직접 입력 텍스트 영역
        self.pkg_text = QTextEdit()
        self.pkg_text.setPlaceholderText("패키지를 직접 입력하세요 (줄 단위)\n예:\nrequests\npandas>=2.0.0\nnumpy")
        self.pkg_text.setMinimumHeight(80)
        self.pkg_text.setMaximumHeight(150)
        self.pkg_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.pkg_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.pkg_text.textChanged.connect(self.on_pkg_text_changed)

        # 패키지 개수 표시
        self.pkg_count_label = QLabel("패키지: 0개")
        self.pkg_count_label.setStyleSheet("color: #666;")

        pkg_layout.addLayout(file_layout)
        pkg_layout.addWidget(QLabel("또는 직접 입력:"))
        pkg_layout.addWidget(self.pkg_text)
        pkg_layout.addWidget(self.pkg_count_label)

        # 드래그앤드롭 활성화
        self.setAcceptDrops(True)

        # 3. 출력 설정 영역
        output_group = QGroupBox("출력 설정")
        output_layout = QVBoxLayout(output_group)

        # 출력 폴더 선택
        folder_layout = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("출력 폴더 경로")
        self.output_path_input.setReadOnly(True)
        self.btn_output_browse = QPushButton("찾아보기")
        self.btn_output_browse.clicked.connect(self.on_browse_output)

        folder_layout.addWidget(QLabel("출력 폴더:"))
        folder_layout.addWidget(self.output_path_input)
        folder_layout.addWidget(self.btn_output_browse)

        # 압축 옵션
        compress_layout = QHBoxLayout()
        self.compress_check = QCheckBox("압축 파일 생성")
        self.compress_check.stateChanged.connect(self.on_compress_changed)

        self.split_label = QLabel("분할 크기(MB):")
        self.split_spin = QSpinBox()
        self.split_spin.setRange(50, 1000)
        self.split_spin.setValue(200)
        self.split_spin.setEnabled(False)

        compress_layout.addWidget(self.compress_check)
        compress_layout.addSpacing(20)
        compress_layout.addWidget(self.split_label)
        compress_layout.addWidget(self.split_spin)
        compress_layout.addStretch()

        output_layout.addLayout(folder_layout)
        output_layout.addLayout(compress_layout)

        # 4. 진행 상황 영역
        progress_group = QGroupBox("진행 상황")
        progress_layout = QVBoxLayout(progress_group)

        # 진행률 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        # 현재 작업 표시
        self.current_task_label = QLabel("대기 중...")
        self.current_task_label.setStyleSheet("color: #666;")

        # 패키지별 상태 목록
        self.status_list = QListWidget()
        self.status_list.setMaximumHeight(120)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.current_task_label)
        progress_layout.addWidget(self.status_list)

        # 5. 액션 버튼 영역
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.btn_download = QPushButton("다운로드")
        self.btn_download.setMinimumWidth(100)
        self.btn_download.setStyleSheet("font-weight: bold;")
        self.btn_download.clicked.connect(self.on_download)

        self.btn_cancel = QPushButton("취소")
        self.btn_cancel.setMinimumWidth(80)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.on_cancel)

        action_layout.addWidget(self.btn_download)
        action_layout.addWidget(self.btn_cancel)

        layout.addWidget(env_group)
        layout.addWidget(pkg_group)
        layout.addWidget(output_group)
        layout.addWidget(progress_group)
        layout.addLayout(action_layout)

        # 상태 표시줄
        self.statusBar().showMessage("준비됨")

        # 환경 목록 로드
        self.load_environments()

        # 설정 불러오기
        self.load_settings()

    def create_menu_bar(self):
        """메뉴바 생성"""
        menubar = self.menuBar()

        # 도움말 메뉴
        help_menu = menubar.addMenu("도움말")

        # 환경 확인 방법
        env_help_action = help_menu.addAction("환경 확인 방법")
        env_help_action.triggered.connect(self.show_env_help)

        help_menu.addSeparator()

        # 정보
        about_action = help_menu.addAction("정보")
        about_action.triggered.connect(self.show_about)

    def show_env_help(self):
        """환경 확인 도움말 표시"""
        dialog = HelpDialog(self)
        dialog.exec()

    def show_about(self):
        """프로그램 정보 표시"""
        QMessageBox.about(
            self,
            "오프라인 패키지 다운로더",
            "<h3>오프라인 패키지 다운로더</h3>"
            "<p>버전: 1.0.0</p>"
            "<p>폐쇄망 환경을 위한 Python 패키지 다운로드 도구</p>"
            "<hr>"
            "<p>이 프로그램은 인터넷이 되는 환경에서 "
            "지정된 플랫폼용 Python 패키지를 다운로드합니다.</p>"
        )

    def load_settings(self):
        """저장된 설정 불러오기"""
        if not self.SETTINGS_FILE.exists():
            return

        try:
            with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # 마지막 환경 선택
            last_env = settings.get("last_env", "")
            if last_env:
                idx = self.env_combo.findText(last_env)
                if idx >= 0:
                    self.env_combo.setCurrentIndex(idx)

            # 마지막 출력 폴더
            last_output = settings.get("last_output", "")
            if last_output and Path(last_output).exists():
                self.output_path_input.setText(last_output)

            # 압축 옵션
            self.compress_check.setChecked(settings.get("compress", False))
            self.split_spin.setValue(settings.get("split_size", 200))

        except Exception:
            pass  # 설정 로드 실패 시 무시

    def save_settings(self):
        """설정 저장"""
        settings = {
            "last_env": self.env_combo.currentText() if self.env_combo.isEnabled() else "",
            "last_output": self.output_path_input.text(),
            "compress": self.compress_check.isChecked(),
            "split_size": self.split_spin.value(),
        }

        try:
            self.SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # 설정 저장 실패 시 무시

    def closeEvent(self, event):
        """프로그램 종료 이벤트"""
        if self.is_downloading:
            reply = QMessageBox.question(
                self, "확인",
                "다운로드가 진행 중입니다.\n정말 종료하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        # 설정 저장
        self.save_settings()
        event.accept()

    def load_environments(self):
        """환경 목록 로드"""
        self.env_combo.clear()
        envs = self.env_service.list()

        if not envs:
            self.env_combo.addItem("-- 환경을 먼저 등록하세요 --")
            self.env_combo.setEnabled(False)
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.env_info_label.setText("")
        else:
            self.env_combo.setEnabled(True)
            self.btn_edit.setEnabled(True)
            self.btn_delete.setEnabled(True)
            for env in envs:
                self.env_combo.addItem(env.name)

    def on_env_changed(self, index):
        """환경 선택 변경"""
        if index < 0 or not self.env_combo.isEnabled():
            return

        name = self.env_combo.currentText()
        env = self.env_service.get(name)
        if env:
            info = f"OS: {env.os}  |  Python: {env.python}  |  플랫폼: {env.platforms[0]}"
            self.env_info_label.setText(info)
            self.statusBar().showMessage(f"환경: {name} ({env.os}, Python {env.python})")

    def on_add_env(self):
        """환경 추가"""
        dialog = EnvDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()

            # 검증
            if not values["name"]:
                QMessageBox.warning(self, "오류", "환경 이름을 입력하세요")
                return

            # 환경 생성
            success, msg, env = self.env_service.create(
                values["name"], values["os"], values["python"]
            )

            if success:
                self.statusBar().showMessage(msg)
                self.load_environments()
                # 새로 추가된 환경 선택
                idx = self.env_combo.findText(values["name"])
                if idx >= 0:
                    self.env_combo.setCurrentIndex(idx)
            else:
                QMessageBox.warning(self, "오류", msg)

    def on_edit_env(self):
        """환경 편집"""
        if not self.env_combo.isEnabled():
            return

        name = self.env_combo.currentText()
        env = self.env_service.get(name)
        if not env:
            return

        dialog = EnvDialog(self, edit_env=env)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()

            # 환경 수정
            success, msg, updated_env = self.env_service.update(
                name, values["os"], values["python"]
            )

            if success:
                self.statusBar().showMessage(msg)
                self.load_environments()
                # 수정된 환경 선택 유지
                idx = self.env_combo.findText(name)
                if idx >= 0:
                    self.env_combo.setCurrentIndex(idx)
            else:
                QMessageBox.warning(self, "오류", msg)

    def on_delete_env(self):
        """환경 삭제"""
        if not self.env_combo.isEnabled():
            return

        name = self.env_combo.currentText()
        reply = QMessageBox.question(
            self, "확인",
            f"환경 '{name}'을(를) 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.env_service.delete(name)
            if success:
                self.statusBar().showMessage(msg)
                self.load_environments()
            else:
                QMessageBox.warning(self, "오류", msg)

    # === 패키지 입력 영역 ===

    def on_browse_file(self):
        """파일 찾아보기"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "requirements.txt 선택", "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.load_requirements_file(file_path)

    def on_clear_file(self):
        """파일 선택 지우기"""
        self.file_path_input.clear()
        self.pkg_text.clear()
        self.pkg_text.setReadOnly(False)
        self.update_pkg_count()

    def on_pkg_text_changed(self):
        """패키지 텍스트 변경"""
        # 파일이 선택되지 않은 경우에만 개수 업데이트
        if not self.file_path_input.text():
            self.update_pkg_count()

    def load_requirements_file(self, file_path):
        """requirements.txt 파일 로드"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.file_path_input.setText(file_path)
            self.pkg_text.setPlainText(content)
            self.pkg_text.setReadOnly(True)  # 파일 로드 시 편집 불가 (스크롤은 가능)
            self.update_pkg_count()
            self.statusBar().showMessage(f"파일 로드됨: {Path(file_path).name}")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"파일을 읽을 수 없습니다:\n{e}")

    def update_pkg_count(self):
        """패키지 개수 업데이트"""
        text = self.pkg_text.toPlainText()
        packages = [line.strip() for line in text.split("\n")
                   if line.strip() and not line.strip().startswith("#")]
        count = len(packages)
        self.pkg_count_label.setText(f"패키지: {count}개")

    def get_packages(self):
        """입력된 패키지 목록 반환"""
        text = self.pkg_text.toPlainText()
        return [line.strip() for line in text.split("\n")
                if line.strip() and not line.strip().startswith("#")]

    # === 드래그앤드롭 ===

    def dragEnterEvent(self, event):
        """드래그 진입 이벤트"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """드롭 이벤트"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith(".txt"):
                self.load_requirements_file(file_path)
            else:
                QMessageBox.warning(self, "오류", "txt 파일만 지원합니다")

    # === 출력 설정 영역 ===

    def on_browse_output(self):
        """출력 폴더 찾아보기"""
        folder = QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if folder:
            self.output_path_input.setText(folder)
            self.statusBar().showMessage(f"출력 폴더: {folder}")

    def on_compress_changed(self, state):
        """압축 옵션 변경"""
        enabled = state == Qt.CheckState.Checked.value
        self.split_spin.setEnabled(enabled)
        self.split_label.setEnabled(enabled)

    # === 다운로드 실행 ===

    def on_download(self):
        """다운로드 시작"""
        # 입력 검증
        if not self.env_combo.isEnabled():
            QMessageBox.warning(self, "오류", "환경을 선택하세요")
            return

        packages = self.get_packages()
        if not packages:
            QMessageBox.warning(self, "오류", "패키지를 입력하거나 파일을 선택하세요")
            return

        output_path = self.output_path_input.text()
        if not output_path:
            QMessageBox.warning(self, "오류", "출력 폴더를 선택하세요")
            return

        # UI 상태 변경
        self.set_downloading(True)

        # 진행 상황 초기화
        self.progress_bar.setValue(0)
        self.status_list.clear()
        self.current_task_label.setText("다운로드 준비 중...")

        # 환경 정보 가져오기
        env_name = self.env_combo.currentText()
        env = self.env_service.get(env_name)
        if not env:
            QMessageBox.warning(self, "오류", "환경 정보를 가져올 수 없습니다")
            self.set_downloading(False)
            return

        # 압축 옵션
        compress = self.compress_check.isChecked()
        split_size = self.split_spin.value() if compress else 0

        # 다운로드 워커 생성 및 시작
        self.download_worker = DownloadWorker(
            env=env,
            packages=packages,
            output_dir=output_path,
            compress=compress,
            split_size=split_size
        )

        # 시그널 연결
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.message.connect(self.on_download_message)
        self.download_worker.finished.connect(self.on_download_finished)

        # 다운로드 시작
        self.download_worker.start()

    def on_download_progress(self, current, total, package, status):
        """다운로드 진행률 업데이트"""
        percent = int(current / total * 100)
        self.progress_bar.setValue(percent)
        self.current_task_label.setText(f"다운로드 중: {package} ({current}/{total})")

        # 상태 목록에 추가
        self.add_status_item(package, status)

    def on_download_message(self, message):
        """다운로드 메시지 표시"""
        self.statusBar().showMessage(message)

    def on_download_finished(self, result):
        """다운로드 완료"""
        self.set_downloading(False)

        if result.get("cancelled"):
            self.current_task_label.setText("취소됨")
            self.statusBar().showMessage("다운로드 취소됨")
            return

        self.show_result(result)

    def on_cancel(self):
        """다운로드 취소"""
        reply = QMessageBox.question(
            self, "확인",
            "다운로드를 취소하시겠습니까?\n이미 받은 파일은 유지됩니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, 'download_worker') and self.download_worker.isRunning():
                self.download_worker.cancel()
                self.current_task_label.setText("취소 중...")
                self.statusBar().showMessage("다운로드 취소 중...")

    def set_downloading(self, downloading: bool):
        """다운로드 중 UI 상태 설정"""
        self.is_downloading = downloading

        # 입력 영역 비활성화/활성화
        self.env_combo.setEnabled(not downloading)
        self.btn_add.setEnabled(not downloading)
        self.btn_edit.setEnabled(not downloading)
        self.btn_delete.setEnabled(not downloading)
        self.btn_browse.setEnabled(not downloading)
        self.btn_clear_file.setEnabled(not downloading)
        self.pkg_text.setEnabled(not downloading)
        self.btn_output_browse.setEnabled(not downloading)
        self.compress_check.setEnabled(not downloading)
        self.split_spin.setEnabled(not downloading and self.compress_check.isChecked())

        # 버튼 상태
        self.btn_download.setEnabled(not downloading)
        self.btn_cancel.setEnabled(downloading)

    def add_status_item(self, package: str, status: str):
        """상태 목록에 항목 추가"""
        item = QListWidgetItem(f"{package}: {status}")
        if status == "OK":
            item.setForeground(Qt.GlobalColor.darkGreen)
        elif status == "FAIL":
            item.setForeground(Qt.GlobalColor.red)
        else:
            item.setForeground(Qt.GlobalColor.gray)
        self.status_list.addItem(item)
        self.status_list.scrollToBottom()

    def show_result(self, result: dict):
        """결과 팝업 표시"""
        dialog = ResultDialog(self, result)
        dialog.exec()

        # 상태 업데이트
        success = result.get("success", 0)
        fail = result.get("fail", 0)
        self.current_task_label.setText(f"완료: 성공 {success}개, 실패 {fail}개")
        self.progress_bar.setValue(100)
        self.statusBar().showMessage(f"완료: {success}개 패키지 다운로드됨")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

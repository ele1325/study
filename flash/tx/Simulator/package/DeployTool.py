import sys
import subprocess
import os
import shutil
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QLineEdit, QTextEdit, QMessageBox, QHBoxLayout, QCheckBox, QComboBox
)

class DeployTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 PyInstaller Deploy Tool (Advanced)")
        self.setMinimumWidth(600)

        layout = QVBoxLayout()

        self.project_label = QLabel("專案主程式 (main.py):")
        self.project_input = QLineEdit()
        self.project_browse = QPushButton("選擇檔案")
        self.project_browse.clicked.connect(self.browse_main)

        self.spec_label = QLabel("Spec 檔案 (.spec):")
        self.spec_input = QLineEdit()
        self.spec_browse = QPushButton("選擇檔案")
        self.spec_browse.clicked.connect(self.browse_spec)

        self.upx_label = QLabel("UPX 路徑 (可選):")
        self.upx_input = QLineEdit()

        self.platform_label = QLabel("目標平台：")
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Windows (.exe)", "macOS (.app / .dmg)"])

        self.inno_label = QLabel("Inno Setup 腳本 (.iss):")
        self.inno_input = QLineEdit()
        self.inno_browse = QPushButton("選擇 .iss")
        self.inno_browse.clicked.connect(self.browse_inno)

        self.run_inno = QCheckBox("打包完成後執行 Inno Setup")
        self.run_inno.setChecked(True)

        self.github_upload = QCheckBox("打包完成後上傳 GitHub Release (需 gh CLI 登入)")

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        self.build_button = QPushButton("🚀 開始打包")
        self.build_button.clicked.connect(self.run_build)

        layout.addWidget(self.project_label)
        layout.addWidget(self.project_input)
        layout.addWidget(self.project_browse)

        layout.addWidget(self.spec_label)
        layout.addWidget(self.spec_input)
        layout.addWidget(self.spec_browse)

        layout.addWidget(self.upx_label)
        layout.addWidget(self.upx_input)

        layout.addWidget(self.platform_label)
        layout.addWidget(self.platform_combo)

        layout.addWidget(self.inno_label)
        layout.addWidget(self.inno_input)
        layout.addWidget(self.inno_browse)
        layout.addWidget(self.run_inno)

        layout.addWidget(self.github_upload)
        layout.addWidget(self.build_button)
        layout.addWidget(QLabel("🔧 日誌輸出："))
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def browse_main(self):
        file, _ = QFileDialog.getOpenFileName(self, "選擇 main.py", "", "Python Files (*.py)")
        if file:
            self.project_input.setText(file)

    def browse_spec(self):
        file, _ = QFileDialog.getOpenFileName(self, "選擇 .spec", "", "Spec Files (*.spec)")
        if file:
            self.spec_input.setText(file)

    def browse_inno(self):
        file, _ = QFileDialog.getOpenFileName(self, "選擇 .iss", "", "Inno Setup Script (*.iss)")
        if file:
            self.inno_input.setText(file)

    def run_build(self):
        main_py = self.project_input.text().strip()
        spec_file = self.spec_input.text().strip()
        upx_path = self.upx_input.text().strip()
        inno_script = self.inno_input.text().strip()
        run_inno = self.run_inno.isChecked()
        push_github = self.github_upload.isChecked()
        platform = self.platform_combo.currentText()

        if not os.path.exists(spec_file):
            QMessageBox.critical(self, "錯誤", ".spec 檔案不存在")
            return

        if os.path.exists(main_py):
            try:
                with open(spec_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                abs_main = os.path.abspath(main_py).replace('\\', '/')
                content = re.sub(r"\['.*main.py'\]", f"['{abs_main}']", content)

                conf_path = os.path.abspath(os.path.join(os.path.dirname(main_py), 'conf', 'config.ini')).replace('\\', '/')
                if os.path.exists(conf_path):
                    content = re.sub(r"\(\s*['\"]..\\\\conf\\\\config.ini['\"].*?\)",
                                     f"('{conf_path}', './conf')", content)

                with open(spec_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_output.append(f"✅ 修正 .spec 路徑與 datas 為: {abs_main}")
            except Exception as e:
                self.log_output.append(f"❌ 修正 .spec 檔失敗: {e}")

        self.log_output.append("[1] 檢查 virtualenv 是否存在...")
        if not os.path.exists("buildenv"):
            self.log_output.append("[2] 建立 virtualenv buildenv...")
            python_exe = shutil.which("python3") or sys.executable
            try:
                subprocess.run([python_exe, "-m", "venv", "buildenv"], check=True)
            except Exception as e:
                self.log_output.append(f"❌ 建立 virtualenv 失敗: {e}")
                return
        else:
            self.log_output.append("buildenv 已存在，略過建立。")

        self.log_output.append("[3] 安裝依賴 pyinstaller + pyqt5...")
        pip_cmd = "buildenv/Scripts/pip" if os.name == 'nt' else "buildenv/bin/pip"
        subprocess.call(f"{pip_cmd} install --upgrade pip pyinstaller PyQt5", shell=True)

        self.log_output.append("[4] 清理 build/dist...")
        for folder in ["build", "dist", "__pycache__"]:
            if os.path.exists(folder):
                shutil.rmtree(folder, ignore_errors=True)

        cmd = f"pyinstaller --clean {'--upx-dir ' + upx_path if upx_path else ''} {spec_file}"
        self.log_output.append(f"[5] 執行打包指令：\n{cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        self.log_output.append(result.stdout)
        self.log_output.append(result.stderr)

        built_success = False
        out_file = ""

        app_name = os.path.splitext(os.path.basename(spec_file))[0]
        dist_dir = os.path.abspath("dist")
        app_path = os.path.join(dist_dir, app_name + ".app")
        dmg_file = os.path.join(dist_dir, app_name + ".dmg")
        binary_file = os.path.join(dist_dir, app_name)
        exe_file = os.path.join(dist_dir, app_name + ".exe")

        if "macOS" in platform:
            if os.path.exists(app_path):
                self.log_output.append("[6] 產生 .dmg 映像檔...")
                create_dmg = f"hdiutil create -volname {app_name} -srcfolder \"{app_path}\" -ov -format UDZO \"{dmg_file}\""
                subprocess.call(create_dmg, shell=True)

                self.log_output.append("[7] 自動簽署 .app...")
                sign_cmd = f"codesign --deep --force --sign - \"{app_path}\""
                subprocess.call(sign_cmd, shell=True)

            for candidate in [dmg_file, app_path, binary_file]:
                if os.path.exists(candidate):
                    if candidate.endswith(".app") or os.path.isdir(candidate) or os.access(candidate, os.X_OK):
                        out_file = candidate
                        built_success = True
                        self.log_output.append(f"✔️ 偵測到輸出檔案成功：{out_file}")
                        break
        else:
            if os.path.exists(exe_file):
                out_file = exe_file
                built_success = True

        if built_success:
            self.log_output.append(f"✅ 打包完成！輸出檔案：{out_file}")
            if run_inno and os.path.exists(inno_script) and "Windows" in platform:
                self.log_output.append("[8] 執行 Inno Setup 腳本打包安裝程式...")
                subprocess.call(f"iscc \"{inno_script}\"", shell=True)
            if push_github:
                self.log_output.append("[9] 上傳到 GitHub Release...")
                tag = "v1.0.0"
                upload_cmd = f"gh release create {tag} {out_file} --title \"Release {tag}\" --notes \"Auto-packed release\""
                subprocess.call(upload_cmd, shell=True)
        else:
            self.log_output.append("❌ 未找到可執行輸出檔案 (.dmg / .app / binary)\n❌ 打包失敗，請檢查錯誤訊息。")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    tool = DeployTool()
    tool.show()
    sys.exit(app.exec_())
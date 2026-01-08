"""
GUI 主应用
"""

import json
import sys

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from translator.config import get_settings
from translator.config.languages import LanguageRegistry
from translator.gui.components import ActionButton, TextPanel
from translator.gui.styles import get_stylesheet


class TranslationWorker(QThread):
    """翻译工作线程"""

    finished = Signal(str)
    error = Signal(str)
    progress = Signal(int, int)

    def __init__(self, engine, text: str, direction: str, custom_prompt: str | None = None):
        super().__init__()
        self.engine = engine
        self.text = text
        self.direction = direction
        self.custom_prompt = custom_prompt
        self._cancelled = False

    def run(self):
        try:
            lines = [line for line in self.text.split("\n") if line.strip()]

            if len(lines) <= 1:
                result = self.engine.translate_text(
                    self.text, direction=self.direction, custom_prompt=self.custom_prompt
                )
                self.finished.emit(result)
            else:
                results = []
                for i, line in enumerate(lines):
                    if self._cancelled:
                        return

                    self.progress.emit(i + 1, len(lines))
                    result = self.engine.translate_text(
                        line, direction=self.direction, custom_prompt=self.custom_prompt
                    )
                    results.append(result)

                self.finished.emit("\n".join(results))

        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._cancelled = True


class TranslationGUI(QMainWindow):
    """翻译系统主窗口"""

    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.engine = None
        self.worker = None
        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle(f"{self.settings.app_name} - HY-MT1.5")
        self.setMinimumSize(900, 700)
        self.resize(self.settings.gui.window_width, self.settings.gui.window_height)

        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 标题
        self._create_header(layout)

        # Tab 页
        tabs = QTabWidget()
        tabs.addTab(self._create_translate_tab(), "📝 翻译")
        tabs.addTab(self._create_settings_tab(), "⚙️ 设置")
        layout.addWidget(tabs)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 - 请先加载模型")

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def _create_header(self, parent_layout: QVBoxLayout):
        """创建标题区域"""
        header = QHBoxLayout()

        # 标题文字
        title_layout = QVBoxLayout()

        title = QLabel(f"🌐 {self.settings.app_name}")
        title.setObjectName("titleLabel")

        subtitle = QLabel("基于 Tencent HY-MT1.5 模型 · 支持中英日互译")
        subtitle.setObjectName("subtitleLabel")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)

        header.addStretch()

        # 加载按钮
        self.load_btn = ActionButton("🚀 加载模型", self._load_model)
        header.addWidget(self.load_btn)

        parent_layout.addLayout(header)

    def _create_translate_tab(self) -> QWidget:
        """创建翻译标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # 工具栏
        toolbar = QHBoxLayout()

        toolbar.addWidget(QLabel("翻译方向:"))

        self.direction_combo = QComboBox()
        for code, direction in LanguageRegistry.get_all().items():
            self.direction_combo.addItem(direction.display, code)
        toolbar.addWidget(self.direction_combo)

        toolbar.addStretch()

        swap_btn = ActionButton("🔄 交换", self._swap_languages, "secondaryBtn")
        clear_btn = ActionButton("🗑️ 清空", self._clear_text, "secondaryBtn")
        toolbar.addWidget(swap_btn)
        toolbar.addWidget(clear_btn)

        layout.addLayout(toolbar)

        # 分割器
        splitter = QSplitter(Qt.Vertical)

        # 输入面板
        self.input_panel = TextPanel(
            "📥 输入文本", "在此输入要翻译的文本...\n\n支持多行文本，每行将独立翻译。"
        )
        self.input_panel.add_button("📂 加载文件", self._load_file)
        splitter.addWidget(self.input_panel)

        # 翻译按钮
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addStretch()

        self.translate_btn = ActionButton("✨ 开始翻译", self._start_translation)
        self.translate_btn.setFixedSize(180, 45)
        self.translate_btn.setEnabled(False)
        btn_layout.addWidget(self.translate_btn)

        btn_layout.addStretch()
        splitter.addWidget(btn_container)

        # 输出面板
        self.output_panel = TextPanel("📤 翻译结果", "翻译结果将在此显示...", readonly=True)
        self.output_panel.add_button("📋 复制", self._copy_result)
        self.output_panel.add_button("💾 保存", self._save_file)
        splitter.addWidget(self.output_panel)

        layout.addWidget(splitter)

        return widget

    def _create_settings_tab(self) -> QWidget:
        """创建设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        # 模型设置
        model_group = QGroupBox("🤖 模型设置")
        model_layout = QVBoxLayout(model_group)

        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("模型路径:"))
        self.model_input = QLineEdit(self.settings.model.name)
        path_row.addWidget(self.model_input)
        model_layout.addLayout(path_row)

        self.bfloat16_check = QCheckBox("使用 bfloat16 精度 (推荐)")
        self.bfloat16_check.setChecked(self.settings.model.use_bfloat16)
        model_layout.addWidget(self.bfloat16_check)

        tokens_row = QHBoxLayout()
        tokens_row.addWidget(QLabel("最大生成长度:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(256, 8192)
        self.max_tokens_spin.setValue(self.settings.model.max_new_tokens)
        self.max_tokens_spin.setSingleStep(256)
        tokens_row.addWidget(self.max_tokens_spin)
        tokens_row.addStretch()
        model_layout.addLayout(tokens_row)

        layout.addWidget(model_group)

        # 自定义提示词
        prompt_group = QGroupBox("📝 自定义提示词 (可选)")
        prompt_layout = QVBoxLayout(prompt_group)
        self.custom_prompt = QTextEdit()
        self.custom_prompt.setPlaceholderText(
            "留空使用默认提示词。\n\n示例: Translate into Chinese in a formal tone."
        )
        self.custom_prompt.setMaximumHeight(120)
        prompt_layout.addWidget(self.custom_prompt)
        layout.addWidget(prompt_group)

        layout.addStretch()

        # 关于
        about = QLabel(
            f"<b>关于</b><br>"
            f"{self.settings.app_name} v{self.settings.version}<br>"
            f"基于 Tencent HY-MT1.5-1.8B 模型"
        )
        about.setStyleSheet("padding: 12px;")
        about.setWordWrap(True)
        layout.addWidget(about)

        return widget

    def _load_model(self):
        """加载模型"""
        self.load_btn.set_loading(True, "⏳ 加载中...")
        self.status_bar.showMessage("正在加载模型...")
        QApplication.processEvents()

        try:
            from translator.core import TranslationEngine

            self.engine = TranslationEngine(
                model_name=self.model_input.text(),
                use_bfloat16=self.bfloat16_check.isChecked(),
                max_new_tokens=self.max_tokens_spin.value(),
            ).load()

            self.load_btn.setText("✅ 已加载")
            self.translate_btn.setEnabled(True)
            self.status_bar.showMessage("模型加载成功！")

            QMessageBox.information(self, "成功", f"模型加载成功！\n设备: {self.engine.device}")

        except Exception as e:
            self.load_btn.reset()
            self.status_bar.showMessage(f"加载失败: {e}")
            QMessageBox.critical(self, "错误", f"模型加载失败:\n{e}")

    def _start_translation(self):
        """开始翻译"""
        text = self.input_panel.text.strip()
        if not text:
            QMessageBox.warning(self, "提示", "请输入要翻译的文本！")
            return

        if not self.engine:
            QMessageBox.warning(self, "提示", "请先加载模型！")
            return

        self.translate_btn.set_loading(True, "⏳ 翻译中...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        direction = self.direction_combo.currentData()
        prompt = self.custom_prompt.toPlainText().strip() or None

        self.worker = TranslationWorker(self.engine, text, direction, prompt)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self._on_progress)
        self.worker.start()

    def _on_finished(self, result: str):
        """翻译完成"""
        self.output_panel.text = result
        self.translate_btn.reset()
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("翻译完成！")

    def _on_error(self, error: str):
        """翻译错误"""
        self.translate_btn.reset()
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"错误: {error}")
        QMessageBox.critical(self, "错误", f"翻译失败:\n{error}")

    def _on_progress(self, current: int, total: int):
        """进度更新"""
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(f"翻译中: {current}/{total}")

    def _swap_languages(self):
        """交换语言"""
        current = self.direction_combo.currentData()
        new_dir = LanguageRegistry.get_swap(current)

        if new_dir:
            idx = self.direction_combo.findData(new_dir)
            if idx >= 0:
                self.direction_combo.setCurrentIndex(idx)

        # 交换文本
        input_text = self.input_panel.text
        output_text = self.output_panel.text
        self.input_panel.text = output_text
        self.output_panel.text = input_text

    def _clear_text(self):
        """清空文本"""
        self.input_panel.clear()
        self.output_panel.clear()

    def _copy_result(self):
        """复制结果"""
        text = self.output_panel.text
        if text:
            QApplication.clipboard().setText(text)
            self.status_bar.showMessage("已复制！", 2000)

    def _load_file(self):
        """加载文件"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "文本文件 (*.txt);;JSON (*.json);;所有文件 (*.*)"
        )

        if path:
            try:
                with open(path, encoding="utf-8") as f:
                    if path.endswith(".json"):
                        data = json.load(f)
                        content = "\n".join(data) if isinstance(data, list) else str(data)
                    else:
                        content = f.read()

                self.input_panel.text = content
                self.status_bar.showMessage(f"已加载: {path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法读取文件:\n{e}")

    def _save_file(self):
        """保存文件"""
        text = self.output_panel.text
        if not text:
            QMessageBox.warning(self, "提示", "没有可保存的内容！")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "", "文本文件 (*.txt);;JSON (*.json)"
        )

        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    if path.endswith(".json"):
                        lines = [line for line in text.split("\n") if line.strip()]
                        json.dump(lines, f, ensure_ascii=False, indent=2)
                    else:
                        f.write(text)

                self.status_bar.showMessage(f"已保存: {path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败:\n{e}")

    def closeEvent(self, event):
        """关闭事件"""
        if self.engine:
            self.engine.unload()
        event.accept()


def main():
    """GUI 入口"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    settings = get_settings()
    app.setStyleSheet(get_stylesheet(settings.gui.theme))

    window = TranslationGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

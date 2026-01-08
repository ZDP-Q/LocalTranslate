"""
GUI 组件定义
"""

from collections.abc import Callable

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TextPanel(QGroupBox):
    """文本面板组件"""

    def __init__(
        self,
        title: str,
        placeholder: str = "",
        readonly: bool = False,
        parent: QWidget | None = None,
    ):
        super().__init__(title, parent)

        layout = QVBoxLayout(self)

        # 文本编辑器
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(placeholder)
        self.text_edit.setReadOnly(readonly)
        self.text_edit.setAcceptRichText(False)
        layout.addWidget(self.text_edit)

        # 底部工具栏
        self.toolbar = QHBoxLayout()
        layout.addLayout(self.toolbar)

        # 字符计数
        self.char_label = QLabel("字符: 0")
        self.toolbar.addStretch()
        self.toolbar.addWidget(self.char_label)

        # 连接信号
        if not readonly:
            self.text_edit.textChanged.connect(self._update_char_count)

    def _update_char_count(self):
        count = len(self.text_edit.toPlainText())
        self.char_label.setText(f"字符: {count}")

    def add_button(
        self, text: str, callback: Callable, style_id: str = "secondaryBtn"
    ) -> QPushButton:
        """添加工具栏按钮"""
        btn = QPushButton(text)
        btn.setObjectName(style_id)
        btn.clicked.connect(callback)
        self.toolbar.insertWidget(0, btn)
        return btn

    def get_text(self) -> str:
        """获取文本"""
        return self.text_edit.toPlainText()

    def set_text(self, text: str):
        """设置文本"""
        self.text_edit.setPlainText(text)

    def clear(self):
        """清空文本"""
        self.text_edit.clear()

    @property
    def text(self) -> str:
        return self.get_text()

    @text.setter
    def text(self, value: str):
        self.set_text(value)


class ActionButton(QPushButton):
    """动作按钮"""

    def __init__(
        self,
        text: str,
        callback: Callable | None = None,
        style_id: str = "",
        parent: QWidget | None = None,
    ):
        super().__init__(text, parent)

        if style_id:
            self.setObjectName(style_id)

        if callback:
            self.clicked.connect(callback)

        self._original_text = text

    def set_loading(self, loading: bool = True, text: str = ""):
        """设置加载状态"""
        if loading:
            self.setEnabled(False)
            self.setText(text or "⏳ 处理中...")
        else:
            self.setEnabled(True)
            self.setText(self._original_text)

    def reset(self):
        """重置按钮"""
        self.setEnabled(True)
        self.setText(self._original_text)

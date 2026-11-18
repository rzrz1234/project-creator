from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QLockFile, QStandardPaths, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFormLayout, QFrame, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSpinBox,
    QTabWidget, QVBoxLayout, QWidget,
)

AIGC_DIRS = [
    "01_方案", "02_提示词", "02_提示词/图片", "02_提示词/视频", "03_计划书",
    "视频素材", "数据分析", "数据分析/截图", "图片生成", "图片生成/角色",
    "图片生成/场景", "图片生成/道具", "图片生成/分段素材", "图片生成/脚本",
    "output", "video",
]


def 创建目录(根目录: Path, 相对目录: list[str]) -> None:
    for 项 in 相对目录:
        (根目录 / 项).mkdir(parents=True, exist_ok=True)


def 写入说明(根目录: Path, 标题: str, 内容: str) -> None:
    (根目录 / "项目说明.md").write_text(
        f"# {标题}\n\n{内容}\n\n创建时间：{datetime.now():%Y-%m-%d %H:%M:%S}\n",
        encoding="utf-8",
    )


class 项目页面(QWidget):
    项目类型 = "项目"

    def __init__(self) -> None:
        super().__init__()
        self.名称 = QLineEdit()
        self.名称.setPlaceholderText("例如：品牌短片_第一版")
        self.位置 = QLineEdit(str(Path.home() / "Videos"))
        self.位置.setPlaceholderText("选择项目的父文件夹")
        self.状态 = QLabel("等待创建项目")
        self.状态.setObjectName("状态标签")
        self.创建按钮 = QPushButton(f"创建 {self.项目类型}项目")
        self.创建按钮.setObjectName("主按钮")
        self.创建按钮.clicked.connect(self.创建项目)
        self.创建公共界面()

    def 创建公共界面(self) -> None:
        浏览 = QPushButton("选择文件夹")
        浏览.setObjectName("次按钮")
        浏览.clicked.connect(self.选择位置)
        位置行 = QHBoxLayout(); 位置行.setSpacing(8); 位置行.addWidget(self.位置); 位置行.addWidget(浏览)

        表单 = QFormLayout(); 表单.setLabelAlignment(Qt.AlignRight); 表单.setFormAlignment(Qt.AlignTop)
        表单.setHorizontalSpacing(18); 表单.setVerticalSpacing(14)
        表单.addRow("项目名称", self.名称); 表单.addRow("保存位置", 位置行)
        self.设置组 = QGroupBox("项目设置"); self.设置组.setLayout(表单)

        顶部 = QLabel(f"{self.项目类型}项目创建")
        顶部.setObjectName("页面标题")
        说明 = QLabel(self.页面说明)
        说明.setObjectName("页面说明")
        说明.setWordWrap(True)
        预览组 = QGroupBox("将创建的目录")
        预览 = QLabel(self.目录预览); 预览.setObjectName("目录预览"); 预览.setWordWrap(True)
        预览布局 = QVBoxLayout(); 预览布局.addWidget(预览); 预览组.setLayout(预览布局)

        操作 = QHBoxLayout(); 操作.setSpacing(12); 操作.addWidget(self.状态); 操作.addStretch(); 操作.addWidget(self.创建按钮)
        主布局 = QVBoxLayout(self); 主布局.setContentsMargins(28, 24, 28, 24); 主布局.setSpacing(18)
        主布局.addWidget(顶部); 主布局.addWidget(说明); 主布局.addWidget(self.设置组); 主布局.addWidget(预览组); 主布局.addStretch(); 主布局.addLayout(操作)

    def 选择位置(self) -> None:
        路径 = QFileDialog.getExistingDirectory(self, f"选择 {self.项目类型}项目保存位置", self.位置.text())
        if 路径:
            self.位置.setText(路径)
            self.状态.setText("已选择保存位置")

    def 校验输入(self) -> tuple[str, str] | None:
        名称, 父目录 = self.名称.text().strip(), self.位置.text().strip()
        if not 名称:
            QMessageBox.warning(self, "缺少项目名称", "请输入项目名称后再创建。")
            self.名称.setFocus(); return None
        if not 父目录 or not Path(父目录).is_dir():
            QMessageBox.warning(self, "保存位置无效", "请选择一个存在的父文件夹。")
            self.位置.setFocus(); return None
        return 名称, 父目录

    def 创建项目(self) -> None:
        raise NotImplementedError


class AIGC页面(项目页面):
    项目类型 = "AIGC "
    页面说明 = "用于管理方案、提示词、素材、图片生成结果、视频输出和交付文件。"
    目录预览 = "01_方案　·　02_提示词（图片 / 视频）　·　03_计划书　·　视频素材\n数据分析　·　图片生成（角色 / 场景 / 道具 / 分段素材 / 脚本）　·　output　·　video"

    def 创建项目(self) -> None:
        输入 = self.校验输入()
        if not 输入: return
        名称, 父目录 = 输入; 根目录 = Path(父目录) / 名称
        try:
            创建目录(根目录, AIGC_DIRS)
            写入说明(根目录, 名称, "这是一个 AIGC 项目，用于管理方案、提示词、素材、生成结果和视频成片。")
            self.状态.setText(f"已创建：{根目录}")
            QMessageBox.information(self, "创建成功", f"AIGC 项目已创建。\n\n{根目录}")
        except Exception as 错误:
            QMessageBox.critical(self, "创建失败", f"无法创建项目目录：\n{错误}")


class Houdini页面(项目页面):
    项目类型 = "Houdini "
    页面说明 = "用于创建 Houdini 工程、镜头目录，以及 hip、cache、render、comp 工作目录。"
    目录预览 = "01_reference　·　02_input　·　03_houdini（hip / otls）　·　04_shots　·　05_output　·　98_temp"

    def __init__(self) -> None:
        self.镜头数量 = QSpinBox(); self.镜头数量.setRange(0, 100); self.镜头数量.setValue(3); self.镜头数量.setSuffix(" 个")
        super().__init__()
        表单 = self.findChild(QGroupBox, "")
        if 表单:
            布局 = 表单.layout(); 布局.addRow("镜头数量", self.镜头数量)

    def 创建项目(self) -> None:
        输入 = self.校验输入()
        if not 输入: return
        名称, 父目录 = 输入; 根目录 = Path(父目录) / 名称
        try:
            创建目录(根目录, ["01_reference", "02_input", "03_houdini/hip", "03_houdini/otls", "04_shots", "05_output", "98_temp"])
            镜头 = []
            for 编号 in range(1, self.镜头数量.value() + 1):
                镜头名 = f"SH{编号 * 10:03d}"; 镜头.append(镜头名)
                创建目录(根目录 / "04_shots", [镜头名, f"{镜头名}/hip", f"{镜头名}/cache", f"{镜头名}/render", f"{镜头名}/comp"])
            写入说明(根目录, 名称, "这是一个 Houdini 项目。\n\n已创建镜头：" + ("、".join(镜头) if 镜头 else "无"))
            self.状态.setText(f"已创建：{根目录}")
            QMessageBox.information(self, "创建成功", f"Houdini 项目已创建。\n\n{根目录}")
        except Exception as 错误:
            QMessageBox.critical(self, "创建失败", f"无法创建项目目录：\n{错误}")


class 主窗口(QMainWindow):
    def __init__(self) -> None:
        super().__init__(); self.setWindowTitle("项目创建工具"); self.resize(820, 560)
        标题 = QLabel("项目创建工具"); 标题.setObjectName("窗口标题")
        副标题 = QLabel("统一创建 AIGC 与 Houdini 项目目录") ; 副标题.setObjectName("窗口副标题")
        标题区 = QVBoxLayout(); 标题区.setSpacing(3); 标题区.addWidget(标题); 标题区.addWidget(副标题)
        标志 = QLabel(); 标志.setObjectName("应用标志"); 标志.setFixedSize(54, 54); 标志.setAlignment(Qt.AlignCenter)
        图标路径 = Path(__file__).with_name("项目创建工具.ico")
        if 图标路径.exists(): 标志.setPixmap(QIcon(str(图标路径)).pixmap(48, 48))
        头部 = QHBoxLayout(); 头部.setSpacing(14); 头部.addWidget(标志); 头部.addLayout(标题区); 头部.addStretch()
        标签页 = QTabWidget(); 标签页.setDocumentMode(True); 标签页.addTab(AIGC页面(), "AIGC 项目"); 标签页.addTab(Houdini页面(), "Houdini 项目")
        中心 = QWidget(); 布局 = QVBoxLayout(中心); 布局.setContentsMargins(28, 24, 28, 22); 布局.setSpacing(20); 布局.addLayout(头部); 布局.addWidget(标签页); self.setCentralWidget(中心)


def main() -> int:
    应用 = QApplication(sys.argv); 应用.setApplicationName("项目创建工具")
    图标路径 = Path(__file__).with_name("项目创建工具.ico")
    if 图标路径.exists(): 应用.setWindowIcon(QIcon(str(图标路径)))
    应用.setStyleSheet("""
        QWidget { font-family: 'Microsoft YaHei UI'; font-size: 10.5pt; color: #1f2937; }
        QMainWindow { background: #f5f7fb; }
        #窗口标题 { font-size: 22pt; font-weight: 700; color: #111827; }
        #应用标志 { background: #ffffff; border: 1px solid #e1e6ef; border-radius: 10px; }
        #窗口副标题, #页面说明 { color: #6b7280; }
        #页面标题 { font-size: 17pt; font-weight: 700; color: #111827; }
        QTabWidget::pane { border: 1px solid #dfe4ec; border-radius: 10px; background: #ffffff; }
        QTabBar::tab { padding: 11px 24px; margin-right: 4px; color: #6b7280; }
        QTabBar::tab:selected { color: #2563eb; font-weight: 700; border-bottom: 3px solid #2563eb; }
        QGroupBox { border: 1px solid #e1e6ef; border-radius: 9px; margin-top: 12px; padding: 18px 16px 14px; background: #ffffff; font-weight: 700; }
        QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; color: #374151; }
        QLineEdit, QSpinBox { min-height: 34px; border: 1px solid #cfd6e2; border-radius: 6px; padding: 0 10px; background: #ffffff; }
        QLineEdit:focus, QSpinBox:focus { border: 1px solid #2563eb; }
        QPushButton { min-height: 36px; padding: 0 16px; border-radius: 6px; border: 1px solid #cfd6e2; background: #ffffff; }
        QPushButton:hover { background: #f1f5ff; }
        #主按钮 { background: #2563eb; color: #ffffff; border: none; font-weight: 700; min-width: 150px; }
        #主按钮:hover { background: #1d4ed8; }
        #次按钮 { min-width: 94px; }
        #状态标签 { color: #64748b; }
        #目录预览 { color: #4b5563; line-height: 1.6; }
    """)
    锁路径 = Path(QStandardPaths.writableLocation(QStandardPaths.TempLocation)) / "aigc_houdini_project_creator.lock"
    锁 = QLockFile(str(锁路径))
    if not 锁.tryLock(100): QMessageBox.warning(None, "程序已运行", "项目创建工具已经打开，请使用现有窗口。"); return 1
    窗口 = 主窗口()
    if 图标路径.exists(): 窗口.setWindowIcon(QIcon(str(图标路径)))
    窗口.show(); return 应用.exec()


if __name__ == "__main__": raise SystemExit(main())

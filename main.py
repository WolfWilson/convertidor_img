import sys
import os
import qtawesome as qta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QToolButton, QFileDialog, QSpinBox, QMessageBox, QFrame
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize
from PIL import Image


# ---------------------------------------------------------------------------
#   Helpers
# ---------------------------------------------------------------------------

def load_stylesheet(path: str) -> str:
    """Load a QSS file relative to this script's directory."""
    base = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base, path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"[WARN] Stylesheet not found: {full_path}")
        return ""


def icon(name: str) -> QIcon:
    """Return a QIcon from the icons/ directory."""
    base = os.path.dirname(os.path.abspath(__file__))
    return QIcon(os.path.join(base, "icons", name))


# ---------------------------------------------------------------------------
#   Main window
# ---------------------------------------------------------------------------

class ImageConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_paths: list[str] = []
        self.output_folder: str = ""

        self._setup_window()
        self._build_ui()

    # ── Window setup ────────────────────────────────────────────────────────

    def _setup_window(self):
        self.setWindowTitle("Convertir imágenes a WebP")
        self.setMinimumSize(560, 360)
        self.setGeometry(400, 200, 580, 380)

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(14)

        root.addWidget(self._make_title())
        root.addWidget(self._make_separator())
        root.addLayout(self._make_action_row())
        root.addWidget(self._make_label_selected())
        root.addWidget(self._make_label_destination())
        root.addWidget(self._make_separator())
        root.addLayout(self._make_quality_row())
        root.addSpacing(6)
        root.addWidget(self._make_convert_button(), alignment=Qt.AlignCenter)

    def _make_title(self) -> QLabel:
        lbl = QLabel("CONVERTIR IMÁGENES A WEBP")
        lbl.setObjectName("titleLabel")
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    def _make_separator(self) -> QFrame:
        line = QFrame()
        line.setObjectName("separator")
        line.setFrameShape(QFrame.HLine)
        return line

    def _make_action_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(16)

        self.btn_select_images = QToolButton()
        self.btn_select_images.setIcon(
            qta.icon("fa5s.file-image", color="#00f5ff")
        )
        self.btn_select_images.setIconSize(QSize(32, 32))
        self.btn_select_images.setToolTip("Seleccionar imágenes (PNG / JPG)")
        self.btn_select_images.clicked.connect(self.select_images)

        self.btn_select_folder = QToolButton()
        self.btn_select_folder.setIcon(
            qta.icon("fa5s.folder-open", color="#00f5ff")
        )
        self.btn_select_folder.setIconSize(QSize(32, 32))
        self.btn_select_folder.setToolTip("Seleccionar carpeta de destino")
        self.btn_select_folder.clicked.connect(self.select_folder)

        row.addStretch()
        row.addWidget(self.btn_select_images)
        row.addWidget(self.btn_select_folder)
        row.addStretch()
        return row

    def _make_label_selected(self) -> QLabel:
        self.lbl_selected = QLabel("No hay imágenes seleccionadas")
        self.lbl_selected.setObjectName("lblSelected")
        self.lbl_selected.setAlignment(Qt.AlignCenter)
        self.lbl_selected.setWordWrap(True)
        return self.lbl_selected

    def _make_label_destination(self) -> QLabel:
        self.lbl_destination = QLabel("Carpeta de destino no seleccionada")
        self.lbl_destination.setObjectName("lblDestination")
        self.lbl_destination.setAlignment(Qt.AlignCenter)
        self.lbl_destination.setWordWrap(True)
        return self.lbl_destination

    def _make_quality_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        lbl = QLabel("CALIDAD:")
        lbl.setObjectName("lblQuality")

        self.spin_quality = QSpinBox()
        self.spin_quality.setRange(0, 100)
        self.spin_quality.setValue(80)

        row.addStretch()
        row.addWidget(lbl)
        row.addWidget(self.spin_quality)
        row.addStretch()
        return row

    def _make_convert_button(self) -> QToolButton:
        btn = QToolButton()
        btn.setObjectName("btnConvert")
        btn.setIcon(icon("convert.png"))
        btn.setIconSize(QSize(24, 24))
        btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        btn.setText("  CONVERTIR")
        btn.setToolTip("Convertir imágenes a WebP")
        btn.clicked.connect(self.convert_images)
        return btn

    # ── Slots / business logic ───────────────────────────────────────────────

    def select_images(self):
        """Open a dialog to pick one or more PNG/JPG images."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar imágenes",
            "",
            "Imágenes (*.png *.jpg *.jpeg);;Todos los archivos (*)"
        )
        if files:
            self.image_paths = files
            names = [os.path.basename(f) for f in files]
            self.lbl_selected.setText("  |  ".join(names))

    def select_folder(self):
        """Open a dialog to pick the output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de destino")
        if folder:
            self.output_folder = folder
            self.lbl_destination.setText(folder)

    def convert_images(self):
        """Convert selected images to WebP using Pillow."""
        if not self.image_paths:
            QMessageBox.warning(self, "Advertencia", "No has seleccionado ninguna imagen.")
            return

        if not self.output_folder:
            QMessageBox.warning(self, "Advertencia", "No has seleccionado carpeta de destino.")
            return

        quality = self.spin_quality.value()
        errors: list[str] = []

        for path in self.image_paths:
            try:
                name_no_ext = os.path.splitext(os.path.basename(path))[0]
                out_path = os.path.join(self.output_folder, f"{name_no_ext}.webp")
                Image.open(path).convert("RGB").save(out_path, "webp", quality=quality)
            except Exception as exc:
                errors.append(f"{os.path.basename(path)}: {exc}")

        if errors:
            QMessageBox.warning(self, "Errores en la conversión", "\n".join(errors))
        else:
            count = len(self.image_paths)
            QMessageBox.information(
                self, "Completado",
                f"{count} imagen{'es' if count != 1 else ''} convertida{'s' if count != 1 else ''} correctamente."
            )


# ---------------------------------------------------------------------------
#   Entry point
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("styles/cyberpunk.qss"))
    window = ImageConverter()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

import sys
import os
import qtawesome as qta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QToolButton, QFileDialog, QSpinBox, QMessageBox, QFrame,
    QCheckBox
)
from PyQt5.QtGui import QIcon, QFont, QPixmap
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
        self._preview_pixmap: QPixmap | None = None

        self._setup_window()
        self._build_ui()

    # ── Window setup ────────────────────────────────────────────────────────

    def _setup_window(self):
        self.setWindowTitle("Convertir imágenes a WebP")
        self.setMinimumSize(760, 480)
        self.setGeometry(300, 150, 920, 540)

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

        # ── Content row: controls (left) + preview (right) ──────────────────
        content = QHBoxLayout()
        content.setSpacing(20)

        controls = QVBoxLayout()
        controls.setSpacing(14)
        controls.addLayout(self._make_action_row())
        controls.addWidget(self._make_label_selected())
        controls.addWidget(self._make_label_destination())
        controls.addWidget(self._make_separator())
        controls.addLayout(self._make_quality_row())
        controls.addLayout(self._make_resize_row())
        controls.addStretch()

        content.addLayout(controls, stretch=3)
        content.addWidget(self._make_preview_panel(), stretch=2)

        root.addLayout(content)
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
        self.btn_select_images.setToolTip("Seleccionar imágenes (PNG / JPG / WebP)")
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

    def _make_resize_row(self) -> QHBoxLayout:
        """Checkbox + width/height inputs for optional resizing."""
        row = QHBoxLayout()
        row.setSpacing(10)

        self.chk_resize = QCheckBox("REDIMENSIONAR")
        self.chk_resize.setObjectName("chkResize")
        self.chk_resize.setChecked(False)
        self.chk_resize.toggled.connect(self._on_resize_toggled)

        lbl_w = QLabel("ANCHO:")
        lbl_w.setObjectName("lblDimension")

        self.spin_width = QSpinBox()
        self.spin_width.setObjectName("spinDimension")
        self.spin_width.setRange(1, 9999)
        self.spin_width.setValue(800)
        self.spin_width.setSuffix(" px")
        self.spin_width.setEnabled(False)

        lbl_h = QLabel("ALTO:")
        lbl_h.setObjectName("lblDimension")

        self.spin_height = QSpinBox()
        self.spin_height.setObjectName("spinDimension")
        self.spin_height.setRange(1, 9999)
        self.spin_height.setValue(600)
        self.spin_height.setSuffix(" px")
        self.spin_height.setEnabled(False)

        row.addStretch()
        row.addWidget(self.chk_resize)
        row.addSpacing(16)
        row.addWidget(lbl_w)
        row.addWidget(self.spin_width)
        row.addSpacing(8)
        row.addWidget(lbl_h)
        row.addWidget(self.spin_height)
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

    def _make_preview_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("previewFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)

        self.lbl_preview = QLabel("SIN VISTA\nPREVIA")
        self.lbl_preview.setObjectName("previewLabel")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setWordWrap(True)
        layout.addWidget(self.lbl_preview)
        return frame

    def _update_preview(self):
        if len(self.image_paths) == 1:
            px = QPixmap(self.image_paths[0])
            if not px.isNull():
                self._preview_pixmap = px
                self._refresh_preview_scaled()
            else:
                self._preview_pixmap = None
                self.lbl_preview.clear()
                self.lbl_preview.setText("⚠ ERROR\nAL CARGAR")
        elif len(self.image_paths) > 1:
            self._preview_pixmap = None
            self.lbl_preview.clear()
            self.lbl_preview.setText(
                f"◈ BATCH MODE ◈\n\n{len(self.image_paths)} imágenes\nseleccionadas"
            )
        else:
            self._preview_pixmap = None
            self.lbl_preview.clear()
            self.lbl_preview.setText("SIN VISTA\nPREVIA")

    def _refresh_preview_scaled(self):
        if self._preview_pixmap is None:
            return
        size = self.lbl_preview.size()
        if size.width() < 10 or size.height() < 10:
            return
        scaled = self._preview_pixmap.scaled(
            size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.lbl_preview.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_preview_scaled()

    def _on_resize_toggled(self, checked: bool):
        """Enable or disable dimension inputs based on checkbox state."""
        self.spin_width.setEnabled(checked)
        self.spin_height.setEnabled(checked)

    # ── Slots / business logic ───────────────────────────────────────────────

    def select_images(self):
        """Open a dialog to pick one or more PNG/JPG images."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar imágenes",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.webp);;Todos los archivos (*)"
        )
        if files:
            self.image_paths = files
            names = [os.path.basename(f) for f in files]
            self.lbl_selected.setText("  |  ".join(names))

            # Default output folder = source folder (overrideable by the user)
            if not self.output_folder:
                source_dir = os.path.dirname(files[0])
                self.output_folder = source_dir
                self.lbl_destination.setText(source_dir)

            self._update_preview()

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
        do_resize = self.chk_resize.isChecked()
        target_w = self.spin_width.value()
        target_h = self.spin_height.value()
        errors: list[str] = []

        for path in self.image_paths:
            try:
                name_no_ext = os.path.splitext(os.path.basename(path))[0]
                out_path = os.path.join(self.output_folder, f"{name_no_ext}.webp")
                img = Image.open(path)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA" if img.mode == "P" and "transparency" in img.info else "RGB")
                if do_resize:
                    img = img.resize((target_w, target_h), Image.LANCZOS)
                img.save(out_path, "webp", quality=quality)
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

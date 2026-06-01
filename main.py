import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QToolButton, QFileDialog, QSpinBox, QMessageBox
    
)

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize
from PIL import Image


class ImageConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Convertir imágenes a WebP")
        self.setGeometry(400, 200, 500, 300)

        # Estilos globales del QMainWindow
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E2E2E;
            }
            QLabel {
                color: #FFFFFF;
            }
            QSpinBox {
                background-color: #3E3E3E;
                color: #FFFFFF;
                border: 1px solid #5E5E5E;
                border-radius: 4px;
                padding: 2px;
            }
        """)

        # Variables para almacenar paths de imágenes y carpeta de destino
        self.image_paths = []
        self.output_folder = ""

        # Widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1) Título
        title_label = QLabel("Convertir imágenes a WebP")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 14, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # --------------------------------------------------
        #   BOTONES DE HERRAMIENTAS (QToolButton) EN FILA 1
        # --------------------------------------------------
        row1_layout = QHBoxLayout()
        layout.addLayout(row1_layout)

        # Botón Seleccionar Imágenes
        btn_select_images = QToolButton()
        btn_select_images.setIcon(QIcon("icons/select_image.png"))
        # Aquí usamos QSize, importado desde PyQt5.QtCore
        btn_select_images.setIconSize(QSize(32, 32))
        btn_select_images.setToolTip("Seleccionar Imágenes (PNG/JPG)")
        btn_select_images.clicked.connect(self.select_images)

        row1_layout.addWidget(btn_select_images)

        # Botón Seleccionar Carpeta
        btn_select_folder = QToolButton()
        btn_select_folder.setIcon(QIcon("icons/folder.png"))
        btn_select_folder.setIconSize(QSize(32, 32))  # <-- IMPORTANTE
        btn_select_folder.setToolTip("Seleccionar Carpeta de Destino")
        btn_select_folder.clicked.connect(self.select_folder)
        row1_layout.addWidget(btn_select_folder)

        row1_layout.addWidget(btn_select_folder)

        # --------------------------------------------------
        #   ETIQUETA CON NOMBRES DE ARCHIVOS
        # --------------------------------------------------
        self.lbl_selected = QLabel("No hay imágenes seleccionadas")
        self.lbl_selected.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        self.lbl_selected.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_selected)

        # --------------------------------------------------
        #   ETIQUETA CON CARPETA DE DESTINO
        # --------------------------------------------------
        self.lbl_destination = QLabel("Carpeta de destino no seleccionada")
        self.lbl_destination.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        self.lbl_destination.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_destination)

        # --------------------------------------------------
        #   CALIDAD (SPINBOX)
        # --------------------------------------------------
        quality_layout = QHBoxLayout()
        layout.addLayout(quality_layout)

        lbl_quality = QLabel("Calidad:")
        lbl_quality.setStyleSheet("font-size: 13px; color: #FFFFFF;")
        quality_layout.addWidget(lbl_quality)

        self.spin_quality = QSpinBox()
        self.spin_quality.setRange(0, 100)
        self.spin_quality.setValue(80)  # valor por defecto
        quality_layout.addWidget(self.spin_quality)

        # --------------------------------------------------
        #   BOTÓN CONVERTIR (TOOLBUTTON)
        # --------------------------------------------------
        btn_convert = QToolButton()
        btn_convert.setIcon(QIcon("icons/convert.png"))
        btn_convert.setIconSize(QSize(32, 32))  # <-- IMPORTANTE
        btn_convert.setToolTip("Convertir Imágenes a WebP")
        btn_convert.clicked.connect(self.convert_images)
        layout.addWidget(btn_convert, alignment=Qt.AlignCenter)

    # ---------------------------------------------------------------------
    #   Funciones para seleccionar y convertir
    # ---------------------------------------------------------------------
    def select_images(self):
        """
        Abre un diálogo para seleccionar una o varias imágenes (png/jpg/jpeg).
        """
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar imágenes",
            "",
            "Imágenes (*.png *.jpg *.jpeg);;Todos los archivos (*)"
        )
        if files:
            self.image_paths = files
            # Mostramos la lista de archivos seleccionados en la etiqueta
            file_names = [os.path.basename(f) for f in files]
            self.lbl_selected.setText("\n".join(file_names))

    def select_folder(self):
        """
        Abre un diálogo para seleccionar la carpeta de destino.
        """
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de destino")
        if folder:
            self.output_folder = folder
            self.lbl_destination.setText(folder)

    def convert_images(self):
        """
        Convierte las imágenes seleccionadas a formato WebP,
        manteniendo el nombre y guardando en la carpeta elegida.
        """
        if not self.image_paths:
            QMessageBox.warning(self, "Advertencia", "No has seleccionado ninguna imagen.")
            return

        if not self.output_folder:
            QMessageBox.warning(self, "Advertencia", "No has seleccionado carpeta de destino.")
            return

        calidad = self.spin_quality.value()  # valor del SpinBox
        errores = []

        for path in self.image_paths:
            try:
                # Nombre base y sin extensión
                base_name = os.path.basename(path)
                name_no_ext = os.path.splitext(base_name)[0]

                # Ruta de salida
                out_path = os.path.join(self.output_folder, f"{name_no_ext}.webp")

                # Convertir a WebP con Pillow
                im = Image.open(path).convert("RGB")
                im.save(out_path, "webp", quality=calidad)
            except Exception as e:
                errores.append(f"Error al convertir {path}: {str(e)}")

        # Mensaje de resultado
        if errores:
            msg = "\n".join(errores)
            QMessageBox.warning(self, "Errores en la conversión", msg)
        else:
            QMessageBox.information(self, "Completado", "Todas las imágenes se convirtieron correctamente.")


def main():
    app = QApplication(sys.argv)
    window = ImageConverter()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

# This Python file uses the following encoding: utf-8
import io
import sys
import traceback as tb

from PIL import Image
from PySide6 import QtGui
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog, QGraphicsPixmapItem

from main_window import MainWindow
from stages import Stage, stages


def pil2pixmap(image: Image) -> QtGui.QPixmap:
    bytes_img = io.BytesIO()
    image.save(bytes_img, format='TIFF')

    qimg = QtGui.QImage()
    qimg.loadFromData(bytes_img.getvalue())

    return QtGui.QPixmap.fromImage(qimg)


class Application:
    app: QApplication
    window: MainWindow
    stages: list[Stage]
    current_stage: int
    history: list[Stage]

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.stages = stages
        self.current_stage = 0
        self.history = []
        self.image_file = None

        self.window = MainWindow(self.stages)
        self.window.show()
        self.set_handlers()

    def set_handlers(self):
        for rb in self.window.stages_radio_buttons:
            rb.clicked.connect(self.change_stage)
        self.window.proceed_button.clicked.connect(self.proceed_current_stage)
        self.window.settings_widget.settings_changed_signal.connect(self.settings_changed)
        self.window.open_file.triggered.connect(self.open_file)
        self.stages[self.current_stage].ready_signal.connect(self.current_stage_ready)

    def exec(self):
        return self.app.exec()

    def open_file(self):
        self.image_file, _ = QFileDialog.getOpenFileName(
            self.window,
            'Открыть изображение',
            '',
            'TIFF (*.tiff *.tif)'
        )
        if self.image_file:
            for s in self.stages:
                s.input_data = None
            image = Image.open(self.image_file)
            self.current_stage = 0
            self.stages[0].input_data = image
            self.window.stages_radio_buttons[0].click()
            for rb in self.window.stages_radio_buttons[1:]:
                rb.setEnabled(False)
            self.window.proceed_button.setEnabled(True)
            self.add_image(image)

    def add_image(self, image):
        for i in self.window.main_image_scene.items():
            self.window.main_image_scene.removeItem(i)
        self.window.main_image_scene.addItem(QGraphicsPixmapItem(pil2pixmap(image)))

    def change_stage(self):
        for i, rb in enumerate(self.window.stages_radio_buttons):
            if rb.isChecked():
                if i != self.current_stage:
                    self.current_stage = i
                    self.window.set_stage(self.stages[i])
                    self.stages[i].ready_signal.connect(self.current_stage_ready)
                    if self.stages[i].input_data is not None:
                        self.window.proceed_button.setEnabled(True)
                break

    def settings_changed(self):
        # print(*self.stages[self.current_stage].settings, sep='\n')
        pass

    def proceed_current_stage(self):
        print(f'Proceeding {self.stages[self.current_stage].name}')
        self.window.proceed_button.setEnabled(False)
        self.stages[self.current_stage].proceed()

    def current_stage_ready(self):
        s = self.stages[self.current_stage]
        print(f'Ready {s.name}')
        self.add_image(s.visualizer(s.result))
        if self.current_stage < len(self.window.stages_radio_buttons) - 1:
            self.window.stages_radio_buttons[self.current_stage + 1].setEnabled(True)
            self.window.stages_radio_buttons[self.current_stage + 1].setChecked(True)
            self.change_stage()
            self.window.proceed_button.setEnabled(True)


def gui_exception_hook(exc_type, value, traceback):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(str(value))
    msg.setInformativeText(''.join(tb.format_exception(exc_type, value, traceback)))
    msg.setWindowTitle(exc_type.__name__)
    msg.exec()


if __name__ == "__main__":
    # sys.excepthook = gui_exception_hook
    app = Application()
    sys.exit(app.exec())

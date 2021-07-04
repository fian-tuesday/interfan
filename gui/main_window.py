# -*- coding: utf-8 -*-
from functools import partial
from textwrap import wrap

from PySide6 import QtCore
from PySide6.QtCore import QRect, QMetaObject
from PySide6.QtGui import Qt, QAction
from PySide6.QtWidgets import (QMainWindow, QSizePolicy, QWidget, QHBoxLayout, QGridLayout, QSlider, QLabel,
                               QGraphicsView, QVBoxLayout, QPushButton, QRadioButton, QToolButton,
                               QListView, QMenuBar, QMenu,
                               QStatusBar, QLineEdit, QCheckBox, QGroupBox, QGraphicsScene)

from stages import Stage


class SettingWidget(QWidget):
    settings_changed_signal = QtCore.Signal()

    def __init__(self, parent, settings=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.setObjectName("settings_widget")
        self.group_box = QGroupBox("Настройки")
        self.layout = QGridLayout()
        self.layout.setObjectName('settings_layout')
        self.layout.setColumnStretch(0, 6)
        self.layout.setColumnStretch(1, 1)
        self.group_box.setLayout(self.layout)
        self.widgets = []

        self.change_settings(settings)

    def change_settings(self, settings):

        # First clean up all previous items
        for i in range(self.layout.count()):
            self.layout.removeItem(self.layout.takeAt(0))
        for w in self.widgets:
            w.deleteLater()
        self.widgets = []

        if not settings:
            label = QLabel(self.parentWidget())
            label.setObjectName("settings_empty_label")
            label.setText("Для данной операции настройки отсутствуют")
            label.setWordWrap(True)
            self.widgets.append(label)
            self.layout.addWidget(label, 0, 0)

        else:
            x = 0
            for s in settings:
                if isinstance(s.type, range):
                    label = QLabel(self.parentWidget())
                    label.setText(s.text)
                    label.setWordWrap(True)
                    self.widgets.append(label)
                    self.layout.addWidget(label, x, 0)

                    slider = QSlider(self.parentWidget())
                    slider.setOrientation(Qt.Horizontal)
                    slider.setMinimum(s.type.start // s.type.step)
                    slider.setMaximum(s.type.stop // s.type.step - 1)
                    slider.setValue(s.value // s.type.step)
                    self.layout.addWidget(slider, x + 1, 0)

                    line_edit = QLineEdit(self.parentWidget())
                    line_edit.setText(str(s.value))
                    self.layout.addWidget(line_edit, x + 1, 1)

                    slider.valueChanged.connect(partial(self.slider_change, line_edit, s))
                    line_edit.returnPressed.connect(partial(self.line_edit_change, slider, line_edit, s))

                    self.widgets.append(slider)
                    self.widgets.append(line_edit)
                    x += 2

                elif s.type == bool:
                    checkbox = QCheckBox(self.parentWidget())
                    checkbox.setText('\n'.join(wrap(s.text, 40)))
                    checkbox.setChecked(s.value)
                    checkbox.clicked.connect(partial(self.checkbox_changed, checkbox, s))

                    self.layout.addWidget(checkbox, x, 0)
                    self.widgets.append(checkbox)
                    x += 1
                elif s.type in (int, float, str):
                    pass

    def slider_change(self, line_edit: QLineEdit, settings_item, value):
        value *= settings_item.type.step
        if settings_item.value != value:
            line_edit.setText(str(value))
            settings_item.value = value
            self.settings_changed_signal.emit()

    def line_edit_change(self, slider: QSlider, line_edit: QLineEdit, settings_item):
        value = line_edit.text()
        try:
            if settings_item.type == int or isinstance(settings_item.type, range):
                value = int(value)
            elif settings_item.type == float:
                value = float(value)
            if isinstance(settings_item.type, range) and value not in settings_item.type:
                raise ValueError
        except ValueError:
            line_edit.setText(str(settings_item.value))
            return
        if settings_item.value != value:
            settings_item.value = value
            if slider is not None:
                slider.setValue(value // settings_item.type.step)
            self.settings_changed_signal.emit()

    def checkbox_changed(self, checkbox: QCheckBox, settings_item):
        if settings_item.value != checkbox.isChecked():
            settings_item.value = checkbox.isChecked()
            self.settings_changed_signal.emit()


class MainWindow(QMainWindow):
    def __init__(self, stages: list[Stage], *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        if not self.objectName():
            self.setObjectName("MainWindow")
        self.resize(800, 600)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
        self.setWindowTitle("Interfan")

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")

        self.main_horizontal_layout = QHBoxLayout(self.central_widget)
        self.main_horizontal_layout.setObjectName("main_horizontal_layout")

        self.left_grid_layout = QGridLayout()
        self.left_grid_layout.setObjectName("left_grid_layout")

        self.slice_slider = QSlider(self.central_widget)
        self.slice_slider.setObjectName("slice_slider")
        self.slice_slider.setEnabled(False)
        self.slice_slider.setOrientation(Qt.Horizontal)

        self.left_grid_layout.addWidget(self.slice_slider, 1, 0, 1, 1)

        self.slice_label = QLabel(self.central_widget)
        self.slice_label.setObjectName("slice_label")
        self.slice_label.setGeometry(QRect(0, 10, 58, 18))
        self.slice_label.setText("0")
        self.left_grid_layout.addWidget(self.slice_label, 1, 1, 1, 1)

        self.main_image_scene = QGraphicsScene()
        self.main_image_view = QGraphicsView(self.main_image_scene)
        self.main_image_view.setObjectName("main_image_view")
        self.left_grid_layout.addWidget(self.main_image_view, 0, 0, 1, 1)

        self.slice_image_scene = QGraphicsScene()
        self.slice_image_view = QGraphicsView(self.slice_image_scene)
        self.slice_image_view.setObjectName("slice_image_view")
        self.left_grid_layout.addWidget(self.slice_image_view, 0, 1, 1, 1)

        self.left_grid_layout.setRowStretch(0, 12)
        self.left_grid_layout.setRowStretch(1, 1)
        self.left_grid_layout.setColumnStretch(0, 6)
        self.left_grid_layout.setColumnStretch(1, 1)

        self.main_horizontal_layout.addLayout(self.left_grid_layout)

        self.right_vertical_layout = QVBoxLayout()
        self.right_vertical_layout.setObjectName("right_vertical_layout")

        self.settings_widget = SettingWidget(self.central_widget)
        self.right_vertical_layout.addWidget(self.settings_widget.group_box)

        self.proceed_button = QPushButton(self.central_widget)
        self.proceed_button.setObjectName("proceed_button")
        self.proceed_button.setText("Выполнить")
        self.proceed_button.setEnabled(False)
        self.right_vertical_layout.addWidget(self.proceed_button)

        self.right_down_layout = QHBoxLayout()
        self.right_down_layout.setObjectName("right_down_layout")
        self.stages_layout = QVBoxLayout()
        self.stages_layout.setObjectName("stages_layout")

        self.stages_label = QLabel(self.central_widget)
        self.stages_label.setObjectName("stages_label")
        self.stages_label.setText("Этапы")
        self.stages_layout.addWidget(self.stages_label, 1)

        self.stages_radio_buttons = []
        for s in stages:
            rb = QRadioButton(self.central_widget)
            rb.setObjectName("stages_radio_button")
            rb.setEnabled(False)
            rb.setText(s.name)
            self.stages_layout.addWidget(rb, 1)
            self.stages_radio_buttons.append(rb)

        self.stages_radio_buttons[0].setEnabled(True)
        self.stages_radio_buttons[0].setChecked(True)
        self.set_stage(stages[0])

        self.right_down_layout.addLayout(self.stages_layout)

        self.history_layout = QVBoxLayout()
        self.history_layout.setObjectName("history_layout")
        self.history_header_layout = QHBoxLayout()
        self.history_header_layout.setObjectName("history_header_layout")

        self.history_label = QLabel(self.central_widget)
        self.history_label.setObjectName("history_label")
        self.history_label.setText("История операций")
        self.history_header_layout.addWidget(self.history_label)

        self.history_minus_button = QToolButton(self.central_widget)
        self.history_minus_button.setObjectName("history_minus_button")
        self.history_minus_button.setEnabled(False)
        self.history_minus_button.setText("-")
        self.history_header_layout.addWidget(self.history_minus_button)

        self.history_header_layout.setStretch(0, 8)
        self.history_header_layout.setStretch(1, 1)

        self.history_layout.addLayout(self.history_header_layout)

        self.history_list_view = QListView(self.central_widget)
        self.history_list_view.setObjectName("history_list_view")
        self.history_layout.addWidget(self.history_list_view)

        self.history_script_button = QPushButton(self.central_widget)
        self.history_script_button.setObjectName("history_script_button")
        self.history_script_button.setText("Просмотреть как скрипт")
        self.history_layout.addWidget(self.history_script_button)

        self.right_down_layout.addLayout(self.history_layout)

        self.right_down_layout.setStretch(0, 1)
        self.right_down_layout.setStretch(1, 1)

        self.right_vertical_layout.addLayout(self.right_down_layout)
        self.right_vertical_layout.setStretch(0, 1)
        self.right_vertical_layout.setStretch(1, 0)
        self.right_vertical_layout.setStretch(2, 1)

        self.main_horizontal_layout.addLayout(self.right_vertical_layout)
        self.main_horizontal_layout.setStretch(0, 1)
        self.main_horizontal_layout.setStretch(1, 1)

        self.setCentralWidget(self.central_widget)
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setObjectName("menu_bar")
        self.menu_bar.setGeometry(QRect(0, 0, 800, 30))
        self.menu = QMenu(self.menu_bar)
        self.menu.setObjectName("men")
        self.menu.setTitle("Меню")
        self.setMenuBar(self.menu_bar)

        self.open_file = QAction(self)
        self.open_file.setObjectName("open_file")
        self.open_file.setText("Открыть файл")
        self.menu.addAction(self.open_file)

        self.status_bar = QStatusBar(self)
        self.status_bar.setObjectName("status_bar")
        self.setStatusBar(self.status_bar)

        self.menu_bar.addAction(self.menu.menuAction())

        QMetaObject.connectSlotsByName(self)

    def set_stage(self, stage: Stage):
        self.settings_widget.change_settings(stage.settings)

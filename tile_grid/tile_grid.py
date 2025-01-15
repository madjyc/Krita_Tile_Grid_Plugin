# Tile Grid plugin for Krita
# By Jean-Yves 'madjyc' Chasle
# SPDX-License-Identifier: CC0-1.0
# A Krita plugin designed to add a set of guides defining "tiles" (or "cells") to the current document based on user-defined margins, gutters, and number of tiles.

from krita import (
        Extension
    )
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QDoubleSpinBox,
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QPushButton,
        QSpinBox,
        QVBoxLayout
    )
import os, json


PLUGIN_VERSION = '0.1.2'

EXTENSION_ID = 'pykrita_tile_grid'
PLUGIN_MENU_ENTRY = i18n('Tile Grid')
PLUGIN_DIALOG_TITLE = i18n("{0} - {1}".format(i18n('Tile Grid'), PLUGIN_VERSION))

class TileGridDialog(QDialog):
    def __init__(self, doc_size_x, doc_size_y, doc_ppi):
        super().__init__()
        self.setWindowTitle(PLUGIN_DIALOG_TITLE)
        
        # Resolution in pixels per inch
        self.doc_size_x = doc_size_x
        self.doc_size_y = doc_size_y
        self.doc_ppi = doc_ppi

        # Default values
        self.LAST_PRESET_FILENAME = "krita_tile_grid_plugin_last_preset"

        self.UNIT_PX = i18n("Pixels (px)")
        self.UNIT_IN = i18n("Inches (in)")
        self.UNIT_CM = i18n("Centimeter (cm)")
        self.UNIT_PC = i18n("Percentage (%)")
        self.UNITS = [self.UNIT_PX, self.UNIT_IN, self.UNIT_CM, self.UNIT_PC]

        self.DEFAULT_MARGIN_L_PC = 10.0
        self.DEFAULT_MARGIN_R_PC = 10.0
        self.DEFAULT_MARGIN_T_PC = 15.0
        self.DEFAULT_MARGIN_B_PC = 15.0
        self.DEFAULT_GUTTER_X_PC = 2.5
        self.DEFAULT_GUTTER_Y_PC = 2.5
        self.DEFAULT_NUM_TILES_X = 3
        self.DEFAULT_NUM_TILES_Y = 3
        self.DEFAULT_TILE_RATIO = 1.78
        self.DEFAULT_CLEAR_GUIDES = False
        self.DEFAULT_LOCK_GUIDES = True
        self.DEFAULT_SNAP_GUIDES = True
        self.DEFAULT_MIN_SPINBOX_WIDTH = 80

        self.layout = QVBoxLayout()
        
        # Create the editable fields
        self.margin_l = QDoubleSpinBox()
        self.margin_l_unit = QComboBox()
        self.margin_r = QDoubleSpinBox()
        self.margin_r_unit = QComboBox()
        self.margin_t = QDoubleSpinBox()
        self.margin_t_unit = QComboBox()
        self.margin_b = QDoubleSpinBox()
        self.margin_b_unit = QComboBox()
        self.gutter_x = QDoubleSpinBox()
        self.gutter_x_unit = QComboBox()
        self.gutter_y = QDoubleSpinBox()
        self.gutter_y_unit = QComboBox()
        self.num_tiles_x = QSpinBox()
        self.num_tiles_y = QSpinBox()
        self.tile_ratio = QDoubleSpinBox()
        self.clear_guides = QCheckBox(i18n("Clear guides"))
        self.lock_guides = QCheckBox(i18n("Lock guides"))
        self.snap_guides = QCheckBox(i18n("Snap to guides"))

        self.tile_ratio.setDecimals(3)
        self.tile_ratio.setSingleStep(0.01)
        self.tile_ratio.setMinimum(0.01)

        self.num_tiles_x.setMinimumWidth(self.DEFAULT_MIN_SPINBOX_WIDTH)
        self.num_tiles_y.setMinimumWidth(self.DEFAULT_MIN_SPINBOX_WIDTH)
        self.tile_ratio.setMinimumWidth(self.DEFAULT_MIN_SPINBOX_WIDTH)

        self.margin_l.setAlignment(Qt.AlignRight)
        self.margin_r.setAlignment(Qt.AlignRight)
        self.margin_t.setAlignment(Qt.AlignRight)
        self.margin_b.setAlignment(Qt.AlignRight)
        self.gutter_x.setAlignment(Qt.AlignRight)
        self.gutter_y.setAlignment(Qt.AlignRight)
        self.num_tiles_x.setAlignment(Qt.AlignRight)
        self.num_tiles_y.setAlignment(Qt.AlignRight)
        self.tile_ratio.setAlignment(Qt.AlignRight)

        self.margin_l.setToolTip(i18n("Set the left margin size"))
        self.margin_l_unit.setToolTip(i18n("Select the unit for the left margin size"))
        self.margin_r.setToolTip(i18n("Set the right margin size"))
        self.margin_r_unit.setToolTip(i18n("Select the unit for the right margin size"))
        self.margin_t.setToolTip(i18n("Set the top margin size"))
        self.margin_t_unit.setToolTip(i18n("Select the unit for the top margin size"))
        self.margin_b.setToolTip(i18n("Set the bottom margin size"))
        self.margin_b_unit.setToolTip(i18n("Select the unit for the bottom margin size"))
        self.gutter_x.setToolTip(i18n("Set the minimum size for the horizontal gutters"))
        self.gutter_x_unit.setToolTip(i18n("Select the unit for the minimum horizontal gutter size"))
        self.gutter_y.setToolTip(i18n("Set the minimum size for the vertical gutters"))
        self.gutter_y_unit.setToolTip(i18n("Select the unit for the minimum vertical gutter size"))
        self.num_tiles_x.setToolTip(i18n("Set the number of tiles horizontally"))
        self.num_tiles_y.setToolTip(i18n("Set the number of tiles vertically"))
        self.tile_ratio.setToolTip(i18n("Set the tile format ratio (width/height)"))
        self.clear_guides.setToolTip(i18n("Clear existing guides before adding new ones"))
        self.lock_guides.setToolTip(i18n("Lock guides so they are not accidentally moved"))
        self.snap_guides.setToolTip(i18n("Toggle the 'View > Snap To... > Snap to Guides' option"))

        # Fill the comboboxes with the units
        self.margin_l_unit.addItems(self.UNITS)
        self.margin_r_unit.addItems(self.UNITS)
        self.margin_t_unit.addItems(self.UNITS)
        self.margin_b_unit.addItems(self.UNITS)
        self.gutter_x_unit.addItems(self.UNITS)
        self.gutter_y_unit.addItems(self.UNITS)

        self.margin_l_params = {"sbox": self.margin_l, "cbox": self.margin_l_unit, "idx": -1, "doc_size": self.doc_size_x}
        self.margin_r_params = {"sbox": self.margin_r, "cbox": self.margin_r_unit, "idx": -1, "doc_size": self.doc_size_x}
        self.margin_t_params = {"sbox": self.margin_t, "cbox": self.margin_t_unit, "idx": -1, "doc_size": self.doc_size_y}
        self.margin_b_params = {"sbox": self.margin_b, "cbox": self.margin_b_unit, "idx": -1, "doc_size": self.doc_size_y}
        self.gutter_x_params = {"sbox": self.gutter_x, "cbox": self.gutter_x_unit, "idx": -1, "doc_size": self.doc_size_x}
        self.gutter_y_params = {"sbox": self.gutter_y, "cbox": self.gutter_y_unit, "idx": -1, "doc_size": self.doc_size_y}

        # Create a grid layout to organize the fields
        self.margin_grid_layout = QGridLayout()
        self.margin_grid_layout.addWidget(QLabel(i18n("Left Margin")), 0, 0, Qt.AlignRight)
        self.margin_grid_layout.addWidget(self.margin_l, 0, 1)
        self.margin_grid_layout.addWidget(self.margin_l_unit, 0, 2)
        self.margin_grid_layout.addWidget(QLabel(i18n("Right Margin")), 0, 3, Qt.AlignRight)
        self.margin_grid_layout.addWidget(self.margin_r, 0, 4)
        self.margin_grid_layout.addWidget(self.margin_r_unit, 0, 5)
        self.margin_grid_layout.addWidget(QLabel(i18n("Top Margin")), 1, 0, Qt.AlignRight)
        self.margin_grid_layout.addWidget(self.margin_t, 1, 1)
        self.margin_grid_layout.addWidget(self.margin_t_unit, 1, 2)
        self.margin_grid_layout.addWidget(QLabel(i18n("Bottom Margin")), 1, 3, Qt.AlignRight)
        self.margin_grid_layout.addWidget(self.margin_b, 1, 4)
        self.margin_grid_layout.addWidget(self.margin_b_unit, 1, 5)
        self.margin_grid_layout.addWidget(QLabel(i18n("Min. Vert. Gutter")), 2, 0, Qt.AlignRight)
        self.margin_grid_layout.addWidget(self.gutter_x, 2, 1)
        self.margin_grid_layout.addWidget(self.gutter_x_unit, 2, 2)
        self.margin_grid_layout.addWidget(QLabel(i18n("Min. Horz. Gutter")), 2, 3, Qt.AlignRight)
        self.margin_grid_layout.addWidget(self.gutter_y, 2, 4)
        self.margin_grid_layout.addWidget(self.gutter_y_unit, 2, 5)

        # Display the grid layout in a group box
        self.margin_grid_gbox = QGroupBox(i18n("Margins and Gutters"))
        self.margin_grid_gbox.setLayout(self.margin_grid_layout)

        self.tile_grid_layout = QHBoxLayout()
        self.tile_grid_layout.addWidget(QLabel(i18n("Columns")))
        self.tile_grid_layout.addWidget(self.num_tiles_x)
        self.tile_grid_layout.addStretch()
        self.tile_grid_layout.addWidget(QLabel(i18n("Rows")))
        self.tile_grid_layout.addWidget(self.num_tiles_y)
        self.tile_grid_layout.addStretch()
        self.tile_grid_layout.addWidget(QLabel(i18n("Format ratio (w/h)")))
        self.tile_grid_layout.addWidget(self.tile_ratio)

        # Surround tile_grid_layout by a frame
        self.tile_grid_gbox = QGroupBox(i18n("Tiles"))
        self.tile_grid_gbox.setLayout(self.tile_grid_layout)

        # Add save and load buttons
        self.save_button = QPushButton(i18n("Save Preset"))
        self.load_button = QPushButton(i18n("Load Preset"))
        self.default_button = QPushButton(i18n("Default"))

        self.save_button.setToolTip(i18n("Save current settings as a preset"))
        self.load_button.setToolTip(i18n("Load settings from a preset"))
        self.default_button.setToolTip(i18n("Restore default settings"))

        self.save_button.clicked.connect(self.save_preset)
        self.load_button.clicked.connect(self.load_preset)
        self.default_button.clicked.connect(self.default_preset)

        self.preset_layout = QHBoxLayout()
        self.preset_layout.addWidget(self.save_button)
        self.preset_layout.addWidget(self.load_button)
        self.preset_layout.addWidget(self.default_button)
        self.preset_layout.addStretch()

        self.checkbox_layout = QHBoxLayout()
        self.checkbox_layout.addStretch()
        self.checkbox_layout.addWidget(self.clear_guides, Qt.AlignRight)
        self.checkbox_layout.addWidget(self.lock_guides, Qt.AlignRight)
        self.checkbox_layout.addWidget(self.snap_guides, Qt.AlignRight)

        self.mix_layout = QHBoxLayout()
        self.mix_layout.addLayout(self.preset_layout)
        self.mix_layout.addLayout(self.checkbox_layout)

        self.dlg_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dlg_buttons.accepted.connect(self.on_accept)
        self.dlg_buttons.rejected.connect(self.reject)

        self.dlg_button_layout = QHBoxLayout()
        self.dlg_button_layout.addWidget(self.dlg_buttons)

        self.layout.addWidget(self.margin_grid_gbox)
        self.layout.addWidget(self.tile_grid_gbox)
        self.layout.addLayout(self.mix_layout)
        self.layout.addLayout(self.dlg_button_layout)

        self.setLayout(self.layout)

        # Values converted in pixels when closing the dialog
        self.ret_margin_l_px = 0
        self.ret_margin_r_px = 0
        self.ret_margin_t_px = 0
        self.ret_margin_b_px = 0
        self.ret_gutter_x_px = 0
        self.ret_gutter_y_px = 0
        self.ret_num_tiles_x = 0
        self.ret_num_tiles_y = 0
        self.ret_tile_ratio = 0

        # Load the last used preset on initialization
        self.load_last_preset()

        # Connect the comboboxes to on_combobox_index_changed with an indirection to allow more parameters
        self.margin_l_unit.currentIndexChanged.connect(lambda new_idx, params=self.margin_l_params: self.on_combobox_index_changed(new_idx, params))
        self.margin_r_unit.currentIndexChanged.connect(lambda new_idx, params=self.margin_r_params: self.on_combobox_index_changed(new_idx, params))
        self.margin_t_unit.currentIndexChanged.connect(lambda new_idx, params=self.margin_t_params: self.on_combobox_index_changed(new_idx, params))
        self.margin_b_unit.currentIndexChanged.connect(lambda new_idx, params=self.margin_b_params: self.on_combobox_index_changed(new_idx, params))
        self.gutter_x_unit.currentIndexChanged.connect(lambda new_idx, params=self.gutter_x_params: self.on_combobox_index_changed(new_idx, params))
        self.gutter_y_unit.currentIndexChanged.connect(lambda new_idx, params=self.gutter_y_params: self.on_combobox_index_changed(new_idx, params))

    def on_combobox_index_changed(self, new_idx, params):
        #QMessageBox.information(None, PLUGIN_DIALOG_TITLE, f"Combobox index changed to {str(new_idx)}, old index {str(params["idx"])}, size {str(params["doc_size"])}")
        old_val = params["sbox"].value()
        old_unit = params["cbox"].itemText(params["idx"])
        doc_size = params["doc_size"]
        old_val_px = self.convert_value_to_pixels(old_val, old_unit, doc_size)

        params["idx"] = new_idx
        self.update_sbox_range(params)
        new_unit = params["cbox"].currentText()
        new_val = self.convert_pixels_to_value(old_val_px, new_unit, doc_size)
        params["sbox"].setValue(new_val)

    def on_accept(self):
        self.save_last_preset(self.get_current_preset())
        try:
            self.update_return_values()
        except ValueError:
            QMessageBox.warning(None, PLUGIN_DIALOG_TITLE, i18n("Invalid input. Please enter valid numbers."))
        else:
            max_tile_size_x = (self.doc_size_x - self.ret_margin_l_px - self.ret_margin_r_px - (self.ret_num_tiles_x - 1) * self.ret_gutter_x_px) / self.ret_num_tiles_x
            max_tile_size_y = (self.doc_size_y - self.ret_margin_t_px - self.ret_margin_b_px - (self.ret_num_tiles_y - 1) * self.ret_gutter_y_px) / self.ret_num_tiles_y

            if max_tile_size_x < 1 or max_tile_size_y < 1:
                # Highlight the fields in red if the grid parameters are too big for the document size
                if max_tile_size_x < 1:
                    self.margin_l.setStyleSheet("color: red;")
                    self.margin_r.setStyleSheet("color: red;")
                    self.gutter_x.setStyleSheet("color: red;")
                if max_tile_size_y < 1:
                    self.margin_t.setStyleSheet("color: red;")
                    self.margin_b.setStyleSheet("color: red;")
                    self.gutter_y.setStyleSheet("color: red;")

                QMessageBox.warning(None, PLUGIN_DIALOG_TITLE, i18n("The specified grid parameters are too big for the document size. Please check the margins and gutter sizes indicated in red."))

                # Reset the fields to their original color
                self.margin_l.setStyleSheet("")
                self.margin_r.setStyleSheet("")
                self.margin_t.setStyleSheet("")
                self.margin_b.setStyleSheet("")
                self.gutter_x.setStyleSheet("")
                self.gutter_y.setStyleSheet("")
            else:
                self.accept()

    def save_preset(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, i18n("Save Preset"), "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            preset = self.get_current_preset()
            with open(file_name, 'w') as file:
                json.dump(preset, file)

    def load_preset(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, i18n("Load Preset"), "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                preset = json.load(file)
                self.apply_preset(preset)

    def default_preset(self):
        self.apply_preset({
            "margin_l": str(self.DEFAULT_MARGIN_L_PC),
            "margin_l_unit": self.UNIT_PC,
            "margin_r": str(self.DEFAULT_MARGIN_R_PC),
            "margin_r_unit": self.UNIT_PC,
            "margin_t": str(self.DEFAULT_MARGIN_T_PC),
            "margin_t_unit": self.UNIT_PC,
            "margin_b": str(self.DEFAULT_MARGIN_B_PC),
            "margin_b_unit": self.UNIT_PC,
            "gutter_x": str(self.DEFAULT_GUTTER_X_PC),
            "gutter_x_unit": self.UNIT_PC,
            "gutter_y": str(self.DEFAULT_GUTTER_Y_PC),
            "gutter_y_unit": self.UNIT_PC,
            "num_tiles_x": str(self.DEFAULT_NUM_TILES_X),
            "num_tiles_y": str(self.DEFAULT_NUM_TILES_Y),
            "tile_ratio": str(self.DEFAULT_TILE_RATIO),
            "clear_guides": str(self.DEFAULT_CLEAR_GUIDES),
            "lock_guides": str(self.DEFAULT_LOCK_GUIDES),
            "snap_guides": str(self.DEFAULT_SNAP_GUIDES)
        })

    def get_current_preset(self):
        return {
            "margin_l": self.margin_l.value(),
            "margin_l_unit": self.margin_l_unit.currentText(),
            "margin_r": self.margin_r.value(),
            "margin_r_unit": self.margin_r_unit.currentText(),
            "margin_t": self.margin_t.value(),
            "margin_t_unit": self.margin_t_unit.currentText(),
            "margin_b": self.margin_b.value(),
            "margin_b_unit": self.margin_b_unit.currentText(),
            "gutter_x": self.gutter_x.value(),
            "gutter_x_unit": self.gutter_x_unit.currentText(),
            "gutter_y": self.gutter_y.value(),
            "gutter_y_unit": self.gutter_y_unit.currentText(),
            "num_tiles_x": self.num_tiles_x.value(),
            "num_tiles_y": self.num_tiles_y.value(),
            "tile_ratio": self.tile_ratio.value(),
            "clear_guides": self.clear_guides.isChecked(),
            "lock_guides": self.lock_guides.isChecked(),
            "snap_guides": self.snap_guides.isChecked()
        }

    def apply_preset(self, preset):
        # Set the text of unit comboboxes
        self.margin_l_unit.setCurrentText(preset.get("margin_l_unit", self.UNIT_PC))
        self.margin_r_unit.setCurrentText(preset.get("margin_r_unit", self.UNIT_PC))
        self.margin_t_unit.setCurrentText(preset.get("margin_t_unit", self.UNIT_PC))
        self.margin_b_unit.setCurrentText(preset.get("margin_b_unit", self.UNIT_PC))
        self.gutter_x_unit.setCurrentText(preset.get("gutter_x_unit", self.UNIT_PC))
        self.gutter_y_unit.setCurrentText(preset.get("gutter_y_unit", self.UNIT_PC))

        # Store the current index of all comboboxes for future use
        self.margin_l_params["idx"] = self.margin_l_unit.currentIndex()
        self.margin_r_params["idx"] = self.margin_r_unit.currentIndex()
        self.margin_t_params["idx"] = self.margin_t_unit.currentIndex()
        self.margin_b_params["idx"] = self.margin_b_unit.currentIndex()
        self.gutter_x_params["idx"] = self.gutter_x_unit.currentIndex()
        self.gutter_y_params["idx"] = self.gutter_y_unit.currentIndex()

        # Update the spinboxes range
        self.update_sbox_range(self.margin_l_params)
        self.update_sbox_range(self.margin_r_params)
        self.update_sbox_range(self.margin_t_params)
        self.update_sbox_range(self.margin_b_params)
        self.update_sbox_range(self.gutter_x_params)
        self.update_sbox_range(self.gutter_y_params)

        # Set the values of the spinboxes and checkboxes
        self.margin_l.setValue(float(preset.get("margin_l", self.DEFAULT_MARGIN_L_PC)))
        self.margin_r.setValue(float(preset.get("margin_r", self.DEFAULT_MARGIN_R_PC)))
        self.margin_t.setValue(float(preset.get("margin_t", self.DEFAULT_MARGIN_T_PC)))
        self.margin_b.setValue(float(preset.get("margin_b", self.DEFAULT_MARGIN_B_PC)))
        self.gutter_x.setValue(float(preset.get("gutter_x", self.DEFAULT_GUTTER_X_PC)))
        self.gutter_y.setValue(float(preset.get("gutter_y", self.DEFAULT_GUTTER_Y_PC)))
        self.num_tiles_x.setValue(int(preset.get("num_tiles_x", self.DEFAULT_NUM_TILES_X)))
        self.num_tiles_y.setValue(int(preset.get("num_tiles_y", self.DEFAULT_NUM_TILES_Y)))
        self.tile_ratio.setValue(float(preset.get("tile_ratio", self.DEFAULT_TILE_RATIO)))
        self.clear_guides.setChecked(bool(preset.get("clear_guides", self.DEFAULT_CLEAR_GUIDES)))
        self.lock_guides.setChecked(bool(preset.get("lock_guides", self.DEFAULT_LOCK_GUIDES)))
        self.snap_guides.setChecked(bool(preset.get("snap_guides", self.DEFAULT_SNAP_GUIDES)))
        
    def save_last_preset(self, preset):
        last_preset_path = os.path.join(os.path.expanduser("~"), self.LAST_PRESET_FILENAME + ".json")
        with open(last_preset_path, 'w') as file:
            json.dump(preset, file)

    def load_last_preset(self):
        last_preset_path = os.path.join(os.path.expanduser("~"), self.LAST_PRESET_FILENAME + ".json")
        try:
            with open(last_preset_path, 'r') as file:
                preset = json.load(file)
                self.apply_preset(preset)
        except FileNotFoundError:
            self.default_preset()

    def update_return_values(self):
        self.ret_margin_l_px = self.convert_value_to_pixels(self.margin_l.value(), self.margin_l_unit.currentText(), self.doc_size_x)
        self.ret_margin_r_px = self.convert_value_to_pixels(self.margin_r.value(), self.margin_r_unit.currentText(), self.doc_size_x)
        self.ret_margin_t_px = self.convert_value_to_pixels(self.margin_t.value(), self.margin_t_unit.currentText(), self.doc_size_y)
        self.ret_margin_b_px = self.convert_value_to_pixels(self.margin_b.value(), self.margin_b_unit.currentText(), self.doc_size_y)
        self.ret_gutter_x_px = self.convert_value_to_pixels(self.gutter_x.value(), self.gutter_x_unit.currentText(), self.doc_size_x)
        self.ret_gutter_y_px = self.convert_value_to_pixels(self.gutter_y.value(), self.gutter_y_unit.currentText(), self.doc_size_y)
        self.ret_num_tiles_x = self.num_tiles_x.value()
        self.ret_num_tiles_y = self.num_tiles_y.value()
        self.ret_tile_ratio = self.tile_ratio.value()

    def convert_value_to_pixels(self, value, unit, doc_size):
        if unit == self.UNIT_PX:
            return value  # Already in pixels
        elif unit == self.UNIT_IN:
            return value * self.doc_ppi  # Use provided ppi for conversion
        elif unit == self.UNIT_CM:
            return value * (self.doc_ppi / 2.54)  # 1 inch = 2.54 cm
        elif unit == self.UNIT_PC:
            return value * 0.01 * doc_size
        else:
            raise ValueError

    def convert_pixels_to_value(self, value, unit, doc_size):
        if unit == self.UNIT_PX:
            return value  # Already in pixels
        elif unit == self.UNIT_IN:
            return value / self.doc_ppi
        elif unit == self.UNIT_CM:
            return value / (self.doc_ppi / 2.54)
        elif unit == self.UNIT_PC:
            return value * 100.0 / doc_size
        else:
            raise ValueError

    def update_sbox_range(self, params):
        sbox = params["sbox"]
        unit = params["cbox"].currentText()
        doc_size = params["doc_size"]

        if unit == self.UNIT_PX:
            sbox.setRange(0.0, doc_size)
        elif unit == self.UNIT_IN:
            sbox.setRange(0.0, doc_size / self.doc_ppi)
        elif unit == self.UNIT_CM:
            sbox.setRange(0.0, doc_size / (self.doc_ppi / 2.54))
        elif unit == self.UNIT_PC:
            sbox.setRange(0.0, 100.0)
        else:
            raise ValueError


class TileGridExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction(EXTENSION_ID, PLUGIN_MENU_ENTRY, "tools/scripts")
        action.triggered.connect(self.add_tile_grid)

    def add_tile_grid(self):
        doc = Krita.instance().activeDocument()
        if doc is None:
            QMessageBox.information(None, PLUGIN_DIALOG_TITLE, i18n("No document is currently opened."))
            return
        #QMessageBox.information(None, PLUGIN_DIALOG_TITLE, str(dir(doc)))
        
        doc_size_x = doc.width()
        doc_size_y = doc.height()
        doc_ppi = doc.resolution()

        dialog = TileGridDialog(doc_size_x, doc_size_y, doc_ppi)
        if not dialog.exec_() == QDialog.Accepted:
            return
        
        # Get the values from the dialog
        margin_l = dialog.ret_margin_l_px  # float
        margin_r = dialog.ret_margin_r_px  # float
        margin_t = dialog.ret_margin_t_px  # float
        margin_b = dialog.ret_margin_b_px  # float
        min_gutter_x = dialog.ret_gutter_x_px  # float
        min_gutter_y = dialog.ret_gutter_y_px  # float
        num_tiles_x = dialog.ret_num_tiles_x  # int
        num_tiles_y = dialog.ret_num_tiles_y  # int
        tile_ratio = dialog.ret_tile_ratio  # float
        
        # Make sure guides are visible and locked, then snap to the guides
        if not doc.guidesVisible():
            Krita.instance().action('view_show_guides').trigger()
        
        if dialog.lock_guides.isChecked() ^ doc.guidesLocked():
            Krita.instance().action('view_lock_guides').trigger()
        
        if dialog.lock_guides.isChecked(): #^ doc.snapToGuides():
            Krita.instance().action('view_snap_to_guides').trigger()
        
        # Calculate the maximum tile size that fits the document (in percentage)
        max_tile_size_x = (doc_size_x - margin_l - margin_r - (num_tiles_x - 1) * min_gutter_x) / num_tiles_x
        max_tile_size_y = (doc_size_y - margin_t - margin_b - (num_tiles_y - 1) * min_gutter_y) / num_tiles_y

        # Already checked in the dialog, but just in case
        #assert max_tile_size_x > 0 and max_tile_size_y > 0, f"Invalid grid parameters max_tile_size_x={max_tile_size_x}, max_tile_size_y={max_tile_size_y}"

        # Calculate the tile height based on the tile ratio
        tile_size_y = max_tile_size_x / tile_ratio # float
        gutter_x, gutter_y, pad_l, pad_t = 0, 0, 0, 0

        # If the tiles height is too big, we need to adjust the tile size (and the gutter size) so that the tiles height is limited to max_tile_size_y
        if tile_size_y <= max_tile_size_y:
            tile_size_x = max_tile_size_x
            if num_tiles_x > 1: # If there is more than one column, we need to calculate the gutter size
                gutter_x = min_gutter_x
                gutter_y = (doc_size_y - margin_t - margin_b - num_tiles_y * tile_size_y) / (num_tiles_y - 1)
            else: # If there is only one column, we need to calculate the padding size
                pad_t = (doc_size_y - margin_t - margin_b - tile_size_y) / 2
        else:
            #QMessageBox.information(None, PLUGIN_DIALOG_TITLE, "tile_size_y > max_tile_size_y")
            tile_size_x = max_tile_size_y * tile_ratio
            tile_size_y = max_tile_size_y
            if num_tiles_x > 1: # If there is more than one column, we need to calculate the gutter size
                gutter_x = (doc_size_x - margin_l - margin_r - num_tiles_x * tile_size_x) / (num_tiles_x - 1)
                gutter_y = min_gutter_y
            else: # If there is only one column, we need to calculate the padding size
                pad_l = (doc_size_x - margin_l - margin_r - tile_size_x) / 2

        # Lists of guide positions (in pixels from the left or top of the document)
        guides_x = [] if dialog.clear_guides.isChecked() else doc.verticalGuides()
        guides_y = [] if dialog.clear_guides.isChecked() else doc.horizontalGuides()

        # Enclose each tile in guides
        guides_x.extend(self.setup_guides(margin_l, pad_l, gutter_x, num_tiles_x, tile_size_x))
        guides_y.extend(self.setup_guides(margin_t, pad_t, gutter_y, num_tiles_y, tile_size_y))

        doc.setVerticalGuides(guides_x)
        doc.setHorizontalGuides(guides_y)

    def setup_guides(self, margin, pad, gutter, num_tiles, tile_size):
        guides = []

        # Enclose each tile in guides
        pos = margin + pad
        for _ in range(num_tiles):
            #if not pos in guides:
            guides.append(pos)
            pos += tile_size
            #if not pos in guides:
            guides.append(pos)
            pos += gutter

        return guides

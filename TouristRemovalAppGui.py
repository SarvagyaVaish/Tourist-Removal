import sys
import os
from PyQt4.QtGui import *
from CommandLineExecutor import CommandLineExecutor
from ImageAligner import ImageAligner
from ImageBlender import ImageBlender
from ImageSource import ImageSource
import cv2
import scipy
import numpy as np


class TouristRemovalGui:

    def __init__(self):
        self.primary = None
        self.output_highlight = None
        self.output_highlight_merge = None
        self.visible_image = None

        self.command_line_executor = CommandLineExecutor(self)
        self.image_aligner = ImageAligner()
        self.image_blender = ImageBlender()
        self.image_source = ImageSource()
        self.application = QApplication(sys.argv)
        self.window = QMainWindow()
        self.image_label = QLabel(self.window)

        self.scroll_area = QScrollArea(self.window)
        self.images_combo = QComboBox(self.window)
        self.images_combo.activated['QString'].connect(self.handle_image_change)

        self.button_highlighted = QAction('Show Highlighted Area', self.window)
        self.button_highlighted_merged = QAction('Show Highlighted Merged Area', self.window)
        self.button_unaltered_primary = QAction('Show Unaltered Primary Image', self.window)
        self.button_merge = QAction('Merge', self.window)
        self.button_update_merge = QPushButton('Update Merge Area', self.window)

        self.input_x = QLineEdit(self.window)
        self.input_y = QLineEdit(self.window)
        self.input_width = QLineEdit(self.window)
        self.input_height = QLineEdit(self.window)

        self.int_validator = None

    def run(self):
        self.window.setFixedSize(320, 240)
        self.window.setWindowTitle("Tourist Removal App")
        self.setup_main_menu()
        self.setup_scroll_area_and_combo()
        self.setup_inputs()

        self.window.show()
        sys.exit(self.application.exec_())

    def setup_inputs(self):
        self.input_x.setVisible(False)
        self.input_y.setVisible(False)
        self.input_width.setVisible(False)
        self.input_height.setVisible(False)

    def setup_scroll_area_and_combo(self):
        self.scroll_area.move(0, 20)
        self.scroll_area.setVisible(False)
        self.scroll_area.setWidget(self.image_label)
        self.images_combo.setVisible(False)
        self.button_update_merge.setVisible(False)
        self.button_update_merge.clicked.connect(self.update_merge)

    def setup_main_menu(self):
        main_menu = self.window.menuBar()
        main_menu.setNativeMenuBar(False)
        file_menu = main_menu.addMenu('&File')
        file_menu.addAction(self.build_import_source_button())
        file_menu.addAction(self.build_exit_button())
        file_menu.addAction(self.build_save_button())

        display_menu = main_menu.addMenu('&Display')
        display_menu.addAction(self.build_show_hightlighed_primary_button())
        display_menu.addAction(self.build_show_hightlighed_merged_button())
        display_menu.addAction(self.build_show_unaltered_primary_button())
        display_menu.addAction(self.build_show_merged_button())

    def build_import_source_button(self):
        button = QAction('Import Source Folder', self.window)
        button.setShortcut('Ctrl+I')
        button.setStatusTip('Set Source')
        button.triggered.connect(self.import_source)
        return button

    def build_save_button(self):
        button = QAction('Save Current Image', self.window)
        button.setShortcut('Ctrl+S')
        button.setStatusTip('Save Image')
        button.triggered.connect(self.save_image)
        return button

    def build_exit_button(self):
        button = QAction('Exit', self.window)
        button.setShortcut('Ctrl+Q')
        button.setStatusTip('Exit application')
        button.triggered.connect(self.window.close)
        return button

    def build_show_hightlighed_primary_button(self):
        self.button_highlighted.triggered.connect(lambda: self.set_label_image(self.output_highlight))
        self.button_highlighted.setEnabled(False)
        return self.button_highlighted

    def build_show_hightlighed_merged_button(self):
        self.button_highlighted_merged.triggered.connect(lambda: self.set_label_image(self.output_highlight_merge))
        self.button_highlighted_merged.setEnabled(False)
        return self.button_highlighted_merged

    def build_show_unaltered_primary_button(self):
        self.button_unaltered_primary.triggered.connect(lambda: self.set_label_image(self.primary))
        self.button_unaltered_primary.setEnabled(False)
        return self.button_unaltered_primary

    def build_show_merged_button(self):
        self.button_merge.triggered.connect(self.merge)
        self.button_merge.setEnabled(False)
        return self.button_merge

    def import_source(self) :
        loaded = self.image_source.load_images(str(QFileDialog.getExistingDirectory(self.window, 'Open Source Folder')))
        if loaded:
            self.primary = self.image_source.primary_image
            self.build_highlight_and_merged(0)
            self.set_label_image(self.primary)

            self.import_success_handler()
            print "Handle Success"
        else :
            print "Handle Error"

    def set_label_image(self, image, show_merge = True):
        if image is not None:
            self.visible_image = np.copy(image)
            self.image_label.setPixmap(QPixmap.fromImage(self.convert_opencv_to_qimage(self.visible_image, show_merge)))
            self.image_label.adjustSize()

    def import_success_handler(self):
        self.scroll_area.setVisible(True)
        shape = self.image_source.primary_image.shape;
        width = min(shape[1], 800)
        height = min(shape[0], 800)
        self.scroll_area.setFixedSize(width, height)
        self.window.setFixedSize(width, height + 80)

        self.images_combo.setVisible(True)
        for pos in range(len(self.image_source.secondary_images)):
            self.images_combo.addItem(str(pos))
        self.images_combo.move(20, height + 35)

        print shape
        self.input_x.setVisible(True)
        self.input_x.setPlaceholderText("x")
        self.input_x.setValidator(QIntValidator(0, shape[1], self.window))
        self.input_x.move(50, height + 35)

        self.input_y.setVisible(True)
        self.input_y.setPlaceholderText("y")
        self.input_y.setValidator(QIntValidator(0, shape[0], self.window))
        self.input_y.move(100, height + 35)

        self.input_width.setVisible(True)
        self.input_width.setPlaceholderText("width")
        self.input_width.setValidator(QIntValidator(0, shape[1], self.window))
        self.input_width.move(150, height + 35)

        self.input_height.setVisible(True)
        self.input_height.setPlaceholderText("height")
        self.input_height.setValidator(QIntValidator(0, shape[0], self.window))
        self.input_height.move(200, height + 35)
        self.input_height.setFixedWidth(50)

        self.button_update_merge.setVisible(True)
        self.button_update_merge.move(250, height + 35)

        self.button_highlighted.setEnabled(True)
        self.button_highlighted_merged.setEnabled(True)
        self.button_unaltered_primary.setEnabled(True)
        self.button_merge.setEnabled(True)

    def convert_opencv_to_qimage (self, cv_img, show_merge = True):
        img = np.copy(cv_img)
        height, width, bytes = img.shape
        bytes_per_line = bytes * width;

        cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)

        if show_merge:
            x = self.tr_int(self.input_x.text())
            y = self.tr_int(self.input_y.text())
            w = self.tr_int(self.input_width.text())
            h = self.tr_int(self.input_height.text())
            cv2.rectangle(img,(x, y),(x + w, y + h), (0, 255, 0))
        return QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)

    def handle_image_change (self, text):
        self.build_highlight_and_merged(int(text))
        self.set_label_image(self.primary)

    def build_highlight_and_merged(self, index):
        align = self.image_aligner.align_image(self.primary, self.image_source.secondary_images[index])
        self.output_highlight = np.copy(self.primary)
        self.output_highlight_merge = np.copy(self.primary)

        for row in range(len(align)):
            for col in range(len(align)):
                if align[row][col][0] > 0:
                    self.output_highlight_merge[row][col] = align[row][col]
                    self.output_highlight_merge[row, col, 0:1] = 0
                    self.output_highlight[row, col, 0:1] = 0

    def update_merge(self):
        self.set_label_image(self.visible_image)

    def tr_int(self, s):
        s = str(s).strip()
        return int(s) if s else 0

    def merge(self):
        mask_size = (self.primary.shape[0], self.primary.shape[1])
        x = self.tr_int(self.input_x.text())
        y = self.tr_int(self.input_y.text())
        w = self.tr_int(self.input_width.text())
        h = self.tr_int(self.input_height.text())
        mask_coordinates = (x, y, w, h)

        mask = self.image_blender.create_rectangular_mask(mask_size, mask_coordinates)

        new_result_image = self.image_blender.blend(self.primary, self.image_source.secondary_images[int(self.images_combo.currentText())], mask)
        self.set_label_image(new_result_image, False)

    def save_image(self):
        cv2.imwrite("result.jpg", self.visible_image)

if __name__ == "__main__":
    gui = TouristRemovalGui()
    gui.run()
    cv2.waitKey(0)



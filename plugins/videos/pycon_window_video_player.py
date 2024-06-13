import os
from os import path

import cv2
import numpy as np
from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QMdiSubWindow, QVBoxLayout, QWidget

from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from plugins_std.pycon_time import PyConTime


class PyConWindowVideoPlayer(PyConPluginBase):

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        uic.loadUiType("plugins/videos/pycon_window_video_player.ui", self)
        self.setWindowTitle("Video Player")

        self.win_widget = None
        self.video_label = None
        self.video_time_msec = 0
        self.cap = None

        self.__initUI(file_path=params.video_name)

    def __initUI(self, file_path):
        self.win_widget = QWidget()
        self.setWidget(self.win_widget)
        self.layout = QVBoxLayout(self.win_widget)
        self.win_widget.setLayout(self.layout)

        self.video_label = QLabel()
        # self.video_label.resize(self.win_widget.width(), self.win_widget.height())
        self.layout.addWidget(self.video_label)
        self.setMinimumSize(1, 1)

        self.video_time_msec = 0

        check_file = os.path.exists(file_path)

        if check_file:
            self.cap = cv2.VideoCapture(file_path)
            # self.setWindowTitle(f"Video Player - {path.basename(file_path)}")

            self.slider_value_changed(PyConTime(0, 0, PyConTime.PyConTimeUnit.M_SEC))
        else:
            logger().warning("video file not found")

    @QtCore.pyqtSlot(PyConTime)
    def slider_value_changed(self, time: PyConTime):

        self.video_time_msec = time.get_time_diff_msec()

        self.__display_frame()

    def get_video_duration_sec(self):
        duration_sec = 0
        if self.cap is not None:
            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            duration_sec = frame_count / fps

        return duration_sec

    def closeEvent(self, event):
        self.cap.release()
        super().closeEvent(event)

    def __display_frame(self):
        if self.cap is not None:
            if not self.cap.isOpened():
                return

            self.cap.set(cv2.CAP_PROP_POS_MSEC, self.video_time_msec)
            ret, frame = self.cap.read()

            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = frame
                height, width, channels = frame_rgb.shape
                max_width = self.video_label.width()
                max_height = self.video_label.height()

                q_img = QImage(frame_rgb.data, width, height, 3 * width, QImage.Format_RGB888)

                if max_height != 1:
                    if width > max_width or height > max_height:
                        q_img = q_img.scaled(max_width, max_height)

                self.video_label.setPixmap(QPixmap.fromImage(q_img))
                self.video_label.adjustSize()

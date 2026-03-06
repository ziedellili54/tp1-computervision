from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
import cv2
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

qtcreator_file = "design.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)


class DesignWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(DesignWindow, self).__init__()
        self.setupUi(self)

        self.image = None
        self.gray_image = None

        for label in [self.OriginalImg, self.RedChannel, self.GreenChannel,
                      self.BlueChannel, self.ColorHist, self.GrayImg, self.GrayHist]:
            label.setScaledContents(True)

        self.Browse.clicked.connect(self.get_image)
        self.DisplayRedChan.clicked.connect(self.showRedChannel)
        self.DisplayGreenChan.clicked.connect(self.showGreenChannel)
        self.DisplayBleueChan.clicked.connect(self.showBlueChannel)
        self.DisplayColorHist.clicked.connect(self.show_HistColor)
        self.DisplayGrayImg.clicked.connect(self.show_UpdatedImgGray)
        self.DisplayGrayHist.clicked.connect(self.show_HistGray)

    def convert_cv_qt(self, cv_image):
        cv_image = np.ascontiguousarray(cv_image)
        if len(cv_image.shape) == 2:
            cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2RGB)
        else:
            cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        h, w, ch = cv_image_rgb.shape
        raw = cv_image_rgb.tobytes()
        qt_image = QtGui.QImage(raw, w, h, ch * w, QtGui.QImage.Format_RGB888)
        qt_image = qt_image.copy()
        return QPixmap.fromImage(qt_image)

    def display_on_label(self, label, pixmap):
        label.setPixmap(pixmap.scaled(label.width(), label.height()))

    def showDimensions(self):
        if self.image is not None:
            if len(self.image.shape) == 2:
                h, w = self.image.shape
                channels = 1
            else:
                h, w, channels = self.image.shape
            self.Dimensions.setText(
                f"Hauteur: {h}\nLargeur: {w}\nNombre de canaux: {channels}"
            )

    def get_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir une image", "", "Images (*.jpg *.jpeg *.png)"
        )
        if file_path:
            self.image = cv2.imread(file_path)
            if self.image is None:
                return
            pixmap = self.convert_cv_qt(self.image)
            self.display_on_label(self.OriginalImg, pixmap)
            self.showDimensions()

    def showRedChannel(self):
        if self.image is not None:
            red_img = self.image.copy()
            red_img[:, :, 0] = 0
            red_img[:, :, 1] = 0
            pixmap = self.convert_cv_qt(red_img)
            self.display_on_label(self.RedChannel, pixmap)

    def showGreenChannel(self):
        if self.image is not None:
            green_img = self.image.copy()
            green_img[:, :, 0] = 0
            green_img[:, :, 2] = 0
            pixmap = self.convert_cv_qt(green_img)
            self.display_on_label(self.GreenChannel, pixmap)

    def showBlueChannel(self):
        if self.image is not None:
            blue_img = self.image.copy()
            blue_img[:, :, 1] = 0
            blue_img[:, :, 2] = 0
            pixmap = self.convert_cv_qt(blue_img)
            self.display_on_label(self.BlueChannel, pixmap)

    def show_HistColor(self):
        if self.image is not None:
            plt.figure()
            colors = ('b', 'g', 'r')
            for i, col in enumerate(colors):
                hist = cv2.calcHist([self.image], [i], None, [256], [0, 256])
                plt.plot(hist, color=col)
            plt.title("Histogramme Couleur")
            plt.xlabel("Intensite")
            plt.ylabel("Frequence")
            plt.savefig("Color_Histogram.png")
            plt.close()
            hist_img = cv2.imread("Color_Histogram.png")
            pixmap = self.convert_cv_qt(hist_img)
            self.display_on_label(self.ColorHist, pixmap)

    def getContrast(self):
        try:
            return float(self.Contrast.toPlainText())
        except ValueError:
            return 1.0

    def getBrightness(self):
        try:
            return float(self.Brightness.toPlainText())
        except ValueError:
            return 0.0

    def show_UpdatedImgGray(self):
        if self.image is not None:
            alpha = self.getContrast()
            beta = self.getBrightness()
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            gray_updated = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
            self.gray_image = gray_updated
            pixmap = self.convert_cv_qt(gray_updated)
            self.display_on_label(self.GrayImg, pixmap)

    def calc_HistGray(self):
        alpha = self.getContrast()
        beta = self.getBrightness()
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    def show_HistGray(self):
        if self.image is not None:
            gray_img = self.calc_HistGray()
            hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
            plt.figure()
            plt.plot(hist, color='gray')
            plt.title("Histogramme Niveaux de Gris")
            plt.xlabel("Intensite")
            plt.ylabel("Frequence")
            plt.savefig("Gray_Histogram.png")
            plt.close()
            hist_img = cv2.imread("Gray_Histogram.png")
            pixmap = self.convert_cv_qt(hist_img)
            self.display_on_label(self.GrayHist, pixmap)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DesignWindow()
    window.show()
    sys.exit(app.exec_())
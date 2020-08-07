from PyQt5 import QtGui, QtWidgets, QtCore

from ui.py.about_dialog import Ui_about_dialog as AboutForm
import revisions


class AboutDialog(QtWidgets.QDialog):

    def __init__(self, a_parent=None):
        super().__init__(a_parent)

        self.ui = AboutForm()
        self.ui.setupUi(self)
        self.show()

        self.ui.version_label.setText(f"Версия программы: {revisions.Revisions.clb_autocalibration}")

        self.ui.close_button.clicked.connect(self.reject)

    def __del__(self):
        print("About deleted")

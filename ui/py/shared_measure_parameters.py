# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/edit_shared_measure_parameters_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_shared_measure_parameters(object):
    def setupUi(self, shared_measure_parameters):
        shared_measure_parameters.setObjectName("shared_measure_parameters")
        shared_measure_parameters.resize(338, 388)
        font = QtGui.QFont()
        font.setPointSize(10)
        shared_measure_parameters.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        shared_measure_parameters.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(shared_measure_parameters)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(shared_measure_parameters)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_10 = QtWidgets.QLabel(self.groupBox)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 9, 0, 1, 1)
        self.mul_30_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mul_30_spinbox.sizePolicy().hasHeightForWidth())
        self.mul_30_spinbox.setSizePolicy(sizePolicy)
        self.mul_30_spinbox.setDecimals(18)
        self.mul_30_spinbox.setMinimum(1e-06)
        self.mul_30_spinbox.setMaximum(1000.0)
        self.mul_30_spinbox.setSingleStep(0.1)
        self.mul_30_spinbox.setProperty("value", 31.0)
        self.mul_30_spinbox.setObjectName("mul_30_spinbox")
        self.gridLayout.addWidget(self.mul_30_spinbox, 3, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 8, 0, 1, 1)
        self.div_350_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.div_350_spinbox.sizePolicy().hasHeightForWidth())
        self.div_350_spinbox.setSizePolicy(sizePolicy)
        self.div_350_spinbox.setDecimals(18)
        self.div_350_spinbox.setMinimum(1e-06)
        self.div_350_spinbox.setMaximum(1000.0)
        self.div_350_spinbox.setSingleStep(0.1)
        self.div_350_spinbox.setProperty("value", 35.5)
        self.div_350_spinbox.setObjectName("div_350_spinbox")
        self.gridLayout.addWidget(self.div_350_spinbox, 7, 1, 1, 1)
        self.div_500_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.div_500_spinbox.sizePolicy().hasHeightForWidth())
        self.div_500_spinbox.setSizePolicy(sizePolicy)
        self.div_500_spinbox.setDecimals(18)
        self.div_500_spinbox.setMinimum(1e-06)
        self.div_500_spinbox.setMaximum(1000.0)
        self.div_500_spinbox.setSingleStep(0.1)
        self.div_500_spinbox.setProperty("value", 50.5)
        self.div_500_spinbox.setObjectName("div_500_spinbox")
        self.gridLayout.addWidget(self.div_500_spinbox, 6, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.coil_1_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.coil_1_spinbox.sizePolicy().hasHeightForWidth())
        self.coil_1_spinbox.setSizePolicy(sizePolicy)
        self.coil_1_spinbox.setDecimals(18)
        self.coil_1_spinbox.setMinimum(1e-06)
        self.coil_1_spinbox.setMaximum(1000.0)
        self.coil_1_spinbox.setSingleStep(0.1)
        self.coil_1_spinbox.setProperty("value", 1.0)
        self.coil_1_spinbox.setObjectName("coil_1_spinbox")
        self.gridLayout.addWidget(self.coil_1_spinbox, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.coil_10_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.coil_10_spinbox.sizePolicy().hasHeightForWidth())
        self.coil_10_spinbox.setSizePolicy(sizePolicy)
        self.coil_10_spinbox.setDecimals(18)
        self.coil_10_spinbox.setMinimum(1e-06)
        self.coil_10_spinbox.setMaximum(1000.0)
        self.coil_10_spinbox.setSingleStep(0.1)
        self.coil_10_spinbox.setProperty("value", 10.0)
        self.coil_10_spinbox.setObjectName("coil_10_spinbox")
        self.gridLayout.addWidget(self.coil_10_spinbox, 2, 1, 1, 1)
        self.coil_001_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.coil_001_spinbox.sizePolicy().hasHeightForWidth())
        self.coil_001_spinbox.setSizePolicy(sizePolicy)
        self.coil_001_spinbox.setDecimals(18)
        self.coil_001_spinbox.setMinimum(1e-06)
        self.coil_001_spinbox.setMaximum(1000.0)
        self.coil_001_spinbox.setSingleStep(0.1)
        self.coil_001_spinbox.setProperty("value", 0.01)
        self.coil_001_spinbox.setObjectName("coil_001_spinbox")
        self.gridLayout.addWidget(self.coil_001_spinbox, 0, 1, 1, 1)
        self.div_200_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.div_200_spinbox.sizePolicy().hasHeightForWidth())
        self.div_200_spinbox.setSizePolicy(sizePolicy)
        self.div_200_spinbox.setDecimals(18)
        self.div_200_spinbox.setMinimum(1e-06)
        self.div_200_spinbox.setMaximum(1000.0)
        self.div_200_spinbox.setSingleStep(0.1)
        self.div_200_spinbox.setProperty("value", 20.5)
        self.div_200_spinbox.setObjectName("div_200_spinbox")
        self.gridLayout.addWidget(self.div_200_spinbox, 8, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.mul_10_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mul_10_spinbox.sizePolicy().hasHeightForWidth())
        self.mul_10_spinbox.setSizePolicy(sizePolicy)
        self.mul_10_spinbox.setDecimals(18)
        self.mul_10_spinbox.setMinimum(1e-06)
        self.mul_10_spinbox.setMaximum(1000.0)
        self.mul_10_spinbox.setSingleStep(0.1)
        self.mul_10_spinbox.setProperty("value", 81.0)
        self.mul_10_spinbox.setObjectName("mul_10_spinbox")
        self.gridLayout.addWidget(self.mul_10_spinbox, 4, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 7, 0, 1, 1)
        self.div_650_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.div_650_spinbox.sizePolicy().hasHeightForWidth())
        self.div_650_spinbox.setSizePolicy(sizePolicy)
        self.div_650_spinbox.setDecimals(18)
        self.div_650_spinbox.setMinimum(1e-06)
        self.div_650_spinbox.setMaximum(1000.0)
        self.div_650_spinbox.setSingleStep(0.1)
        self.div_650_spinbox.setProperty("value", 65.5)
        self.div_650_spinbox.setObjectName("div_650_spinbox")
        self.gridLayout.addWidget(self.div_650_spinbox, 5, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 10, 0, 1, 1)
        self.div_55_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.div_55_spinbox.sizePolicy().hasHeightForWidth())
        self.div_55_spinbox.setSizePolicy(sizePolicy)
        self.div_55_spinbox.setPrefix("")
        self.div_55_spinbox.setSuffix("")
        self.div_55_spinbox.setDecimals(18)
        self.div_55_spinbox.setMinimum(1e-06)
        self.div_55_spinbox.setMaximum(1000.0)
        self.div_55_spinbox.setSingleStep(0.1)
        self.div_55_spinbox.setProperty("value", 5.5)
        self.div_55_spinbox.setObjectName("div_55_spinbox")
        self.gridLayout.addWidget(self.div_55_spinbox, 9, 1, 1, 1)
        self.div_40_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.div_40_spinbox.sizePolicy().hasHeightForWidth())
        self.div_40_spinbox.setSizePolicy(sizePolicy)
        self.div_40_spinbox.setDecimals(18)
        self.div_40_spinbox.setMinimum(1e-06)
        self.div_40_spinbox.setMaximum(1000.0)
        self.div_40_spinbox.setSingleStep(0.1)
        self.div_40_spinbox.setProperty("value", 4.0)
        self.div_40_spinbox.setObjectName("div_40_spinbox")
        self.gridLayout.addWidget(self.div_40_spinbox, 10, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setObjectName("buttons_layout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttons_layout.addItem(spacerItem)
        self.accept_button = QtWidgets.QPushButton(shared_measure_parameters)
        self.accept_button.setDefault(True)
        self.accept_button.setObjectName("accept_button")
        self.buttons_layout.addWidget(self.accept_button)
        self.cancel_button = QtWidgets.QPushButton(shared_measure_parameters)
        self.cancel_button.setObjectName("cancel_button")
        self.buttons_layout.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.buttons_layout)

        self.retranslateUi(shared_measure_parameters)
        QtCore.QMetaObject.connectSlotsByName(shared_measure_parameters)
        shared_measure_parameters.setTabOrder(self.accept_button, self.cancel_button)

    def retranslateUi(self, shared_measure_parameters):
        _translate = QtCore.QCoreApplication.translate
        shared_measure_parameters.setWindowTitle(_translate("shared_measure_parameters", "Общие параметры для всех измерений"))
        self.groupBox.setTitle(_translate("shared_measure_parameters", "Коэффициенты приборов"))
        self.label_10.setText(_translate("shared_measure_parameters", "Делитель 55 В"))
        self.label_8.setText(_translate("shared_measure_parameters", "Делитель 200 В"))
        self.label_5.setText(_translate("shared_measure_parameters", "Усилитель 10 мВ"))
        self.coil_1_spinbox.setSuffix(_translate("shared_measure_parameters", " Ом"))
        self.label_6.setText(_translate("shared_measure_parameters", "Делитель 650 В"))
        self.label_7.setText(_translate("shared_measure_parameters", "Делитель 500 В"))
        self.coil_10_spinbox.setSuffix(_translate("shared_measure_parameters", " Ом"))
        self.coil_001_spinbox.setSuffix(_translate("shared_measure_parameters", " Ом"))
        self.label_4.setText(_translate("shared_measure_parameters", "Усилитель 30 мВ"))
        self.label_3.setText(_translate("shared_measure_parameters", "Катушка 10 Ом"))
        self.label.setText(_translate("shared_measure_parameters", "Катушка 0,01 Ом"))
        self.label_2.setText(_translate("shared_measure_parameters", "Катушка 1 Ом"))
        self.label_9.setText(_translate("shared_measure_parameters", "Делитель 350 В"))
        self.label_11.setText(_translate("shared_measure_parameters", "Делитель 40 В"))
        self.accept_button.setText(_translate("shared_measure_parameters", "Принять"))
        self.cancel_button.setText(_translate("shared_measure_parameters", "Отмена"))
import icons_rc
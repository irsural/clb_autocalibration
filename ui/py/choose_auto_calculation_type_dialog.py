# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'choose_auto_calculation_type_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_choose_auto_calculation_type_dialog(object):
    def setupUi(self, choose_auto_calculation_type_dialog):
        choose_auto_calculation_type_dialog.setObjectName("choose_auto_calculation_type_dialog")
        choose_auto_calculation_type_dialog.resize(338, 155)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(choose_auto_calculation_type_dialog.sizePolicy().hasHeightForWidth())
        choose_auto_calculation_type_dialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(choose_auto_calculation_type_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_widget_layout = QtWidgets.QVBoxLayout()
        self.main_widget_layout.setSpacing(6)
        self.main_widget_layout.setObjectName("main_widget_layout")
        self.label = QtWidgets.QLabel(choose_auto_calculation_type_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.main_widget_layout.addWidget(self.label)
        self.verticalLayout.addLayout(self.main_widget_layout)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setObjectName("buttons_layout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttons_layout.addItem(spacerItem)
        self.add_button = QtWidgets.QPushButton(choose_auto_calculation_type_dialog)
        self.add_button.setObjectName("add_button")
        self.buttons_layout.addWidget(self.add_button)
        self.replace_button = QtWidgets.QPushButton(choose_auto_calculation_type_dialog)
        self.replace_button.setObjectName("replace_button")
        self.buttons_layout.addWidget(self.replace_button)
        self.cancel_button = QtWidgets.QPushButton(choose_auto_calculation_type_dialog)
        self.cancel_button.setObjectName("cancel_button")
        self.buttons_layout.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.buttons_layout)

        self.retranslateUi(choose_auto_calculation_type_dialog)
        QtCore.QMetaObject.connectSlotsByName(choose_auto_calculation_type_dialog)

    def retranslateUi(self, choose_auto_calculation_type_dialog):
        _translate = QtCore.QCoreApplication.translate
        choose_auto_calculation_type_dialog.setWindowTitle(_translate("choose_auto_calculation_type_dialog", "Выберите действие"))
        self.label.setText(_translate("choose_auto_calculation_type_dialog", "<html><head/><body><p>Выберите тип добавления коэффициентов.</p><p>При выборе <span style=\" font-weight:600;\">Дополнить</span> рассчитанные коэффициенты будут добавлены к уже существующим.</p><p>При выборе <span style=\" font-weight:600;\">Заменить</span> существующие коэффициенты будут стерты.</p></body></html>"))
        self.add_button.setText(_translate("choose_auto_calculation_type_dialog", "Дополнить"))
        self.replace_button.setText(_translate("choose_auto_calculation_type_dialog", "Заменить"))
        self.cancel_button.setText(_translate("choose_auto_calculation_type_dialog", "Отмена"))

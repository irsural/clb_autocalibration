# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_measure_parameters_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_edit_measure_parameters_dialog(object):
    def setupUi(self, edit_measure_parameters_dialog):
        edit_measure_parameters_dialog.setObjectName("edit_measure_parameters_dialog")
        edit_measure_parameters_dialog.resize(520, 530)
        font = QtGui.QFont()
        font.setPointSize(10)
        edit_measure_parameters_dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        edit_measure_parameters_dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(edit_measure_parameters_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_widget_layout = QtWidgets.QVBoxLayout()
        self.main_widget_layout.setObjectName("main_widget_layout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(edit_measure_parameters_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.flash_after_finish_checkbox = QtWidgets.QCheckBox(edit_measure_parameters_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.flash_after_finish_checkbox.sizePolicy().hasHeightForWidth())
        self.flash_after_finish_checkbox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.flash_after_finish_checkbox.setFont(font)
        self.flash_after_finish_checkbox.setObjectName("flash_after_finish_checkbox")
        self.gridLayout.addWidget(self.flash_after_finish_checkbox, 2, 0, 1, 1)
        self.enable_correction_checkbox = QtWidgets.QCheckBox(edit_measure_parameters_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.enable_correction_checkbox.sizePolicy().hasHeightForWidth())
        self.enable_correction_checkbox.setSizePolicy(sizePolicy)
        self.enable_correction_checkbox.setObjectName("enable_correction_checkbox")
        self.gridLayout.addWidget(self.enable_correction_checkbox, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.aci_radio = QtWidgets.QRadioButton(edit_measure_parameters_dialog)
        self.aci_radio.setChecked(True)
        self.aci_radio.setObjectName("aci_radio")
        self.horizontalLayout.addWidget(self.aci_radio)
        self.dci_radio = QtWidgets.QRadioButton(edit_measure_parameters_dialog)
        self.dci_radio.setObjectName("dci_radio")
        self.horizontalLayout.addWidget(self.dci_radio)
        self.acv_radio = QtWidgets.QRadioButton(edit_measure_parameters_dialog)
        self.acv_radio.setObjectName("acv_radio")
        self.horizontalLayout.addWidget(self.acv_radio)
        self.dcv_radio = QtWidgets.QRadioButton(edit_measure_parameters_dialog)
        self.dcv_radio.setObjectName("dcv_radio")
        self.horizontalLayout.addWidget(self.dcv_radio)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)
        self.main_widget_layout.addLayout(self.gridLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(edit_measure_parameters_dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.add_flash_table_row_button = QtWidgets.QPushButton(edit_measure_parameters_dialog)
        self.add_flash_table_row_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_flash_table_row_button.setIcon(icon1)
        self.add_flash_table_row_button.setObjectName("add_flash_table_row_button")
        self.horizontalLayout_2.addWidget(self.add_flash_table_row_button)
        self.remove_flash_table_row_button = QtWidgets.QPushButton(edit_measure_parameters_dialog)
        self.remove_flash_table_row_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/minus2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_flash_table_row_button.setIcon(icon2)
        self.remove_flash_table_row_button.setObjectName("remove_flash_table_row_button")
        self.horizontalLayout_2.addWidget(self.remove_flash_table_row_button)
        self.main_widget_layout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.flash_table = QtWidgets.QTableWidget(edit_measure_parameters_dialog)
        self.flash_table.setStyleSheet("selection-color: rgb(0, 0, 0);\n"
"selection-background-color: rgb(170, 170, 255);")
        self.flash_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.flash_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.flash_table.setObjectName("flash_table")
        self.flash_table.setColumnCount(5)
        self.flash_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.flash_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.flash_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.flash_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.flash_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.flash_table.setHorizontalHeaderItem(4, item)
        self.flash_table.horizontalHeader().setStretchLastSection(True)
        self.flash_table.verticalHeader().setVisible(False)
        self.horizontalLayout_4.addWidget(self.flash_table)
        self.main_widget_layout.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addLayout(self.main_widget_layout)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setObjectName("buttons_layout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttons_layout.addItem(spacerItem1)
        self.accept_button = QtWidgets.QPushButton(edit_measure_parameters_dialog)
        self.accept_button.setDefault(True)
        self.accept_button.setObjectName("accept_button")
        self.buttons_layout.addWidget(self.accept_button)
        self.cancel_button = QtWidgets.QPushButton(edit_measure_parameters_dialog)
        self.cancel_button.setObjectName("cancel_button")
        self.buttons_layout.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.buttons_layout)

        self.retranslateUi(edit_measure_parameters_dialog)
        QtCore.QMetaObject.connectSlotsByName(edit_measure_parameters_dialog)
        edit_measure_parameters_dialog.setTabOrder(self.aci_radio, self.dci_radio)
        edit_measure_parameters_dialog.setTabOrder(self.dci_radio, self.acv_radio)
        edit_measure_parameters_dialog.setTabOrder(self.acv_radio, self.dcv_radio)
        edit_measure_parameters_dialog.setTabOrder(self.dcv_radio, self.enable_correction_checkbox)
        edit_measure_parameters_dialog.setTabOrder(self.enable_correction_checkbox, self.flash_after_finish_checkbox)
        edit_measure_parameters_dialog.setTabOrder(self.flash_after_finish_checkbox, self.add_flash_table_row_button)
        edit_measure_parameters_dialog.setTabOrder(self.add_flash_table_row_button, self.remove_flash_table_row_button)
        edit_measure_parameters_dialog.setTabOrder(self.remove_flash_table_row_button, self.flash_table)
        edit_measure_parameters_dialog.setTabOrder(self.flash_table, self.accept_button)
        edit_measure_parameters_dialog.setTabOrder(self.accept_button, self.cancel_button)

    def retranslateUi(self, edit_measure_parameters_dialog):
        _translate = QtCore.QCoreApplication.translate
        edit_measure_parameters_dialog.setWindowTitle(_translate("edit_measure_parameters_dialog", "Параметры измерения"))
        self.label.setText(_translate("edit_measure_parameters_dialog", "Сигнал калибратора"))
        self.flash_after_finish_checkbox.setText(_translate("edit_measure_parameters_dialog", "Прошивать после завершения"))
        self.enable_correction_checkbox.setText(_translate("edit_measure_parameters_dialog", "Коррекция включена"))
        self.aci_radio.setText(_translate("edit_measure_parameters_dialog", "I~"))
        self.dci_radio.setText(_translate("edit_measure_parameters_dialog", "I="))
        self.acv_radio.setText(_translate("edit_measure_parameters_dialog", "U~"))
        self.dcv_radio.setText(_translate("edit_measure_parameters_dialog", "U="))
        self.label_2.setText(_translate("edit_measure_parameters_dialog", "Таблица диапазонов прошивки"))
        item = self.flash_table.horizontalHeaderItem(0)
        item.setText(_translate("edit_measure_parameters_dialog", "№"))
        item = self.flash_table.horizontalHeaderItem(1)
        item.setText(_translate("edit_measure_parameters_dialog", "Смещение\n"
"в eeprom"))
        item = self.flash_table.horizontalHeaderItem(2)
        item.setText(_translate("edit_measure_parameters_dialog", "Размер"))
        item = self.flash_table.horizontalHeaderItem(3)
        item.setText(_translate("edit_measure_parameters_dialog", "Начальное\n"
"значение"))
        item = self.flash_table.horizontalHeaderItem(4)
        item.setText(_translate("edit_measure_parameters_dialog", "Конечное\n"
"значение"))
        self.accept_button.setText(_translate("edit_measure_parameters_dialog", "Принять"))
        self.cancel_button.setText(_translate("edit_measure_parameters_dialog", "Отмена"))
from irspy.qt.resources import icons

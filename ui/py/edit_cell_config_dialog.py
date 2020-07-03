# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/edit_cell_config_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(531, 529)
        font = QtGui.QFont()
        font.setPointSize(10)
        Dialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_widget_layout = QtWidgets.QVBoxLayout()
        self.main_widget_layout.setObjectName("main_widget_layout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.aci_radio = QtWidgets.QRadioButton(Dialog)
        self.aci_radio.setChecked(True)
        self.aci_radio.setObjectName("aci_radio")
        self.horizontalLayout.addWidget(self.aci_radio)
        self.dci_radio = QtWidgets.QRadioButton(Dialog)
        self.dci_radio.setObjectName("dci_radio")
        self.horizontalLayout.addWidget(self.dci_radio)
        self.acv_radio = QtWidgets.QRadioButton(Dialog)
        self.acv_radio.setObjectName("acv_radio")
        self.horizontalLayout.addWidget(self.acv_radio)
        self.dcv_radio = QtWidgets.QRadioButton(Dialog)
        self.dcv_radio.setObjectName("dcv_radio")
        self.horizontalLayout.addWidget(self.dcv_radio)
        self.main_widget_layout.addLayout(self.horizontalLayout)
        self.flash_after_finish_checkbox = QtWidgets.QCheckBox(Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.flash_after_finish_checkbox.setFont(font)
        self.flash_after_finish_checkbox.setObjectName("flash_after_finish_checkbox")
        self.main_widget_layout.addWidget(self.flash_after_finish_checkbox)
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.flash_table = QtWidgets.QTableWidget(self.tab)
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
        self.horizontalLayout_2.addWidget(self.flash_table)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.add_flash_table_row_button = QtWidgets.QPushButton(self.tab)
        self.add_flash_table_row_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_flash_table_row_button.setIcon(icon)
        self.add_flash_table_row_button.setObjectName("add_flash_table_row_button")
        self.verticalLayout_2.addWidget(self.add_flash_table_row_button)
        self.remove_flash_table_row_button = QtWidgets.QPushButton(self.tab)
        self.remove_flash_table_row_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/minus2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_flash_table_row_button.setIcon(icon1)
        self.remove_flash_table_row_button.setObjectName("remove_flash_table_row_button")
        self.verticalLayout_2.addWidget(self.remove_flash_table_row_button)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.extra_variables_table = QtWidgets.QTableWidget(self.tab_2)
        self.extra_variables_table.setStyleSheet("selection-color: rgb(0, 0, 0);\n"
"selection-background-color: rgb(170, 170, 255);")
        self.extra_variables_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.extra_variables_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.extra_variables_table.setObjectName("extra_variables_table")
        self.extra_variables_table.setColumnCount(5)
        self.extra_variables_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.extra_variables_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.extra_variables_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.extra_variables_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.extra_variables_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.extra_variables_table.setHorizontalHeaderItem(4, item)
        self.extra_variables_table.horizontalHeader().setStretchLastSection(True)
        self.horizontalLayout_3.addWidget(self.extra_variables_table)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.add_extra_param_button = QtWidgets.QPushButton(self.tab_2)
        self.add_extra_param_button.setText("")
        self.add_extra_param_button.setIcon(icon)
        self.add_extra_param_button.setObjectName("add_extra_param_button")
        self.verticalLayout_3.addWidget(self.add_extra_param_button)
        self.remove_extra_param_button = QtWidgets.QPushButton(self.tab_2)
        self.remove_extra_param_button.setText("")
        self.remove_extra_param_button.setIcon(icon1)
        self.remove_extra_param_button.setObjectName("remove_extra_param_button")
        self.verticalLayout_3.addWidget(self.remove_extra_param_button)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.tabWidget.addTab(self.tab_2, "")
        self.main_widget_layout.addWidget(self.tabWidget)
        self.verticalLayout.addLayout(self.main_widget_layout)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setObjectName("buttons_layout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttons_layout.addItem(spacerItem2)
        self.accept_button = QtWidgets.QPushButton(Dialog)
        self.accept_button.setObjectName("accept_button")
        self.buttons_layout.addWidget(self.accept_button)
        self.cancel_button = QtWidgets.QPushButton(Dialog)
        self.cancel_button.setObjectName("cancel_button")
        self.buttons_layout.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.buttons_layout)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Параметры измерения"))
        self.label.setText(_translate("Dialog", "Сигнал калибратора"))
        self.aci_radio.setText(_translate("Dialog", "I~"))
        self.dci_radio.setText(_translate("Dialog", "I="))
        self.acv_radio.setText(_translate("Dialog", "U~"))
        self.dcv_radio.setText(_translate("Dialog", "U="))
        self.flash_after_finish_checkbox.setText(_translate("Dialog", "Прошивать после завершения"))
        item = self.flash_table.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Номер"))
        item = self.flash_table.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Н. индекса"))
        item = self.flash_table.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "Размер"))
        item = self.flash_table.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "Н. значения"))
        item = self.flash_table.horizontalHeaderItem(4)
        item.setText(_translate("Dialog", "К. значения"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "Таблица прошивки"))
        item = self.extra_variables_table.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Имя"))
        item = self.extra_variables_table.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Индекс"))
        item = self.extra_variables_table.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "Тип"))
        item = self.extra_variables_table.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "Рабоч. знач."))
        item = self.extra_variables_table.horizontalHeaderItem(4)
        item.setText(_translate("Dialog", "Знач. по-умолч."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Dialog", "Дополнительные переменные"))
        self.accept_button.setText(_translate("Dialog", "Принять"))
        self.cancel_button.setText(_translate("Dialog", "Отмена"))
import icons_rc

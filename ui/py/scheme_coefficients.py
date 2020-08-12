# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/shared_measure_parameters.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_edit_agilent_config_dialog(object):
    def setupUi(self, edit_agilent_config_dialog):
        edit_agilent_config_dialog.setObjectName("edit_agilent_config_dialog")
        edit_agilent_config_dialog.resize(305, 214)
        font = QtGui.QFont()
        font.setPointSize(10)
        edit_agilent_config_dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        edit_agilent_config_dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(edit_agilent_config_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(edit_agilent_config_dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(edit_agilent_config_dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(edit_agilent_config_dialog)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(edit_agilent_config_dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(edit_agilent_config_dialog)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(edit_agilent_config_dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.connect_type_combobox = QtWidgets.QComboBox(edit_agilent_config_dialog)
        self.connect_type_combobox.setObjectName("connect_type_combobox")
        self.connect_type_combobox.addItem("")
        self.connect_type_combobox.addItem("")
        self.connect_type_combobox.addItem("")
        self.connect_type_combobox.addItem("")
        self.gridLayout.addWidget(self.connect_type_combobox, 0, 1, 1, 1)
        self.gpib_index_spinbox = QtWidgets.QSpinBox(edit_agilent_config_dialog)
        self.gpib_index_spinbox.setMaximum(9999)
        self.gpib_index_spinbox.setObjectName("gpib_index_spinbox")
        self.gridLayout.addWidget(self.gpib_index_spinbox, 1, 1, 1, 1)
        self.gpib_address_spinbox = QtWidgets.QSpinBox(edit_agilent_config_dialog)
        self.gpib_address_spinbox.setMaximum(9999)
        self.gpib_address_spinbox.setObjectName("gpib_address_spinbox")
        self.gridLayout.addWidget(self.gpib_address_spinbox, 2, 1, 1, 1)
        self.com_name_edit = QtWidgets.QLineEdit(edit_agilent_config_dialog)
        self.com_name_edit.setObjectName("com_name_edit")
        self.gridLayout.addWidget(self.com_name_edit, 3, 1, 1, 1)
        self.ip_address_edit = QtWidgets.QLineEdit(edit_agilent_config_dialog)
        self.ip_address_edit.setObjectName("ip_address_edit")
        self.gridLayout.addWidget(self.ip_address_edit, 4, 1, 1, 1)
        self.port_spinbox = QtWidgets.QSpinBox(edit_agilent_config_dialog)
        self.port_spinbox.setMaximum(9999)
        self.port_spinbox.setObjectName("port_spinbox")
        self.gridLayout.addWidget(self.port_spinbox, 5, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setObjectName("buttons_layout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttons_layout.addItem(spacerItem)
        self.accept_button = QtWidgets.QPushButton(edit_agilent_config_dialog)
        self.accept_button.setDefault(True)
        self.accept_button.setObjectName("accept_button")
        self.buttons_layout.addWidget(self.accept_button)
        self.cancel_button = QtWidgets.QPushButton(edit_agilent_config_dialog)
        self.cancel_button.setObjectName("cancel_button")
        self.buttons_layout.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.buttons_layout)

        self.retranslateUi(edit_agilent_config_dialog)
        QtCore.QMetaObject.connectSlotsByName(edit_agilent_config_dialog)
        edit_agilent_config_dialog.setTabOrder(self.accept_button, self.cancel_button)

    def retranslateUi(self, edit_agilent_config_dialog):
        _translate = QtCore.QCoreApplication.translate
        edit_agilent_config_dialog.setWindowTitle(_translate("edit_agilent_config_dialog", "Параметры Agilent3458A"))
        self.label.setText(_translate("edit_agilent_config_dialog", "Способ подключения"))
        self.label_4.setText(_translate("edit_agilent_config_dialog", "COM name"))
        self.label_6.setText(_translate("edit_agilent_config_dialog", "Порт"))
        self.label_3.setText(_translate("edit_agilent_config_dialog", "Адрес GPIB"))
        self.label_5.setText(_translate("edit_agilent_config_dialog", "IP адрес"))
        self.label_2.setText(_translate("edit_agilent_config_dialog", "Индекс GPIB"))
        self.connect_type_combobox.setItemText(0, _translate("edit_agilent_config_dialog", "Agilent USB-GPIB"))
        self.connect_type_combobox.setItemText(1, _translate("edit_agilent_config_dialog", "NI USB-GPIB"))
        self.connect_type_combobox.setItemText(2, _translate("edit_agilent_config_dialog", "Prologix COM-GPIB"))
        self.connect_type_combobox.setItemText(3, _translate("edit_agilent_config_dialog", "Prologix Ethernet-GPIB"))
        self.accept_button.setText(_translate("edit_agilent_config_dialog", "Принять"))
        self.cancel_button.setText(_translate("edit_agilent_config_dialog", "Отмена"))
import icons_rc

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/edit_cell_config_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_edit_cell_config_dialog(object):
    def setupUi(self, edit_cell_config_dialog):
        edit_cell_config_dialog.setObjectName("edit_cell_config_dialog")
        edit_cell_config_dialog.resize(407, 698)
        font = QtGui.QFont()
        font.setPointSize(10)
        edit_cell_config_dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        edit_cell_config_dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(edit_cell_config_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_widget_layout = QtWidgets.QVBoxLayout()
        self.main_widget_layout.setObjectName("main_widget_layout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(edit_cell_config_dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(edit_cell_config_dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.retry_count_spinbox = QtWidgets.QSpinBox(edit_cell_config_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.retry_count_spinbox.sizePolicy().hasHeightForWidth())
        self.retry_count_spinbox.setSizePolicy(sizePolicy)
        self.retry_count_spinbox.setMinimumSize(QtCore.QSize(100, 0))
        self.retry_count_spinbox.setMinimum(1)
        self.retry_count_spinbox.setProperty("value", 3)
        self.retry_count_spinbox.setObjectName("retry_count_spinbox")
        self.gridLayout.addWidget(self.retry_count_spinbox, 3, 1, 1, 1)
        self.measure_delay_spinbox = QtWidgets.QSpinBox(edit_cell_config_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.measure_delay_spinbox.sizePolicy().hasHeightForWidth())
        self.measure_delay_spinbox.setSizePolicy(sizePolicy)
        self.measure_delay_spinbox.setMinimumSize(QtCore.QSize(100, 0))
        self.measure_delay_spinbox.setMinimum(1)
        self.measure_delay_spinbox.setMaximum(9999)
        self.measure_delay_spinbox.setProperty("value", 100)
        self.measure_delay_spinbox.setObjectName("measure_delay_spinbox")
        self.gridLayout.addWidget(self.measure_delay_spinbox, 1, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.aci_radio = QtWidgets.QRadioButton(edit_cell_config_dialog)
        self.aci_radio.setEnabled(False)
        self.aci_radio.setChecked(True)
        self.aci_radio.setObjectName("aci_radio")
        self.horizontalLayout.addWidget(self.aci_radio)
        self.dci_radio = QtWidgets.QRadioButton(edit_cell_config_dialog)
        self.dci_radio.setEnabled(False)
        self.dci_radio.setObjectName("dci_radio")
        self.horizontalLayout.addWidget(self.dci_radio)
        self.acv_radio = QtWidgets.QRadioButton(edit_cell_config_dialog)
        self.acv_radio.setEnabled(False)
        self.acv_radio.setObjectName("acv_radio")
        self.horizontalLayout.addWidget(self.acv_radio)
        self.dcv_radio = QtWidgets.QRadioButton(edit_cell_config_dialog)
        self.dcv_radio.setEnabled(False)
        self.dcv_radio.setObjectName("dcv_radio")
        self.horizontalLayout.addWidget(self.dcv_radio)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 3)
        self.label_5 = QtWidgets.QLabel(edit_cell_config_dialog)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)
        self.measure_time_spinbox = QtWidgets.QSpinBox(edit_cell_config_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.measure_time_spinbox.sizePolicy().hasHeightForWidth())
        self.measure_time_spinbox.setSizePolicy(sizePolicy)
        self.measure_time_spinbox.setMinimumSize(QtCore.QSize(100, 0))
        self.measure_time_spinbox.setMinimum(0)
        self.measure_time_spinbox.setMaximum(99999)
        self.measure_time_spinbox.setProperty("value", 300)
        self.measure_time_spinbox.setObjectName("measure_time_spinbox")
        self.gridLayout.addWidget(self.measure_time_spinbox, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(edit_cell_config_dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(edit_cell_config_dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.coefficient_edit = QEditDoubleClick(edit_cell_config_dialog)
        self.coefficient_edit.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.coefficient_edit.setFont(font)
        self.coefficient_edit.setObjectName("coefficient_edit")
        self.gridLayout.addWidget(self.coefficient_edit, 4, 1, 1, 1)
        self.main_widget_layout.addLayout(self.gridLayout)
        self.consider_output_value_checkbox = QtWidgets.QGroupBox(edit_cell_config_dialog)
        self.consider_output_value_checkbox.setCheckable(True)
        self.consider_output_value_checkbox.setChecked(False)
        self.consider_output_value_checkbox.setObjectName("consider_output_value_checkbox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.consider_output_value_checkbox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.enable_output_filtering_checkbox = QtWidgets.QCheckBox(self.consider_output_value_checkbox)
        self.enable_output_filtering_checkbox.setObjectName("enable_output_filtering_checkbox")
        self.verticalLayout_2.addWidget(self.enable_output_filtering_checkbox)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_6 = QtWidgets.QLabel(self.consider_output_value_checkbox)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 0, 1, 1)
        self.sampling_time_spinbox = QtWidgets.QDoubleSpinBox(self.consider_output_value_checkbox)
        self.sampling_time_spinbox.setDecimals(4)
        self.sampling_time_spinbox.setSingleStep(0.1)
        self.sampling_time_spinbox.setProperty("value", 0.1)
        self.sampling_time_spinbox.setObjectName("sampling_time_spinbox")
        self.gridLayout_2.addWidget(self.sampling_time_spinbox, 0, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.consider_output_value_checkbox)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 1, 0, 1, 1)
        self.filter_points_count_spinbox = QtWidgets.QSpinBox(self.consider_output_value_checkbox)
        self.filter_points_count_spinbox.setMaximum(9999)
        self.filter_points_count_spinbox.setProperty("value", 100)
        self.filter_points_count_spinbox.setObjectName("filter_points_count_spinbox")
        self.gridLayout_2.addWidget(self.filter_points_count_spinbox, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.main_widget_layout.addWidget(self.consider_output_value_checkbox)
        self.tabWidget = QtWidgets.QTabWidget(edit_cell_config_dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.coil_no_radio = QtWidgets.QRadioButton(self.groupBox_3)
        self.coil_no_radio.setChecked(True)
        self.coil_no_radio.setObjectName("coil_no_radio")
        self.buttonGroup_2 = QtWidgets.QButtonGroup(edit_cell_config_dialog)
        self.buttonGroup_2.setObjectName("buttonGroup_2")
        self.buttonGroup_2.addButton(self.coil_no_radio)
        self.verticalLayout_5.addWidget(self.coil_no_radio)
        self.coil_001_radio = QtWidgets.QRadioButton(self.groupBox_3)
        self.coil_001_radio.setObjectName("coil_001_radio")
        self.buttonGroup_2.addButton(self.coil_001_radio)
        self.verticalLayout_5.addWidget(self.coil_001_radio)
        self.coil_1_radio = QtWidgets.QRadioButton(self.groupBox_3)
        self.coil_1_radio.setObjectName("coil_1_radio")
        self.buttonGroup_2.addButton(self.coil_1_radio)
        self.verticalLayout_5.addWidget(self.coil_1_radio)
        self.coil_10_radio = QtWidgets.QRadioButton(self.groupBox_3)
        self.coil_10_radio.setObjectName("coil_10_radio")
        self.buttonGroup_2.addButton(self.coil_10_radio)
        self.verticalLayout_5.addWidget(self.coil_10_radio)
        self.horizontalLayout_2.addWidget(self.groupBox_3)
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.divider_200_radio = QtWidgets.QRadioButton(self.groupBox_4)
        self.divider_200_radio.setObjectName("divider_200_radio")
        self.buttonGroup_3 = QtWidgets.QButtonGroup(edit_cell_config_dialog)
        self.buttonGroup_3.setObjectName("buttonGroup_3")
        self.buttonGroup_3.addButton(self.divider_200_radio)
        self.gridLayout_3.addWidget(self.divider_200_radio, 4, 0, 1, 1)
        self.divider_500_radio = QtWidgets.QRadioButton(self.groupBox_4)
        self.divider_500_radio.setObjectName("divider_500_radio")
        self.buttonGroup_3.addButton(self.divider_500_radio)
        self.gridLayout_3.addWidget(self.divider_500_radio, 2, 0, 1, 1)
        self.divider_650_radio = QtWidgets.QRadioButton(self.groupBox_4)
        self.divider_650_radio.setObjectName("divider_650_radio")
        self.buttonGroup_3.addButton(self.divider_650_radio)
        self.gridLayout_3.addWidget(self.divider_650_radio, 1, 0, 1, 1)
        self.divider_40_radio = QtWidgets.QRadioButton(self.groupBox_4)
        self.divider_40_radio.setObjectName("divider_40_radio")
        self.buttonGroup_3.addButton(self.divider_40_radio)
        self.gridLayout_3.addWidget(self.divider_40_radio, 6, 0, 1, 1)
        self.divider_350_radio = QtWidgets.QRadioButton(self.groupBox_4)
        self.divider_350_radio.setObjectName("divider_350_radio")
        self.buttonGroup_3.addButton(self.divider_350_radio)
        self.gridLayout_3.addWidget(self.divider_350_radio, 3, 0, 1, 1)
        self.divider_no_radio = QtWidgets.QRadioButton(self.groupBox_4)
        self.divider_no_radio.setChecked(True)
        self.divider_no_radio.setObjectName("divider_no_radio")
        self.buttonGroup_3.addButton(self.divider_no_radio)
        self.gridLayout_3.addWidget(self.divider_no_radio, 0, 0, 1, 1)
        self.divider_55_radio = QtWidgets.QRadioButton(self.groupBox_4)
        self.divider_55_radio.setObjectName("divider_55_radio")
        self.buttonGroup_3.addButton(self.divider_55_radio)
        self.gridLayout_3.addWidget(self.divider_55_radio, 5, 0, 1, 1)
        self.amplifier_30_radio = QtWidgets.QRadioButton(self.groupBox_4)
        self.amplifier_30_radio.setObjectName("amplifier_30_radio")
        self.buttonGroup_3.addButton(self.amplifier_30_radio)
        self.gridLayout_3.addWidget(self.amplifier_30_radio, 1, 1, 1, 1)
        self.amplifier_10_radio = QtWidgets.QRadioButton(self.groupBox_4)
        self.amplifier_10_radio.setObjectName("amplifier_10_radio")
        self.buttonGroup_3.addButton(self.amplifier_10_radio)
        self.gridLayout_3.addWidget(self.amplifier_10_radio, 2, 1, 1, 1)
        self.horizontalLayout_2.addWidget(self.groupBox_4)
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.ammeter_radio = QtWidgets.QRadioButton(self.groupBox_2)
        self.ammeter_radio.setEnabled(False)
        self.ammeter_radio.setChecked(True)
        self.ammeter_radio.setObjectName("ammeter_radio")
        self.buttonGroup = QtWidgets.QButtonGroup(edit_cell_config_dialog)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.ammeter_radio)
        self.verticalLayout_4.addWidget(self.ammeter_radio)
        self.voltmeter_radio = QtWidgets.QRadioButton(self.groupBox_2)
        self.voltmeter_radio.setEnabled(False)
        self.voltmeter_radio.setObjectName("voltmeter_radio")
        self.buttonGroup.addButton(self.voltmeter_radio)
        self.verticalLayout_4.addWidget(self.voltmeter_radio)
        self.horizontalLayout_2.addWidget(self.groupBox_2)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.add_extra_param_button = QtWidgets.QPushButton(self.tab_2)
        self.add_extra_param_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_extra_param_button.setIcon(icon1)
        self.add_extra_param_button.setObjectName("add_extra_param_button")
        self.horizontalLayout_3.addWidget(self.add_extra_param_button)
        self.remove_extra_param_button = QtWidgets.QPushButton(self.tab_2)
        self.remove_extra_param_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/minus2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_extra_param_button.setIcon(icon2)
        self.remove_extra_param_button.setObjectName("remove_extra_param_button")
        self.horizontalLayout_3.addWidget(self.remove_extra_param_button)
        self.verticalLayout_6.addLayout(self.horizontalLayout_3)
        self.extra_variables_table = QtWidgets.QTableWidget(self.tab_2)
        self.extra_variables_table.setStyleSheet("selection-color: rgb(0, 0, 0);\n"
"selection-background-color: rgb(170, 170, 255);")
        self.extra_variables_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.extra_variables_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.extra_variables_table.setObjectName("extra_variables_table")
        self.extra_variables_table.setColumnCount(6)
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
        item = QtWidgets.QTableWidgetItem()
        self.extra_variables_table.setHorizontalHeaderItem(5, item)
        self.extra_variables_table.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_6.addWidget(self.extra_variables_table)
        self.tabWidget.addTab(self.tab_2, "")
        self.main_widget_layout.addWidget(self.tabWidget)
        self.verticalLayout.addLayout(self.main_widget_layout)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setObjectName("buttons_layout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttons_layout.addItem(spacerItem1)
        self.accept_button = QtWidgets.QPushButton(edit_cell_config_dialog)
        self.accept_button.setDefault(True)
        self.accept_button.setObjectName("accept_button")
        self.buttons_layout.addWidget(self.accept_button)
        self.cancel_button = QtWidgets.QPushButton(edit_cell_config_dialog)
        self.cancel_button.setObjectName("cancel_button")
        self.buttons_layout.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.buttons_layout)

        self.retranslateUi(edit_cell_config_dialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(edit_cell_config_dialog)
        edit_cell_config_dialog.setTabOrder(self.aci_radio, self.dci_radio)
        edit_cell_config_dialog.setTabOrder(self.dci_radio, self.acv_radio)
        edit_cell_config_dialog.setTabOrder(self.acv_radio, self.dcv_radio)
        edit_cell_config_dialog.setTabOrder(self.dcv_radio, self.measure_delay_spinbox)
        edit_cell_config_dialog.setTabOrder(self.measure_delay_spinbox, self.retry_count_spinbox)
        edit_cell_config_dialog.setTabOrder(self.retry_count_spinbox, self.consider_output_value_checkbox)
        edit_cell_config_dialog.setTabOrder(self.consider_output_value_checkbox, self.enable_output_filtering_checkbox)
        edit_cell_config_dialog.setTabOrder(self.enable_output_filtering_checkbox, self.tabWidget)
        edit_cell_config_dialog.setTabOrder(self.tabWidget, self.coil_no_radio)
        edit_cell_config_dialog.setTabOrder(self.coil_no_radio, self.coil_001_radio)
        edit_cell_config_dialog.setTabOrder(self.coil_001_radio, self.coil_1_radio)
        edit_cell_config_dialog.setTabOrder(self.coil_1_radio, self.coil_10_radio)
        edit_cell_config_dialog.setTabOrder(self.coil_10_radio, self.divider_no_radio)
        edit_cell_config_dialog.setTabOrder(self.divider_no_radio, self.divider_650_radio)
        edit_cell_config_dialog.setTabOrder(self.divider_650_radio, self.divider_500_radio)
        edit_cell_config_dialog.setTabOrder(self.divider_500_radio, self.divider_350_radio)
        edit_cell_config_dialog.setTabOrder(self.divider_350_radio, self.divider_200_radio)
        edit_cell_config_dialog.setTabOrder(self.divider_200_radio, self.divider_55_radio)
        edit_cell_config_dialog.setTabOrder(self.divider_55_radio, self.divider_40_radio)
        edit_cell_config_dialog.setTabOrder(self.divider_40_radio, self.amplifier_30_radio)
        edit_cell_config_dialog.setTabOrder(self.amplifier_30_radio, self.amplifier_10_radio)
        edit_cell_config_dialog.setTabOrder(self.amplifier_10_radio, self.ammeter_radio)
        edit_cell_config_dialog.setTabOrder(self.ammeter_radio, self.voltmeter_radio)
        edit_cell_config_dialog.setTabOrder(self.voltmeter_radio, self.extra_variables_table)
        edit_cell_config_dialog.setTabOrder(self.extra_variables_table, self.remove_extra_param_button)
        edit_cell_config_dialog.setTabOrder(self.remove_extra_param_button, self.accept_button)
        edit_cell_config_dialog.setTabOrder(self.accept_button, self.cancel_button)

    def retranslateUi(self, edit_cell_config_dialog):
        _translate = QtCore.QCoreApplication.translate
        edit_cell_config_dialog.setWindowTitle(_translate("edit_cell_config_dialog", "Конфигурация ячейки"))
        self.label.setText(_translate("edit_cell_config_dialog", "Сигнал калибратора"))
        self.label_3.setText(_translate("edit_cell_config_dialog", "Количество попыток"))
        self.aci_radio.setText(_translate("edit_cell_config_dialog", "I~"))
        self.dci_radio.setText(_translate("edit_cell_config_dialog", "I="))
        self.acv_radio.setText(_translate("edit_cell_config_dialog", "U~"))
        self.dcv_radio.setText(_translate("edit_cell_config_dialog", "U="))
        self.label_5.setText(_translate("edit_cell_config_dialog", "Время измерения, с"))
        self.label_4.setText(_translate("edit_cell_config_dialog", "Задержка измерения, с"))
        self.label_2.setText(_translate("edit_cell_config_dialog", "Коэффициент преобразования"))
        self.coefficient_edit.setText(_translate("edit_cell_config_dialog", "1"))
        self.consider_output_value_checkbox.setTitle(_translate("edit_cell_config_dialog", "Учитывать выходное значение при измерении"))
        self.enable_output_filtering_checkbox.setText(_translate("edit_cell_config_dialog", "Включить фильтрацию выходного значения"))
        self.label_6.setText(_translate("edit_cell_config_dialog", "Время дискретизации"))
        self.label_7.setText(_translate("edit_cell_config_dialog", "Количество точек"))
        self.groupBox_3.setTitle(_translate("edit_cell_config_dialog", "Катушка"))
        self.coil_no_radio.setText(_translate("edit_cell_config_dialog", "Нет"))
        self.coil_001_radio.setText(_translate("edit_cell_config_dialog", "0,01 Ом"))
        self.coil_1_radio.setText(_translate("edit_cell_config_dialog", "1 Ом"))
        self.coil_10_radio.setText(_translate("edit_cell_config_dialog", "10 Ом"))
        self.groupBox_4.setTitle(_translate("edit_cell_config_dialog", "Делитель/Усилитель"))
        self.divider_200_radio.setText(_translate("edit_cell_config_dialog", "/200 В"))
        self.divider_500_radio.setText(_translate("edit_cell_config_dialog", "/500 В"))
        self.divider_650_radio.setText(_translate("edit_cell_config_dialog", "/650 В"))
        self.divider_40_radio.setText(_translate("edit_cell_config_dialog", "/40 В"))
        self.divider_350_radio.setText(_translate("edit_cell_config_dialog", "/350 В"))
        self.divider_no_radio.setText(_translate("edit_cell_config_dialog", "Нет"))
        self.divider_55_radio.setText(_translate("edit_cell_config_dialog", "/55 В"))
        self.amplifier_30_radio.setText(_translate("edit_cell_config_dialog", "*30 мВ"))
        self.amplifier_10_radio.setText(_translate("edit_cell_config_dialog", "* 10 мВ"))
        self.groupBox_2.setTitle(_translate("edit_cell_config_dialog", "Измеритель"))
        self.ammeter_radio.setText(_translate("edit_cell_config_dialog", "Амперметр"))
        self.voltmeter_radio.setText(_translate("edit_cell_config_dialog", "Вольтметр"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("edit_cell_config_dialog", "Схема подключения"))
        item = self.extra_variables_table.horizontalHeaderItem(0)
        item.setText(_translate("edit_cell_config_dialog", "Имя"))
        item = self.extra_variables_table.horizontalHeaderItem(1)
        item.setText(_translate("edit_cell_config_dialog", "Индекс"))
        item = self.extra_variables_table.horizontalHeaderItem(2)
        item.setText(_translate("edit_cell_config_dialog", "Индекс\n"
"бита"))
        item = self.extra_variables_table.horizontalHeaderItem(3)
        item.setText(_translate("edit_cell_config_dialog", "Тип"))
        item = self.extra_variables_table.horizontalHeaderItem(4)
        item.setText(_translate("edit_cell_config_dialog", "Рабочее\n"
"значение"))
        item = self.extra_variables_table.horizontalHeaderItem(5)
        item.setText(_translate("edit_cell_config_dialog", "Значение\n"
"по-умолчанию"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("edit_cell_config_dialog", "Дополнительные переменные"))
        self.accept_button.setText(_translate("edit_cell_config_dialog", "Принять"))
        self.cancel_button.setText(_translate("edit_cell_config_dialog", "Отмена"))
from irspy.qt.custom_widgets.CustomLineEdit import QEditDoubleClick
import icons_rc

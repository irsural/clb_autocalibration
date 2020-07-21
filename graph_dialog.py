from typing import List, Dict, Tuple, Iterable
import logging

from PyQt5 import QtGui, QtWidgets
import pyqtgraph

from ui.py.graph_dialog import Ui_graph_dialog as GraphForm
from irspy.settings_ini_parser import Settings
import irspy.utils as utils


class GraphDialog(QtWidgets.QDialog):
    GRAPH_COLORS = (
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (0, 204, 204),
        (204, 0, 102),
        (204, 204, 0),
        (255, 0, 255),
        (102, 153, 153),
        (255, 153, 0),
        (102, 204, 255),
        (0, 255, 153),
        (204, 102, 255),
    )

    def __init__(self, a_graph_data: Dict[str, Tuple[Iterable[float], Iterable[float]]], a_settings: Settings,
                 a_parent=None):
        super().__init__(a_parent)

        self.ui = GraphForm()
        self.ui.setupUi(self)

        self.open_icon = QtGui.QIcon(QtGui.QPixmap(":/icons/icons/right.png"))
        self.close_icon = QtGui.QIcon(QtGui.QPixmap(":/icons/icons/left.png"))

        self.settings = a_settings
        self.restoreGeometry(self.settings.get_last_geometry(self.objectName()))
        self.ui.graph_dialog_splitter.restoreState(self.settings.get_last_geometry(
            self.ui.graph_dialog_splitter.objectName()))
        self.ui.parameters_table.horizontalHeader().restoreState(self.settings.get_last_header_state(
            self.ui.parameters_table.objectName()))

        self.ui.parameters_widget.setHidden(self.settings.graph_parameters_hidden)
        if self.settings.graph_parameters_hidden:
            self.ui.graph_parameters_button.setIcon(self.open_icon)
        else:
            self.ui.graph_parameters_button.setIcon(self.close_icon)
        self.show()

        self.graph_widget = pyqtgraph.PlotWidget()
        self.graph_widget.setBackground('w')
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.addLegend()

        self.ui.chart_layout.addWidget(self.graph_widget)

        self.graph_items: Dict[str, pyqtgraph.PlotCurveItem] = {}
        self.graphs_data = {name: (list(data_x), list(data_y)) for name, (data_x, data_y) in a_graph_data.items()}

        for graph_name in a_graph_data.keys():
            self.ui.graphs_combobox.addItem(graph_name)
            self.add_graph(graph_name)

        self.ui.graph_parameters_button.clicked.connect(self.show_graph_parameters)

    def show_graph_parameters(self, _):
        parameters_hidden = self.ui.parameters_widget.isHidden()
        now_parameters_hidden = not parameters_hidden

        self.ui.parameters_widget.setHidden(now_parameters_hidden)
        self.settings.graph_parameters_hidden = int(now_parameters_hidden)

        if parameters_hidden:
            sizes = self.ui.graph_dialog_splitter.sizes()
            size_left = self.settings.graph_parameters_splitter_size
            self.ui.graph_dialog_splitter.setSizes([size_left, sizes[1] - size_left])

            self.ui.graph_parameters_button.setIcon(self.close_icon)
        else:
            sizes = self.ui.graph_dialog_splitter.sizes()
            self.settings.graph_parameters_splitter_size = sizes[0]
            self.ui.graph_dialog_splitter.setSizes([0, sizes[0] + sizes[1]])

            self.ui.graph_parameters_button.setIcon(self.open_icon)

    def add_graph(self, a_graph_name):
        graph_number = len(self.graph_widget.listDataItems())
        graph_color = GraphDialog.GRAPH_COLORS[graph_number % len(GraphDialog.GRAPH_COLORS)]

        pg_item = pyqtgraph.PlotCurveItem(pen=pyqtgraph.mkPen(color=graph_color, width=2), name=a_graph_name)
        pg_item.setData(x=self.graphs_data[a_graph_name][0], y=self.graphs_data[a_graph_name][1], name=a_graph_name)
        self.graph_widget.addItem(pg_item)

    def __del__(self):
        print("graphs deleted")

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_geometry(self.ui.graph_dialog_splitter.objectName(),
                                    self.ui.graph_dialog_splitter.saveState())
        self.settings.save_geometry(self.ui.parameters_table.objectName(),
                                    self.ui.parameters_table.horizontalHeader().saveState())
        self.settings.save_geometry(self.objectName(), self.saveGeometry())
        a_event.accept()

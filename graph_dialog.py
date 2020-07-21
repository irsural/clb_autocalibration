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

        self.settings = a_settings
        self.restoreGeometry(self.settings.get_last_geometry(self.objectName()))
        self.ui.graph_dialog_splitter.restoreState(self.settings.get_last_geometry(
            self.ui.graph_dialog_splitter.objectName()))
        self.ui.parameters_table.horizontalHeader().restoreState(self.settings.get_last_header_state(
            self.ui.parameters_table.objectName()))

        self.ui.parameters_widget.setHidden(True)
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
        self.ui.parameters_widget.setHidden(not parameters_hidden)

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

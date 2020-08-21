from irspy.qt.qt_settings_ini_parser import QtSettings


def get_clb_autocalibration_settings():
    return QtSettings("./settings.ini", [
        QtSettings.VariableInfo(a_name="fixed_step_list", a_section="PARAMETERS", a_type=QtSettings.ValueType.LIST_FLOAT,
                                a_default=[0.0001, 0.01, 0.1, 1, 10, 20, 100]),
        QtSettings.VariableInfo(a_name="checkbox_states", a_section="PARAMETERS", a_type=QtSettings.ValueType.LIST_INT),
        QtSettings.VariableInfo(a_name="fixed_step_idx", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT),
        QtSettings.VariableInfo(a_name="rough_step", a_section="PARAMETERS", a_type=QtSettings.ValueType.FLOAT, a_default=0.5),
        QtSettings.VariableInfo(a_name="common_step", a_section="PARAMETERS", a_type=QtSettings.ValueType.FLOAT, a_default=0.05),
        QtSettings.VariableInfo(a_name="exact_step", a_section="PARAMETERS", a_type=QtSettings.ValueType.FLOAT, a_default=0.002),
        QtSettings.VariableInfo(a_name="tstlan_update_time", a_section="PARAMETERS", a_type=QtSettings.ValueType.FLOAT, a_default=0.2),
        QtSettings.VariableInfo(a_name="tstlan_show_marks", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=0),
        QtSettings.VariableInfo(a_name="tstlan_marks", a_section="PARAMETERS", a_type=QtSettings.ValueType.LIST_INT),
        QtSettings.VariableInfo(a_name="tstlan_graphs", a_section="PARAMETERS", a_type=QtSettings.ValueType.LIST_INT),
        QtSettings.VariableInfo(a_name="last_configuration_path", a_section="PARAMETERS", a_type=QtSettings.ValueType.STRING),
        QtSettings.VariableInfo(a_name="meter_type", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=0),
        QtSettings.VariableInfo(a_name="agilent_connect_type", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=0),
        QtSettings.VariableInfo(a_name="agilent_gpib_index", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=0),
        QtSettings.VariableInfo(a_name="agilent_gpib_address", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=22),
        QtSettings.VariableInfo(a_name="agilent_com_name", a_section="PARAMETERS", a_type=QtSettings.ValueType.STRING, a_default="com4"),
        QtSettings.VariableInfo(a_name="agilent_ip_address", a_section="PARAMETERS", a_type=QtSettings.ValueType.STRING, a_default="0.0.0.0"),
        QtSettings.VariableInfo(a_name="agilent_port", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=0),
        QtSettings.VariableInfo(a_name="switch_to_active_cell", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=0),
        QtSettings.VariableInfo(a_name="graph_parameters_splitter_size", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=500),
        QtSettings.VariableInfo(a_name="show_scheme_in_cell", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=1),
        QtSettings.VariableInfo(a_name="scheme_type", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=0),
        QtSettings.VariableInfo(a_name="display_data_precision", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=6),
        QtSettings.VariableInfo(a_name="edit_data_precision", a_section="PARAMETERS", a_type=QtSettings.ValueType.INT, a_default=20),
    ])

from irspy.settings_ini_parser import Settings


def get_clb_autocalibration_settings():
    return Settings("./settings.ini", [
        Settings.VariableInfo(a_name="fixed_step_list", a_section="PARAMETERS", a_type=Settings.ValueType.LIST_FLOAT,
                              a_default=[0.0001, 0.01, 0.1, 1, 10, 20, 100]),
        Settings.VariableInfo(a_name="checkbox_states", a_section="PARAMETERS", a_type=Settings.ValueType.LIST_INT),
        Settings.VariableInfo(a_name="fixed_step_idx", a_section="PARAMETERS", a_type=Settings.ValueType.INT),
        Settings.VariableInfo(a_name="rough_step", a_section="PARAMETERS", a_type=Settings.ValueType.FLOAT, a_default=0.5),
        Settings.VariableInfo(a_name="common_step", a_section="PARAMETERS", a_type=Settings.ValueType.FLOAT, a_default=0.05),
        Settings.VariableInfo(a_name="exact_step", a_section="PARAMETERS", a_type=Settings.ValueType.FLOAT, a_default=0.002),
        Settings.VariableInfo(a_name="tstlan_update_time", a_section="PARAMETERS", a_type=Settings.ValueType.FLOAT, a_default=0.2),
        Settings.VariableInfo(a_name="tstlan_show_marks", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=0),
        Settings.VariableInfo(a_name="tstlan_marks", a_section="PARAMETERS", a_type=Settings.ValueType.LIST_INT),
        Settings.VariableInfo(a_name="tstlan_graphs", a_section="PARAMETERS", a_type=Settings.ValueType.LIST_INT),
        Settings.VariableInfo(a_name="last_configuration_path", a_section="PARAMETERS", a_type=Settings.ValueType.STRING),
        Settings.VariableInfo(a_name="meter_type", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=0),
        Settings.VariableInfo(a_name="agilent_connect_type", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=0),
        Settings.VariableInfo(a_name="agilent_gpib_index", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=0),
        Settings.VariableInfo(a_name="agilent_gpib_address", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=22),
        Settings.VariableInfo(a_name="agilent_com_name", a_section="PARAMETERS", a_type=Settings.ValueType.STRING, a_default="com4"),
        Settings.VariableInfo(a_name="agilent_ip_address", a_section="PARAMETERS", a_type=Settings.ValueType.STRING, a_default="0.0.0.0"),
        Settings.VariableInfo(a_name="agilent_port", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=0),
        Settings.VariableInfo(a_name="switch_to_active_cell", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=0),
        Settings.VariableInfo(a_name="graph_parameters_splitter_size", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=500),
        Settings.VariableInfo(a_name="show_scheme_in_cell", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=1),
    ])

import os


def delete_convert_ui_strings(a_tmp_file):
    with open("main.py", encoding='utf8') as main_py:
        with open(a_tmp_file, "w", encoding='utf8') as compile_main:
            for line in main_py:
                if not ("ui_to_py" in line):
                    compile_main.write(line)


def restore_convert_ui_strings(a_tmp_file):
    os.remove(a_tmp_file)


if __name__ == "__main__":
    tmp_file = "Clb_AutoCalibration.py"

    delete_convert_ui_strings(tmp_file)
    os.system(
        f'pyinstaller --onefile --noconsole --icon=main_icon.ico '
        f'--add-data "C:\\Windows\\System32\\vcruntime140d.dll";. '
        f'--add-data "C:\\Windows\\System32\\ucrtbased.dll";. '
        f'--add-data "C:\\Users\\503\\Desktop\\Qt Projects\\mxsrclib_dll\\mxsrclib_dll\\CDMv2.12.28\\i386\\ftd2xx.dll";. '
        f'--add-data "C:\\Users\\503\\Desktop\\Python projects\\clb_autocalibration\\irspy\\clb\\clb_driver_dll.dll";. '
        f'--add-data "C:\\Users\\503\\Desktop\\Python projects\\clb_autocalibration\\irspy\\dlls\\mxsrclib_dll.dll";. '
        f'{tmp_file}'
    )
    restore_convert_ui_strings(tmp_file)

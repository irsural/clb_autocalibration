import os


def delete_convert_ui_strings(a_tmp_file):
    with open("main.py") as main_py:
        with open(a_tmp_file, "w+") as compile_main:
            for line in main_py:
                if not ("ui_to_py" in line):
                    compile_main.write(line)


def restore_convert_ui_strings(a_tmp_file):
    os.remove(a_tmp_file)


if __name__ == "__main__":
    tmp_file = "main_to_compile.py"

    delete_convert_ui_strings(tmp_file)
    os.system(f"pyinstaller -n clb_autocheck --onefile --noconsole --icon=main_icon.ico --add-data "
              f"C:\\Windows\\System32\\vcruntime140d.dll;. --add-data C:\\Windows\\System32\\ucrtbased.dll;. "
              f"{tmp_file}")
    restore_convert_ui_strings(tmp_file)

import os
import json
import hashlib

HASHES_FILE = "hashes.json"


def convert_ui(path_in=".", path_out="."):
    __convert_gui("pyuic5 {_in} > {_out}", ".ui", ".py", path_in, path_out)


def convert_resources(path_in=".", path_out="."):
    __convert_gui("pyrcc5 {_in} > {_out}", ".qrc", "_rc.py", path_in, path_out)


def __convert_gui(convert_cmd: str, ext_in: str, ext_out: str, path_in=".", path_out="."):
    hashes_path = "{0}/{1}".format(path_in, HASHES_FILE)
    try:
        with open(hashes_path, 'r') as hashes_file:
            hashes = json.load(hashes_file)
    except FileNotFoundError:
        hashes = {}

    for r, d, f in os.walk(path_in):
        for file in f:
            if ext_in in file:
                ui_filename = "{0}/{1}".format(path_in, file)
                ui_current_hash = __get_file_hash(ui_filename)
                ui_prev_hash = "" if ui_filename not in hashes.keys() else hashes[ui_filename]

                py_filename = "{0}/{1}".format(path_out, file.replace(ext_in, ext_out))

                if ui_prev_hash != ui_current_hash or not os.path.isfile(py_filename):
                    hashes[ui_filename] = ui_current_hash
                    os.system(convert_cmd.format(_in=ui_filename, _out=py_filename))

    with open(hashes_path, 'w') as hashes_file:
        json.dump(hashes, hashes_file)


def __get_file_hash(a_filename):
    with open(a_filename, 'rb') as file:
        return hashlib.md5(file.read()).hexdigest()


if __name__ == "__main__":
    convert_ui("./ui", "./ui/py")
    convert_resources("./resources", ".")

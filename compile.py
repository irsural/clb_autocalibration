import irspy.pyinstaller_build as py_build

import os

from revisions import Revisions


if __name__ == "__main__":
    libs = [
        'C:\\Windows\\System32\\vcruntime140d.dll',
        'C:\\Windows\\System32\\ucrtbased.dll',
        'C:\\Users\\503\\Desktop\\Python projects\\clb_autocalibration\\irspy\\clb\\clb_driver_dll.dll',
        'C:\\Users\\503\\Desktop\\Python projects\\clb_autocalibration\\irspy\\dlls\\mxsrclib_dll.dll',
        # 'C:\\Users\\503\\Desktop\\Qt Projects\\mxsrclib_dll\\mxsrclib_dll\\CDMv2.12.28\\i386\\ftd2xx.dll'
    ]

    py_build.build_qt_app(a_main_filename="main.py",
                          a_app_name="Clb_AutoCalibration",
                          a_version=Revisions.clb_autocalibration,
                          a_icon_filename="main_icon.ico",
                          a_noconsole=True,
                          a_one_file=True,
                          a_libs=libs)

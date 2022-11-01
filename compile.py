import irspy.pyinstaller_build as py_build

import app_info


if __name__ == "__main__":
    app_info = py_build.AppInfo(a_app_name=app_info.SHORT_NAME,
                                a_version=app_info.VERSION,
                                a_company_name='ООО "РЭС"',
                                a_file_description=app_info.FULL_NAME,
                                a_internal_name=app_info.SHORT_NAME,
                                a_copyright='ООО РЭС(c)',
                                a_original_filename=app_info.FULL_NAME,
                                a_product_name=app_info.FULL_NAME)

    libs = [
        ('C:\\Windows\\System32\\vcruntime140d.dll', '.'),
        ('C:\\Windows\\System32\\ucrtbased.dll', '.'),
        ('irspy\\clb\\clb_driver_dll.dll', '.\\irspy\\clb'),
        ('irspy\\dlls\\mxsrclib_dll.dll', '.\\irspy\\dlls')
    ]

    py_build.build_qt_app(a_main_filename="main.py",
                          a_app_info=app_info,
                          a_icon_filename="main_icon.ico",
                          a_noconsole=True,
                          a_one_file=True,
                          a_libs=libs)


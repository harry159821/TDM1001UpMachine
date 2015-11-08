#!/usr/bin/python
# -*- coding:utf-8 -*-
from distutils.core import setup
import py2exe
import time,shutil,os
TIME = time.time()
print u"Pack Begining 开始打包"

setup(
    version = "1.0",
    description = u"UpMachine",
    name = "UpMachine",
    url = None,
    author = u'harry159821',
    author_email = u'harry159821@gmail.com',
    license = "UpMachine License",
    zipfile= None, # 'library.zip', 
    windows=[{
                "script":"UpMachine.py", # 列举出转换成GUI窗口程序的脚本
                'icon_resources': [(1, './icon.ico')],  # 程序图标
                'copyright': "Copyright (c) 2015 harry159821." # copyright
            }],
    options={
        "py2exe":{
            "optimize":2,       # 优化
            "compressed":2,     # 压缩
            "bundle_files":1,
            "includes":["sip",  # 包含的库
                        "PyQt4.QtGui", 
                        "PyQt4.QtCore", 
                        "serial",
                        # "pyqtgraph",
                        # "numpy",
                        "CRCModules"],              
            "dll_excludes":["msvcm90.dll", # 不包含的DLL库
                            "msvcp90.dll", 
                            "msvcr90.dll"]
                }
            }
    )

print u"Pack Ending 打包完毕"
print u'用时:',time.time()-TIME

if os.path.isdir('build'): # 清除build文件夹
    shutil.rmtree('build')

'''
DESCRIPTION
    New keywords for distutils' setup function specify what to build:
    
        console
            list of scripts to convert into console exes
            列举出转换成控制台程序的脚本
    
        windows
            list of scripts to convert into gui exes
            列举出转换成GUI窗口程序的脚本
    
        service
            list of module names containing win32 service classes
    
        com_server
            list of module names containing com server classes
    
        ctypes_com_server
            list of module names containing com server classes
    
        zipfile
            name of shared zipfile to generate, may specify a subdirectory,
            defaults to 'library.zip'
    
    
    py2exe options, to be specified in the options keyword to the setup function:
    
        unbuffered - if true, use unbuffered binary stdout and stderr
        optimize - string or int (0, 1, or 2)
    
        includes - list of module names to include
        packages - list of packages to include with subpackages
        ignores - list of modules to ignore if they are not found
        excludes - list of module names to exclude
        dll_excludes - list of dlls to exclude
    
        dist_dir - directory where to build the final files
        typelibs - list of gen_py generated typelibs to include (XXX more text needed)
    
    Items in the console, windows, service or com_server list can also be
    dictionaries to further customize the build process.  The following
    keys in the dictionary are recognized, most are optional:
    
        modules (SERVICE, COM) - list of module names (required)
        script (EXE) - list of python scripts (required)
        dest_base - directory and basename for the executable
                    if a directory is contained, must be the same for all targets
        create_exe (COM) - boolean, if false, don't build a server exe
        create_dll (COM) - boolean, if false, don't build a server dll
        bitmap_resources - list of 2-tuples (id, pathname)
        icon_resources - list of 2-tuples (id, pathname)
        other_resources - list of 3-tuples (resource_type, id, datastring)

'''

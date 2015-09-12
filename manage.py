#!/usr/bin/env python
import subprocess
import os
import sys

if __name__ == "__main__":
    # Verficamos con git en que rama nos encontramos
    if len (sys.argv) == 1:
        # Si tiene 1 argumento...
        pass
    print("getcwd: " + os.getcwd())
    stdoutdata = subprocess.check_output(
        'git --work-tree=\"' + os.getcwd() + '\" --git-dir=\"' + os.getcwd() + '/.git\" status',
        shell=True
    )
    #print('-----------------------stdoutdata')
    #print(stdoutdata)
    #print('---------------------------------')

    # Compara byte array
    if b'On branch develop' in stdoutdata:
        import manage.manage_develop
        #exec(open('manage/manage_develop.py').read())
    elif b'On branch pre' in stdoutdata:
        import manage.manage_pre
        #exec(open('manage/manage_pre.py').read())
    elif b'On branch master' in stdoutdata:
        import manage.manage_master
        #exec(open('manage/manage_master.py').read())
    else:
        pass


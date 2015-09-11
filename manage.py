#!/usr/bin/env python

import subprocess

if __name__ == "__main__":
    # Verficamos con git en que rama nos encontramos
    stdoutdata = subprocess.check_output("git status", shell=True)

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


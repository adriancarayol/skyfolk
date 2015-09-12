#!/usr/bin/env python
import subprocess
import os
import sys

if __name__ == "__main__":

    if os.path.isfile("/var/www/skyfolk/run/deploy-master.lock"):
        entorno = "master"
    elif os.path.isfile("/var/www/skyfolk/run/deploy-pre.lock"):
        entorno = "pre"
    else:
        entorno = "develop"

    if entorno == "master":
        import manage.manage_master
    elif entorno == "pre":
        import manage.manage_pre
    else:
        import manage.manage_develop


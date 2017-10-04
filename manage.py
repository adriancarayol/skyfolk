#!/usr/bin/env python
import os
import subprocess
import sys
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    # import ipdb;ipdb.set_trace()
    # verificamos si param --entorno [develop|pre|master]
    deploy = False
    try:
        primerParam = str(sys.argv[1])
        segundoParam = str(sys.argv[2])
    except:
        # sys.exit(0)
        # print("catch")
        primerParam = "null"
        segundoParam = "null"

    print("primer parametro: " + primerParam + " segundo paramentro: " + segundoParam)
    if primerParam == "--entorno" and (segundoParam == "develop" or
                                               segundoParam == "pre" or
                                               segundoParam == "master"):
        # print("Antes de extraer parametros: " + str(sys.argv))
        deploy = True
        entorno = segundoParam
        sys.argv.remove(str(sys.argv[1]))
        sys.argv.remove(str(sys.argv[1]))
        # print("Despues de extraer parametros: " + str(sys.argv))
    else:
        # develop
        entorno = "develop"

    print("Lanzando entorno: [" + entorno + " / argv: " + str(sys.argv) + "]")
    if entorno == "master":
        os.environ['DAPHNE_RUNLEVEL'] = 'master'
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skyfolk.settings.master")
        execute_from_command_line(sys.argv)
    elif entorno == "pre":
        os.environ['DAPHNE_RUNLEVEL'] = 'pre'
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skyfolk.settings.pre")
        execute_from_command_line(sys.argv)
    else:
        # develop
        os.environ['SECRET_KEY'] = 'develop'
        os.environ['DAPHNE_RUNLEVEL'] = 'develop'
        os.environ['RABBIT_PORT_5672_TCP'] = 'localhost:5672'
        os.environ['NEO4J_BOLT_URL'] = 'localhost'
        os.environ['ELASTICSEARCH_URL'] = 'localhost'

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skyfolk.settings.develop")

        execute_from_command_line(sys.argv)

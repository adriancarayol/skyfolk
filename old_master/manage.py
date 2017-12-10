#!/usr/bin/env python
import subprocess
import os
import sys


if __name__ == "__main__":

    # verificamos si param --entorno [develop|pre|master]
    deploy = False
    try:
        primerParam = str(sys.argv[1])
        segundoParam = str(sys.argv[2])
    except:
        #sys.exit(0)
        #print("catch")
        primerParam = "null"
        segundoParam = "null"

    #print("primerParam: " + primerParam + " / segundoParam" + segundoParam)
    if primerParam == "--entorno" and ( segundoParam == "develop" or
                                        segundoParam == "pre" or
                                        segundoParam == "master" ):
        #print("Antes de extraer parametros: " + str(sys.argv))
        deploy = True
        entorno = segundoParam
        sys.argv.remove(str(sys.argv[1]))
        sys.argv.remove(str(sys.argv[1]))
        #print("Despues de extraer parametros: " + str(sys.argv))
    else:
        #develop
        entorno = "develop"

    print("entorno: " + entorno + " / argv: " + str(sys.argv))
    if entorno == "master":
        import manage.manage_master
    elif entorno == "pre":
        import manage.manage_pre
    else:
        #develop
        import manage.manage_develop

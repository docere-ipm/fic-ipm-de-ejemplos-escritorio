#!/usr/bin/env python3

# En python usamos Gtk a traves de GObject Introspection.
# https://gi.readthedocs.io/en/latest/ Es una idea muy interesante,
# pero fuera del ámbito de las IGUs.
import gi

# Usaremos la versión 4 de Gtk. Se puede usar la versión 3 haciendo
# los cambios pertienentes.
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


if __name__ == '__main__':
    # Es habitual en muchas librerías gráficas tener un objeto que
    # representa la aplicación.
    app = Gtk.Application(application_id= "es.udc.fic.ipm.HelloWorld")

    # Una vez finalizada la inicialización de la aplicación, le
    # pasamos el control a la librería.  Se podría decir que esta es
    # la implementación del `main` en la librería.
    app.run(None)

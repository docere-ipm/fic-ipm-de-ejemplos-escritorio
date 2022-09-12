#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


def on_activate(app: Gtk.Application) -> None:
    # Es habitual que las librerías gráficas sigan un diseño OO, donde
    # tenemos que crear una instancia por cada widget.
    # Cada librería tiene su api y su galería de widgets.
    
    # Creamos una ventana, inicializando algunas de sus propiedades.
    win = Gtk.ApplicationWindow(title= "¡Hola Mundo!",
                                default_width= 600,
                                default_height= 400)
    
    # Añadimos la ventana a la aplicación.
    app.add_window(win)

    # En GTK tenemos que programar explicitamente que un widget sea
    # visible.
    win.present()


if __name__ == '__main__':
    app = Gtk.Application(application_id= "es.udc.fic.ipm.HelloWorld")

    # Antes de pasar el control a la librería, tenemos que establecer
    # una función o método que se encarge de crear la interface.
    app.connect('activate', on_activate)
    app.run(None)

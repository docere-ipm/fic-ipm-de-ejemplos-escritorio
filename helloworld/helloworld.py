#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


def on_activate(app: Gtk.Application) -> None:
    win = Gtk.ApplicationWindow(title= "¡Hola Mundo!",
                                default_width= 600,
                                default_height= 400)    
    app.add_window(win)

    # Conectamos el evento 'destroy' con el _callback_
    # correspondiente.

    # El método `ApplicationWindow.close` hace que `Application.run`
    # termine.
    win.connect("destroy", lambda win: win.close())

    win.present()


if __name__ == '__main__':
    app = Gtk.Application(application_id= "es.udc.fic.ipm.HelloWorld")
    app.connect('activate', on_activate)

    # En las interfaces gráficas no podemos hacer una programación
    # secuencial.

    # La mayor parte del tiempo, a aplicación está esperando a que la
    # usuaria interactúe con la interface. En respuesta a esa
    # interacción, _evento_, se ejecutan las instrucciones
    # pertienentes, _función_ o _método_.

    # El _bucle de eventos_ ya está implementado en la
    # librería. P.e. en GTK está dentro de `app.run`. Nuestra
    # aplicación tiene que establecer qué funciones/métodos se
    # ejecutan con cada evento. Esto se hacer por cada widget. Los
    # eventos están asociados al widget con el que se produjo la
    # interacción. La manera de hacerlo depende del api de la
    # librería, p.e. en GTK es un mecanismo de callbacks.
    app.run(None)

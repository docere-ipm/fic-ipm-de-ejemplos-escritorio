#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


# En GTK los manejadores de eventos, reciven un parámetro: el widget
# en el que se produjo el evento.
def on_button_clicked(w: Gtk.Widget) -> None:
    print("Hello!")
    

def on_activate(app: Gtk.Application) -> None:
    win = Gtk.ApplicationWindow(title= "¡Hola Mundo!",
                                default_width= 600,
                                default_height= 400)    
    app.add_window(win)
    win.connect("destroy", lambda win: win.close())

    # Añadimos un `Button`
    # Los botones son widgets que al activarlos lanzan una acción.
    #
    #   - activar = hacer click | pulsar espacio
    #
    #   - ¿ Cómo sabe la usuaria que es un botón ? ¿ y cómo sabe
    #     que lanza una acción ?
    #
    #   - Si hay varios widgets, ¿ Cómo sabemos que pulsar espacio
    #   - activa este botón ?
    button = Gtk.Button(label= "Print hello")
    button.connect('clicked', on_button_clicked)
    win.set_child(button)
    
    win.present()


if __name__ == '__main__':
    app = Gtk.Application(application_id= "es.udc.fic.ipm.HelloWorld")
    app.connect('activate', on_activate)
    app.run(None)

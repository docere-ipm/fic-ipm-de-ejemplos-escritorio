#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


WINDOW_PADDING: int = 24


# Vamos a añadir estado a la aplicación. Como no tenemos ningún
# patrón para aplicar, haremos una chapuza con variables globales.
state: int = 0
label: Gtk.Label = None

# TIP: Si metemos todo esto en una clase, sigue siendo la misma
# chapuza. En vez de tener todo global en el ámbito del módulo, lo
# tenemos en el ámbito de una clase.


# Función de utilidad que calcula el texto a mostrar en la etiqueta a
# partir del estado
def get_label_text() -> str:
    if state == 1:
        return "I've said hello 1 time"
    else:
        return f"I've said hello {state} times"
    
    
def on_say_hello_clicked(w: Gtk.Widget) -> None:
    # Modificamos el estado
    global state
    state = state + 1

    # Actualizamos la vista
    label.set_label(get_label_text())

    # Importante: dejamos de imprimir en la salida estándar. Estuvo
    # bien para hacer un ejemplo rápido, pero esto es una interface
    # gráfica, la salida en el terminal no está incluida.


def counter() -> Gtk.Widget:
    # Queremos modificar la variable global
    global label
    box = Gtk.Box(
        orientation= Gtk.Orientation.VERTICAL,
        homogeneous= False,
        spacing= 12,
        margin_top= WINDOW_PADDING,
        margin_end= WINDOW_PADDING,
        margin_bottom= WINDOW_PADDING,
        margin_start= WINDOW_PADDING
    )
    label = Gtk.Label(
        # Importante: inicializar a partir del estado
        label= get_label_text(),
        halign= Gtk.Align.CENTER,
        vexpand= True
    )
    button = Gtk.Button(
        label= "Say Hello",
        halign= Gtk.Align.CENTER
    )
    box.append(label)
    box.append(button)
    button.connect('clicked', on_say_hello_clicked)
    return box


def on_activate(app: Gtk.Application) -> None:
    win = Gtk.ApplicationWindow(
        title= "¡Hola Mundo!",
    )    
    app.add_window(win)
    win.connect("destroy", lambda win: win.close())
    win.set_child(counter())
    win.present()


if __name__ == '__main__':
    app = Gtk.Application(application_id= "es.udc.fic.ipm.HelloWorld")
    app.connect('activate', on_activate)
    app.run(None)

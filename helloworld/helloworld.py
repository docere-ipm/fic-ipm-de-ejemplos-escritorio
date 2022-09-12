#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

# En otros lenguajes, esto sería una constante.
WINDOW_PADDING: int = 24


def on_say_hello_clicked(w: Gtk.Widget) -> None:
    print("Hello!")


# Si tenemos más de un widget dentro de la ventana, tenemos que
# resolver el _layout_:
#
#   - ¿ Cómo indicamos la posición de cada uno ?
#   - ¿ Cómo indicamos el tamaño de cada uno ?
#
# a. En entornos siempre iguales y conocidos (muy raro):
#    coordenadas y tamaño en pixels
#
# b. _Containers_, _contenedores_: objetos que calculan el layout
#    de sus hijos según un criterio.


def counter() -> Gtk.Widget:
    # `Box` es un contenedor básico, dispone sus hijos en línea,
    # vertical u horizontal.
    #
    # En esta aplicación no se da el caso, pero un container puede ser
    # hijo de otro container. Esto nos permite crear layouts
    # complejos.
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
        label= "Hello!",
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
    # La parte que crea los widgets contenidos en la ventana la
    # separamos a otra función para organizar el código.
    #
    # El código que crea la interface suele ser largo. La manera de
    # organizarlo ya va en el estilo de programación.
    win.set_child(counter())
    win.present()


if __name__ == '__main__':
    app = Gtk.Application(application_id= "es.udc.fic.ipm.HelloWorld")
    app.connect('activate', on_activate)
    app.run(None)

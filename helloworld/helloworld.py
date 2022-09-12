#!/usr/bin/env python3

from future import __annotations__
from typing import Optional


import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


# Vamos a aplicar el patrón MVP

# El componente estado/modelo se reduce a una clase.
class State:
    count: int= 0

    def incr_count(self, step: int= 1) -> None:
        self.count += step

    def get_count(self) -> int:
        return self.count


# El componente vista se reduce a una clase y una función.
def get_count_text(count: int) -> str:
    return (
        "I've said hello 1 time" if count == 1 else
        f"I've said hello {count} times"
    )


class View:
    WINDOW_PADDING: int = 24

    label: Gtk.Label = None

    # Esta no es la única forma de implementar esta parte. Por
    # ejemplo, en vez de pasar el Presenter como parámetro, podíamos
    # tener un método `View.connect_to(:Presenter)`
    def build(self, app: Gtk.Application, presenter: 'Presenter') -> None:
        win = Gtk.ApplicationWindow(
            title= "¡Hola Mundo!",
        )    
        app.add_window(win)
        win.connect("destroy", lambda win: win.close())
        win.set_child(self.counter(presenter))
        win.present()

    def counter(self, presenter: 'Presenter') -> Gtk.Widget:
        box = Gtk.Box(
            orientation= Gtk.Orientation.VERTICAL,
            homogeneous= False,
            spacing= 12,
            margin_top= View.WINDOW_PADDING,
            margin_end= View.WINDOW_PADDING,
            margin_bottom= View.WINDOW_PADDING,
            margin_start= View.WINDOW_PADDING
        )
        label = Gtk.Label(
            label= "",
            halign= Gtk.Align.CENTER,
            vexpand= True
        )
        button = Gtk.Button(
            label= "Say Hello",
            halign= Gtk.Align.CENTER
        )
        box.append(label)
        box.append(button)
        button.connect('clicked', presenter.on_say_hello_clicked)
        self.label = label
        return box

    def update_count_label(self, count: int) -> None:
        self.label.set_label(get_count_text(count))


# Finalmente el Presenter
class Presenter:
    def __init__(self, state: Optional[State]= None):
        state = state or State()
        self.state = state
        self.view = View()

    def run(self) -> None:
        app = Gtk.Application(application_id= "es.udc.fic.ipm.HelloWorld")
        app.connect('activate', self.on_activate)
        app.run(None)

    def on_activate(self, app: Gtk.Application) -> None:
        self.view.build(app, self)
        # La vista es totalmente pasiva. El presenter se encarga de
        # actualizarla en todo momento.
        self._update_count()
        
    def on_say_hello_clicked(self, _w: Gtk.Widget) -> None:
        # "Llamamos" al modelo
        self.state.incr_count()
        # Actualizamos la vista
        self._update_count()

    def _update_count(self) -> None:
        self.view.update_count_label(self.state.get_count())

        
if __name__ == '__main__':
    presenter = Presenter()
    presenter.run()

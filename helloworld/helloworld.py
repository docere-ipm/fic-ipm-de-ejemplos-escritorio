#!/usr/bin/env python3

from __future__ import annotations
import gettext
import locale
from pathlib import Path
import threading
from typing import Optional


import gi
gi.require_version('Gtk', '4.0')
# Necesitamos una función de GLib (Gtk -> Gdk -> GLib -> GObject)
from gi.repository import Gtk, GLib


_ = gettext.gettext
N_ = gettext.ngettext


class State:
    count: int= 0

    def incr_count(self, step: int= 1) -> None:
        import time
        time.sleep(3)
        self.count += step

    def get_count(self) -> int:
        return self.count


def get_count_text(count: int) -> str:
    return N_(
        "I've said hello {0} time",
        "I've said hello {0} times",
        count
    ).format(count)


class View:
    WINDOW_PADDING: int = 24

    label: Gtk.Label = None

    def build(self, app: Gtk.Application, presenter: Presenter) -> None:
        win = Gtk.ApplicationWindow(
            title= _("Hello World!"),
        )    
        app.add_window(win)
        win.connect("destroy", lambda win: win.close())
        win.set_child(self.counter(presenter))
        win.present()

    def counter(self, presenter: Presenter) -> Gtk.Widget:
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
            label= _("Say Hello"),
            halign= Gtk.Align.CENTER
        )
        box.append(label)
        box.append(button)
        button.connect('clicked', presenter.on_say_hello_clicked)
        self.label = label
        return box

    def update_count_label(self, count: int) -> None:
        self.label.set_label(get_count_text(count))


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
        self._update_count()
        
    def on_say_hello_clicked(self, _w: Gtk.Widget) -> None:
        threading.Thread(target= self.say_hello, daemon= True).start()
        # Cuando la usuaria activa el botón
        # Preguntas, problemas, ...:
        #
        # - El botón lanza una acción, una acción requiere una
        #   respuesta/resultado, pero durante varios segundos no
        #   ocurre nada. Bad UX.
        #
        # - ¿ Si se está ejecutando la acción, ¿ tiene sentido lanzar
        #   otra ?
        #
        # - Si no tiene sentido lanzar dos acciones simultáneas, ¿
        #   cómo lo evitamos ?
        #
        # - Si tiene sentido lanzar más de una acción simultánea, ¿
        #   cómo las sincronizamos ?  P.e.: ¿ qué pasa si el click nº5
        #   termina antes que el nº4 ?
        #
        # - La operación tarda mucho tiempo y no se puede
        #   cancelar. Bad UX.
        
    def say_hello(self) -> None:
        self.state.incr_count()
        GLib.idle_add(self._update_count)

    def _update_count(self) -> None:
        self.view.update_count_label(self.state.get_count())

        
if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    LOCALE_DIR = Path(__file__).parent / "locale"
    locale.bindtextdomain('HelloWorld', LOCALE_DIR)
    gettext.bindtextdomain('HelloWorld', LOCALE_DIR)
    gettext.textdomain('HelloWorld')
    
    presenter = Presenter()
    presenter.run()


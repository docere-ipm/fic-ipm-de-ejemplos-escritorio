#!/usr/bin/env python3

from __future__ import annotations
import gettext
import locale
from pathlib import Path
import threading
from typing import Optional


import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


_ = gettext.gettext
N_ = gettext.ngettext


class State:
    count: int= 0

    def incr_count(self, step: int= 1) -> int:
        import time
        time.sleep(3)
        return self.count + step

    def commit(self, state: int) -> None:
        self.count = state
        
    def get_count(self) -> int:
        return self.count


def get_count_text(count: int) -> str:
    return N_(
        "I've said hello {0} time",
        "I've said hello {0} times",
        count
    ).format(count)


class View:
    idle_add = GLib.idle_add
    
    WINDOW_PADDING: int = 24

    window: Gtk.ApplicationWindow = None
    label: Gtk.Label = None
    spinner: Gtk.Spinner = None
    cancel: Gtk.Button = None
    button: Gtk.Button = None

    def build(self, app: Gtk.Application, presenter: Presenter) -> None:
        win = Gtk.ApplicationWindow(
            title= _("Hello World!"),
        )    
        app.add_window(win)
        win.connect("destroy", lambda win: win.close())
        win.set_child(self.counter(presenter))
        self.window = win
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
        label_box = Gtk.Box(
            orientation= Gtk.Orientation.HORIZONTAL,
            homogeneous= False,
            spacing= 8,
            vexpand= True
        )
        label = Gtk.Label(
            label= "",
            halign= Gtk.Align.CENTER,
            hexpand= True
        )
        spinner = Gtk.Spinner(hexpand= False)
        spinner.hide()
        cancel = Gtk.Button(label= _("Cancel"), hexpand= False)
        cancel.hide()
        cancel.connect('clicked', presenter.on_say_hello_cancelled)
        label_box.append(label)
        label_box.append(spinner)
        label_box.append(cancel)
        button = Gtk.Button(
            label= _("Say Hello"),
            halign= Gtk.Align.CENTER
        )
        box.append(label_box)
        box.append(button)
        button.connect('clicked', presenter.on_say_hello_clicked)
        self.label = label
        self.spinner = spinner
        self.cancel = cancel
        self.button = button
        return box

    def update_count_label(self, count: int) -> None:
        self.label.set_label(get_count_text(count))

    def show_saying_indicator(self, showing: bool) -> None:
        if showing:
            self.label.set_label("Counting ...")
            self.spinner.show()
            self.cancel.show()
            self.spinner.start()
        else:
            self.spinner.stop()
            self.spinner.hide()
            self.cancel.hide()
            
    def info(self, text: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for= self.window,
            modal= True,
            message_type= Gtk.MessageType.INFO,
            buttons= Gtk.ButtonsType.OK,
            text= text,
        )
        dialog.connect('response', lambda d, _: d.destroy())
        dialog.show()


class Presenter:
    def __init__(self, state: Optional[State]= None):
        state = state or State()
        self.state = state
        self.view = View()
        self.saying_hello_thread = None

    def run(self) -> None:
        app = Gtk.Application(application_id= "es.udc.fic.ipm.HelloWorld")
        app.connect('activate', self.on_activate)
        app.run(None)

    def on_activate(self, app: Gtk.Application) -> None:
        self.view.build(app, self)
        self._update_count(None)
        
    def on_say_hello_clicked(self, _w: Gtk.Widget) -> None:
        # Aprovechamos para organizar el código de otra manera
        def say_hello() -> None:
            state = self.state.incr_count()
            View.idle_add(self._update_count, state, threading.current_thread())
            # En python la creación de _closures_ tienen limitaciones,
            # pero aquí prodríamos usarlos:
            # View.idle_add(lambda: self._update_count(state, threading.current_thread())

        if self.saying_hello_thread is not None:
            self.view.info(_("I'm already in the process of saying hello"))
        else:
            new_thread = threading.Thread(target= say_hello, daemon= True)
            self.saying_hello_thread = new_thread
            self.view.show_saying_indicator(True)
            new_thread.start()

        # Cuando la usuaria activa el botón
        # Preguntas, problemas, ...:
        #
        # En este ejemplo, ésto no tiene sentido.
        # Queda como ejercicio.
        # - Si tiene sentido lanzar más de una acción simultánea, ¿
        #   cómo las sincronizamos ?  P.e.: ¿ qué pasa si el click nº5
        #   termina antes que el nº4 ?
        #

    def on_say_hello_cancelled(self, _w: Gtk.Widget) -> None:
        self.saying_hello_thread = None
        self._update_count(None)
        
    def _update_count(
            self,
            state: Optional[int], # None significa no hay estado nuevo, usar el actual
            from_thread: Optional[threading.Thread]= None
    ) -> None:
        if state is not None and self.saying_hello_thread == from_thread:
            # Si hay estado nuevo y no se cancelo el Thread
            self.state.commit(state)
            self.saying_hello_thread = None
        if self.saying_hello_thread is None:
            self.view.show_saying_indicator(False)
            self.view.update_count_label(self.state.get_count())

        
if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    LOCALE_DIR = Path(__file__).parent / "locale"
    locale.bindtextdomain('HelloWorld', LOCALE_DIR)
    gettext.bindtextdomain('HelloWorld', LOCALE_DIR)
    gettext.textdomain('HelloWorld')
    
    presenter = Presenter()
    presenter.run()


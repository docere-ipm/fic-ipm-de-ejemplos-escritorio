from __future__ import annotations


import gettext
from typing import Callable, Protocol


import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


_ = gettext.gettext
N_ = gettext.ngettext


def run(application_id: str, on_activate: Callable) -> None:
    app = Gtk.Application(application_id= application_id)
    app.connect('activate', on_activate)
    app.run(None)

    
run_on_main_thread = GLib.idle_add
# En este ejemplo si falla si usamos Gtk desde un thread auxiliar
# run_on_main_thread = lambda f, *args: f(*args)


class FlightBookerViewHandler(Protocol):
    def on_built(view: FlightBookerView) -> None: pass
    def on_flight_type_changed(one_way: bool) -> None: pass
    def on_start_date_changed(text: str) -> None: pass
    def on_return_date_changed(text: str) -> None: pass
    def on_book_clicked() -> None: pass
    def on_book_cancelled() -> None: pass
    

WINDOW_PADDING = 20


class FlightBookerView:
    # Estas variables realmente no se llegan a usar nunca, porque lo
    # primero que hacemos es escribirlas. Pero así simulamos que las
    # hemos declarado.
    window: Gtk.ApplicationWindow = None
    flight_type: Gtk.ComboBox = None
    start_date_entry: Gtk.Entry = None
    return_date_entry: Gtk.Entry = None
    
    def __init__(self):
        self.handler = None

    def set_handler(self, handler: FlightBookerViewHandler) -> None:
        self.handler = handler
        
    def on_activate(self, app: Gtk.Application) -> None:
        self.build(app)
        self.handler.on_built(self)

    def build(self, app: Gtk.Application) -> None:
        self.window = win = Gtk.ApplicationWindow(
            title= _("Flight Booker"),
        )    
        app.add_window(win)
        win.connect("destroy", lambda win: win.close())

        box = Gtk.Box(
            orientation= Gtk.Orientation.VERTICAL,
            homogeneous= False,
            spacing= 12,
            margin_top= WINDOW_PADDING,
            margin_end= WINDOW_PADDING,
            margin_bottom= WINDOW_PADDING,
            margin_start= WINDOW_PADDING
        )
        box.append(self.flight_type_input())
        box.append(self.start_date_input())
        box.append(self.return_date_input())
        box.append(book_button := Gtk.Button(label= _("Book")))
        self.book_button = book_button
        book_button.connect('clicked', lambda _wg: self.handler.on_book_clicked())

        win.set_child(box)
        win.present()

    def flight_type_input(self) -> Gtk.Widget:
        flight_type_store = Gtk.ListStore(str)
        flight_type_store.append([_("one-way flight")])
        flight_type_store.append([_("return flight")])
        self.flight_type = flight_type = Gtk.ComboBox(
            model=flight_type_store,
            entry_text_column= 0,
            active= 0)
        renderer_text = Gtk.CellRendererText()
        flight_type.pack_start(renderer_text, True)
        flight_type.add_attribute(renderer_text, "text", 0)
        flight_type.connect(
            'changed',
            lambda wg: self.handler.on_flight_type_changed(one_way= wg.get_active() == 0)
        )
        return flight_type

    def start_date_input(self) -> Gtk.Widget:
        self.start_date_entry = start_date_entry = Gtk.Entry(text= "")
        start_date_entry.connect(
            'changed',
            lambda wg: self.handler.on_start_date_changed(text= wg.get_text())
        )
        return start_date_entry
    
    def return_date_input(self) -> Gtk.Widget:
        self.return_date_entry = return_date_entry = Gtk.Entry(text= "")
        return_date_entry.connect(
            'changed',
            lambda wg: self.handler.on_return_date_changed(text= wg.get_text())
        )
        return return_date_entry

    def update(
            self,
            return_date_enabled: bool,
            book_enabled: bool
    ) -> None:
        self.return_date_entry.set_sensitive(return_date_enabled)
        self.book_button.set_sensitive(book_enabled)


    def show_info(self, text: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for= self.window,
            modal= True,
            message_type= Gtk.MessageType.INFO,
            buttons= Gtk.ButtonsType.OK,
            text= text,
        )
        dialog.connect('response', lambda d, _: d.destroy())
        dialog.show()

    def show_error(self, text: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for= self.window,
            modal= True,
            message_type= Gtk.MessageType.ERROR,
            buttons= Gtk.ButtonsType.CLOSE,
            text= text,
        )
        dialog.connect('response', lambda d, _: d.destroy())
        dialog.show()

    def show_book_dialog(self) -> Gtk.Dialog:
        def on_response(dialog: Gtk.Dialog, _response: int) -> None:
            dialog.destroy()
            self.handler.on_book_cancelled()
            
        dialog = Gtk.MessageDialog(
            transient_for= self.window,
            modal= True,
            message_type= Gtk.MessageType.ERROR,
            buttons= Gtk.ButtonsType.CLOSE,
            text= "Booking ...",
        )
        box = dialog.get_child()
        label = box.get_first_child()
        box.insert_child_after(spinner := Gtk.Spinner(), label)
        spinner.start()
        dialog.connect('response', on_response)
        dialog.show()
        return dialog

    def destroy_dialog(self, dialog: Gtk.Dialog) -> None:
        # No nos interesa que el Presenter haga ninguna llamada a Gtk.
        dialog.destroy()

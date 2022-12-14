from __future__ import annotations


from enum import Enum
import gettext
from typing import Callable, Protocol


import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


from date_utils import date_sample, show_date


_ = gettext.gettext
N_ = gettext.ngettext


class UIText(Enum):
    BOOKING = _("Booking ...")
    BOOK_SUCCESS = _("Sucessfully booked")
    CONTACTING_SERVER = _("Contacting server ...")
    SENDING_DATA = _("Sending booking data ...")
    WAITING_ANSWER = _("Waiting for server's response ...")
    WRONG_DATE_FORMAT = _("Date format is: {0}")
    MANDATORY_FIELD = _("This field is mandatory")
    INVALID_DATE = _("Date is not valid")

def run(application_id: str, on_activate: Callable) -> None:
    app = Gtk.Application(application_id= application_id)
    app.connect('activate', on_activate)
    app.run(None)

    
run_on_main_thread = GLib.idle_add
# En este ejemplo sí falla si usamos Gtk desde un thread auxiliar
# run_on_main_thread = lambda f, *args: f(*args)


class FlightBookerViewHandler(Protocol):
    def on_built(view: FlightBookerView) -> None: pass
    def on_flight_type_changed(one_way: bool) -> None: pass
    def on_start_date_changed(text: str) -> None: pass
    def on_return_date_changed(text: str) -> None: pass
    def on_book_clicked() -> None: pass
    def on_book_cancelled() -> None: pass
    

WINDOW_PADDING = 20


def toogle_class(widget: Gtk.Widget, class_name: str, value: bool) -> None:
    if value:
        widget.get_style_context().add_class(class_name)
    else:
        widget.get_style_context().remove_class(class_name)        


class DateEntry:
    def __init__(
            self,
            label: str,
            handler: Callable[[Gtk.Widget], None]
    ) -> tuple[Gtk.Widget, Gtk.Widget]:
        box = Gtk.Box(
            orientation= Gtk.Orientation.HORIZONTAL,
            homogeneous= False,
            spacing= 10,
            hexpand= True
        )
        box.append(
            Gtk.Label(label= label, hexpand= True, halign= Gtk.Align.START)
        )
        vbox = Gtk.Box(
            orientation= Gtk.Orientation.VERTICAL,
            homogeneous= False,
            spacing= 0,
            hexpand= True
        )
        vbox.append(
            entry := Gtk.Entry(
                text= "",
                hexpand= False,
                halign= Gtk.Align.END
            )
        )
        vbox.append(
            msg := Gtk.Label(label= "Algho farias", wrap= True, hexpand= True, halign= Gtk.Align.START)
        )
        box.append(vbox)
        msg.get_style_context().add_class('error')
        msg.hide()
        entry.set_placeholder_text(_("Example: {}").format(show_date(date_sample)))
        entry.connect('changed', handler)
        self.widget = box
        self.entry = entry
        self.msg = msg

    def show_feedback(self, feedback: Optional[tuple[str, str]]) -> None:
        # Siempre que hay un feedback es porque el dato no es correcto,
        # y al reves, si no hay feeback es porque el datao es correcto.
        if feedback is None:
            toogle_class(self.entry, 'error', False)
            self.msg.hide()
        else:
            cls_name, text = feedback
            toogle_class(self.entry, 'error', True)
            if cls_name == 'error':
                toogle_class(self.msg, 'error', True)
                toogle_class(self.msg, 'warning', False)
                self.msg.set_label(text)
                self.msg.show()
            elif cls_name == 'info':
                toogle_class(self.msg, 'warning', True)
                toogle_class(self.msg, 'error', False)
                self.msg.set_label(text)
                self.msg.show()
            else:
                raise ValueError(f"Unkown feedback.{cls_name=}")
        
    def set_sensitive(self, value: bool) -> None:
        self.entry.set_sensitive(value)
        

class FlightBookerView:
    window: Gtk.ApplicationWindow = None
    flight_type: Gtk.ComboBox = None
    start_date_entry: DateEntry = None
    return_date_entry: DateEntry = None
    
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
        box.append(book_button := Gtk.Button(
            label= _("Book"),
            hexpand= False,
            halign= Gtk.Align.CENTER)
        )
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
            active= 0,
            hexpand= False,
            halign= Gtk.Align.START
        )
        renderer_text = Gtk.CellRendererText()
        flight_type.pack_start(renderer_text, True)
        flight_type.add_attribute(renderer_text, "text", 0)
        flight_type.connect(
            'changed',
            lambda wg: self.handler.on_flight_type_changed(one_way= wg.get_active() == 0)
        )
        box = Gtk.Box(
            orientation= Gtk.Orientation.HORIZONTAL,
            homogeneous= False,
            spacing= 10,
            hexpand= True
        )
        box.append(
            Gtk.Label(
                label= _("Flight type:"),
                hexpand= True,
                halign= Gtk.Align.START
            )
        )
        box.append(flight_type)
        return box

    def start_date_input(self) -> Gtk.Widget:
        self.start_date_entry = DateEntry(
            _("Start date:"),
            lambda wg: self.handler.on_start_date_changed(text= wg.get_text())
        )
        return self.start_date_entry.widget
    
    def return_date_input(self) -> Gtk.Widget:
        self.return_date_entry = DateEntry(
            _("Return date:"),
            lambda wg: self.handler.on_return_date_changed(text= wg.get_text())
        )
        return self.return_date_entry.widget

    def update(
            self,
            start_date_feedback: Optional[tuple[str, str]],
            return_date_feedback: Optional[tuple[str, str]],
            return_date_enabled: bool,
            book_enabled: bool
    ) -> None:
        self.start_date_entry.show_feedback(start_date_feedback)
        self.return_date_entry.show_feedback(return_date_feedback)
        self.return_date_entry.set_sensitive(return_date_enabled)
        self.book_button.set_sensitive(book_enabled)
        # HACK: Parece la única forma "razonable" de que la ventana
        # cambie el tamaño cuando aparece y desaparece el feedback
        self.window.set_default_size(self.window.get_width(), 0)

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

    def progress_dialog(self, title: str) -> FlightBookerProgressDialog:
        dialog = Gtk.MessageDialog(
            transient_for= self.window,
            modal= True,
            message_type= Gtk.MessageType.INFO,
            buttons= Gtk.ButtonsType.CLOSE,
            text= title,
            secondary_text= ""
        )
        return FlightBookerProgressDialog(dialog, self.handler)


class FlightBookerProgressDialog:
    def __init__(self, dialog: Gtk.Dialog, handler: FlightBookerViewHandler):
        def on_response(dialog: Gtk.Dialog, _response: int) -> None:
            self.dialog.destroy()
            self.handler.on_book_cancelled()

        dialog.get_message_area().append(spinner := Gtk.Spinner())
        spinner.start()
        dialog.connect('response', on_response)
        dialog.show()
        self.dialog = dialog

    def update_progress(self, text: str) -> None:
        self.dialog.set_property('secondary-text', text)
        
    def destroy(self) -> None:
        self.dialog.destroy()

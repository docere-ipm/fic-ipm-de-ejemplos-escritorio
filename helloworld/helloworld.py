#!/usr/bin/env python3

from __future__ import annotations
from typing import Optional


# Vamos a internacionalizar la apliación añadiendo el soporte para
# texto en distintos idiomas usando `gettext`.

# Para el texto internacionalizado necesitamos la librería de soporte
# de locales y gettext.
import locale
import gettext
from pathlib import Path


import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


# Creamos un "alias" para las funciones de traducción con un nombre
# más corto.
# La convención es ' _' y 'N_'.
_ = gettext.gettext
N_ = gettext.ngettext


class State:
    count: int= 0

    def incr_count(self, step: int= 1) -> None:
        self.count += step

    def get_count(self) -> int:
        return self.count


def get_count_text(count: int) -> str:
    # Las f-strings no son internacionalizables
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
            # Por defecto todos los textos están en ingles
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
        self.state.incr_count()
        self._update_count()

    def _update_count(self) -> None:
        self.view.update_count_label(self.state.get_count())

        
if __name__ == '__main__':
    # Primero vamos a inicalizar el soporte de traducciones.

    # El primer paso es configurar el módulo `locale` con el locale de
    # la usuaria.
    # En windows esta configuración no se hace con las variables de entorno.
    locale.setlocale(locale.LC_ALL, '')

    # Establecemos las BBDD de traducciones. En gettext se llaman _dominios_.
    # Primero calculamos el directorio donde se encuentran.
    # En un FHS sería `/usr/share/locale`, ...
    LOCALE_DIR = Path(__file__).parent / "locale"
    # Relacionamos el nombre de las BBDD y el directorio donde buscar.
    # Las BBDD se llaman igual para todos los idiomas, sólo cambia el
    # directorio donde están.
    locale.bindtextdomain('HelloWorld', LOCALE_DIR)
    gettext.bindtextdomain('HelloWorld', LOCALE_DIR)
    # Configuramos el nombre de la BD de traducciones a usar
    gettext.textdomain('HelloWorld')
    
    presenter = Presenter()
    presenter.run()


    # Una vez internacionalizado el código, tenemos que hacer las
    # localizaciones.
    #
    # `xgettext -kN_:1,2 helloworld.py` extrae todas las cadenas de
    # texto del código que necesitan una traducción, incluyendo las
    # que tienen forma en plural.
    # Posiblemente tengamos que editar el fichero messages.po para
    # establecer el CHARSET.
    #
    # A continuación la persona encargada realiza las traducciones.
    # El fichero de traducciones para cada idioma se inicializa:
    # `$ msginit -i messages.po -l es`
    # o se actualiza con `msmerge`
    #
    # Una vez traducido, hay que crear la BD y copiarla al directorio
    # correspondiente. P.e.: {LOCALE_DIR}/es/LC_MESSAGES
    # El fichero con la BD tiene que tener el mismo nombre que usamos
    # en la configuración de gettext (nombre de dominio)
    # `msgfmt es.po -o locale/es/LC_MESSAGES/HelloWorld.mo`

    # En Unix la configuración del locale se establece en las
    # variables de entorno. Ver `locale -a`, y `locale`
    #
    # Para probar una localización es suficiente con cambiar esas variables.
    # P.e.: (según la shell y locale)
    # `LC_ALL=en_GB.utf8 ./helloworld.py`

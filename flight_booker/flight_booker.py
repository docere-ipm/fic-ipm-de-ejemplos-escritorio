#!/usr/bin/env python3

import locale
import gettext
from pathlib import Path

from models import FlightBookerModel
from views import FlightBookerView
from presenters import FlightBookerPresenter


# Los formularios enseguida tienden a proporcionar una mala
# experiencia de usuario:
#   - Son tediosos
#   - Es fácil equivocarse
#   - Partimos a priori de una "mala reputación"
#
# Es importante:
#   - Proporcionar toda la ayuda posible para cubrir los datos
#
#   - Gestionar los errores e informar de la manera más útil y lo
#     antes posible.

if __name__ == '__main__':
    
    locale.setlocale(locale.LC_ALL, '')
    LOCALE_DIR = Path(__file__).parent / "locale"
    locale.bindtextdomain('FlightBooker', LOCALE_DIR)
    gettext.bindtextdomain('FlightBooker', LOCALE_DIR)
    gettext.textdomain('FlightBooker')

    FlightBookerPresenter(
        model= FlightBookerModel(),
        view= FlightBookerView()
    ).run(application_id= "es.udc.fic.ipm.FlightBooker")

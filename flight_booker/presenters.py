from __future__ import annotations


import datetime
import threading
from typing import Optional


from models import FlightBookerModel
from views import FlightBookerView, UIText, run, run_on_main_thread


from date_utils import parse_date


class FlightBookerPresenter:
    def __init__(
            self,
            model: Optional[FlightBookerModel]= None,
            view: Optional[FlightBookerView]= None
    ) -> None:
        self.model = model or FlightBookerModel()
        self.view = view or FlightBookerView()
        self.data = self.model.build_data()

    def run(self, application_id: str) -> None:
        self.view.set_handler(self)
        run(application_id= application_id, on_activate= self.view.on_activate)

    def on_built(self, _view: FlightBookerView) -> None:
        self._update_view()
    
    def on_flight_type_changed(self, one_way: bool) -> None:
        self.data = self.data.update_one_way(one_way)
        self._update_view()
    
    def on_start_date_changed(self, text: str) -> None:
        text = text.strip()
        date = parse_date(text)
        self.data = self.data.update_start_date(date)
        self._update_view()
                
    def on_return_date_changed(self, text: str) -> None:
        text = text.strip()
        date = parse_date(text)
        self.data = self.data.update_return_date(date)
        self._update_view()
    
    def on_book_clicked(self) -> None:
        dialog = self.view.show_book_dialog()

        def do_book() -> None:
            generator = self.model.do_book(self.data)
            try:
                for step in generator:
                    if self.book_cancelled:
                        generator.close()
                        # Queda sin resolver cómo cancelamos el
                        # booking en el servidor
                        break
                    # TODO: Ejercicio: mostrar info de los steps
                else:
                    run_on_main_thread(do_book_continuation)
            except IOError as e:
                text = str(e)
                run_on_main_thread(do_book_continuation, text)

        def do_book_continuation(error: Optional[str]= None) -> None:
            self.view.destroy_dialog(dialog)
            if error is None:
                self.view.show_info(UIText.BOOK_SUCCESS.value)
            else:
                self.view.show_error(error)
            
        self.book_cancelled = False
        threading.Thread(target= do_book, daemon= True).start()

    def on_book_cancelled(self) -> None:
        self.book_cancelled = True
        
    def _update_view(self) -> None:
        # Este planteamiento tiene sus problemas.
        
        # Estamos marcando como erroneo la fecha de vuelta si es
        # anterior a la fecha de salida aunque el formato sea una
        # fecha válida
        
        if self.data.is_valid():
            book_enabled = True
            start_date_error = False
            return_date_error = self.data.return_date is None
        else:
            if self.data.start_date is not None:
                start_date_error = False
                return_date_error = True
            else:
                start_date_error = True
                return_date_error = self.data.return_date is not None
            book_enabled = False
        self.view.update(
            start_date_error= start_date_error,
            return_date_error= return_date_error,
            return_date_enabled= not self.data.one_way,
            book_enabled= book_enabled,
        )

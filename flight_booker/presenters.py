from __future__ import annotations


import datetime
import threading
from typing import Optional


from models import FlightBookerModel, FlightBookerProgress
from views import FlightBookerView, UIText, run, run_on_main_thread


from date_utils import date_sample, parse_date, show_date


class FlightBookerPresenter:
    def __init__(
            self,
            model: Optional[FlightBookerModel]= None,
            view: Optional[FlightBookerView]= None
    ) -> None:
        self.model = model or FlightBookerModel()
        self.view = view or FlightBookerView()
        self.data = self.model.build_data()
        self.start_date_text = ""
        self.return_date_text = ""

    def run(self, application_id: str) -> None:
        self.view.set_handler(self)
        run(application_id= application_id, on_activate= self.view.on_activate)

    def on_built(self, _view: FlightBookerView) -> None:
        self._update_view()
    
    def on_flight_type_changed(self, one_way: bool) -> None:
        self.data = self.data._replace(one_way= one_way)
        self._update_view()
    
    def on_start_date_changed(self, text: str) -> None:
        text = text.strip()
        self.start_date_text = text
        date = parse_date(text)
        self.data = self.data._replace(start_date= date)
        self._update_view()
                
    def on_return_date_changed(self, text: str) -> None:
        text = text.strip()
        self.return_date_text = text
        date = parse_date(text)
        self.data = self.data._replace(return_date= date)
        self._update_view()
    
    def on_book_clicked(self) -> None:
        dialog = self.view.progress_dialog(UIText.BOOKING.value)

        def do_book() -> None:
            generator = self.model.do_book(self.data)
            try:
                for step in generator:
                    if self.book_cancelled:
                        generator.close()
                        # Queda sin resolver cómo cancelamos el
                        # booking en el servidor
                        break
                    if step == FlightBookerProgress.CONTACTING_SERVER:
                        run_on_main_thread(
                            dialog.update_progress,
                            UIText.CONTACTING_SERVER.value
                        )
                    elif step ==  FlightBookerProgress.SENDING_DATA:
                        run_on_main_thread(
                            dialog.update_progress,
                            UIText.SENDING_DATA.value
                        )
                    elif step == FlightBookerProgress.WAITING_ANSWER:
                        run_on_main_thread(
                            dialog.update_progress,
                            UIText.WAITING_ANSWER.value
                        )
                    else:
                        run_on_main_thread(
                            dialog.update_progress,
                            str(step)
                        )
                else:
                    run_on_main_thread(do_book_continuation)
            except IOError as e:
                text = str(e)
                run_on_main_thread(do_book_continuation, text)

        def do_book_continuation(error: Optional[str]= None) -> None:
            dialog.destroy()
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
        
        if self.model.is_valid(self.data):
            book_enabled = True
            start_date_feedback = None
            return_date_feedback = None
        else:
            if self.start_date_text == "":
                start_date_feedback = ('error', UIText.MANDATORY_FIELD.value)
            elif self.data.start_date is None:
                start_date_feedback = (
                    'info',
                    UIText.WRONG_DATE_FORMAT.value.format(show_date(date_sample))
                )
            else:
                start_date_feedback = None
            if self.data.one_way:
                return_date_feedback = None
            else:
                if self.return_date_text == "":
                    return_date_feedback =  ('error', UIText.MANDATORY_FIELD.value)
                elif self.data.return_date is None:
                    return_date_feedback = (
                        'info',
                        UIText.WRONG_DATE_FORMAT.value.format(show_date(date_sample))
                    )
                else:
                    return_date_feedback = ('error', UIText.INVALID_DATE.value)
            book_enabled = False
        self.view.update(
            start_date_feedback= start_date_feedback,
            return_date_feedback= return_date_feedback,
            return_date_enabled= not self.data.one_way,
            book_enabled= book_enabled,
        )

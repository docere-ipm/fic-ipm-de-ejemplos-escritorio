from __future__ import annotations

import datetime
from enum import Enum, auto
import time
from typing import Iterator, NamedTuple, Optional
import random


class FlightBookerData(NamedTuple):
    one_way: bool = True
    start_date: Optional[datetime.datetime] = None
    return_date: Optional[datetime.datetime] = None

    
class FlightBookerProgress(Enum):
    CONTACTING_SERVER = auto()
    SENDING_DATA = auto()
    WAITING_ANSWER = auto()
    
    
class FlightBookerModel:
    n_progress_steps = 3

    def build_data(self) -> FlightBookerData:
        return FlightBookerData()

    def is_valid(self, data: FlightBookerData) -> bool:
        return (
            (
                data.one_way and
                data.start_date is not None
            ) or
            (
                not data.one_way and
                data.start_date is not None and
                data.return_date is not None and
                data.return_date >= data.start_date
            )
        )

    def do_book(self, booking_data: FlightBookerData) -> Iterator[FlightBookerProgress]:
        if not self.is_valid(booking_data):
            raise ValueError(f"Invalid {booking_data=}")
        yield FlightBookerProgress.CONTACTING_SERVER
        time.sleep(random.uniform(0, 1))
        yield FlightBookerProgress.SENDING_DATA
        time.sleep(random.uniform(0, 1))
        yield FlightBookerProgress.WAITING_ANSWER
        time.sleep(random.uniform(0, 2))
        ok = random.choice([True, False])
        if not ok:
            raise IOError("The server rejected the booking request")

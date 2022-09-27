import datetime
from typing import Optional


def parse_date(text: str) -> Optional[datetime.datetime]:
    try:
        # i18n: el formato de fecha es el que marca el locale
        date = datetime.datetime.strptime(text, "%x")
    except ValueError:
        date = None
    return date

    
def show_date(date: datetime.datetime) -> str:
    # i18n: el formato de fecha es el que marca el locale
    return date.strftime("%x")


date_sample = datetime.datetime.today()

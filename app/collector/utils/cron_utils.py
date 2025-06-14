from croniter import croniter
from datetime import datetime, timedelta, date


def check_if_cron_is_today(cron_expression: str):
    if cron_expression is None:
        return False

    today = datetime.strptime(date.today().strftime("%Y%m%d"), "%Y%m%d")
    base = today - timedelta(hours=1)
    iter = croniter(cron_expression, base)
    next_cron = iter.get_next(datetime)    
    return today == next_cron

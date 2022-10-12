"""
Usage: python wait-until.py desired-time

where `desired-time` is an `HH:MM` timestamp e.g. `23:45`.
"""

import datetime, logging, enum, sys, time

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class ExitCodes(enum.Enum):
    INVALID_USAGE = enum.auto()
    INVALID_TIMESTAMP = enum.auto()

def current_timestamp():
    """
    Gets datetime.now(), without the microseconds.
    """
    ts = datetime.datetime.now()
    # Chop off overly precise microseconds portion.
    ts -= datetime.timedelta(microseconds=ts.microsecond)
    return ts

def parse_timestamp(ts):
    try:
        now = datetime.datetime.now()
        hhmm = datetime.datetime.strptime(ts, '%H:%M')
        then = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=hhmm.hour, minute=hhmm.minute)
        if now >= then: then += datetime.timedelta(days=1)
        return then
    except ValueError:
        log.error(f"Invalid timestamp '{ts}'; expected HH:MM format.")
        sys.exit(ExitCodes.INVALID_TIMESTAMP.value)

def wait_until(then):
    while True:
        now = current_timestamp()
        if now >= then: break # It is time!
        delta = then - now
        log.info(f"Waiting {delta} until {then}...")
        time.sleep(delta.seconds)

if len(sys.argv) < 2:
    print("Usage: python wait-until.py desired-time")
    sys.exit(ExitCodes.INVALID_USAGE.value)

desired_time = parse_timestamp(sys.argv[1])
wait_until(desired_time)

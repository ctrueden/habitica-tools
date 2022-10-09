"""
A script to start a quest at a particular time.

Usage: python autoquest.py quest-id invite-time [force-start-after]

where:
* `quest-id` is the quest ID string.
* `invite-time` is an `HH:MM` timestamp e.g. `23:10`.
* `force-start-after` is a number of minutes before forcing it to start.

If you run `python autoquest.py` with no arguments,
the program lists the IDs of quests that you own.
"""

import datetime, enum, logging, sys, time

import habitica

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class ExitCodes(enum.Enum):
    INVALID_USAGE = enum.auto()
    INVALID_TIMESTAMP = enum.auto()
    INVALID_INTEGER = enum.auto()
    QUEST_NOT_OWNED = enum.auto()
    QUEST_ALREADY_ACTIVE = enum.auto()

def current_timestamp():
    """
    Gets datetime.now(), without the microseconds.
    """
    ts = datetime.datetime.now()
    # Chop off overly precise microseconds portion.
    ts -= datetime.timedelta(microseconds=ts.microsecond)
    return ts

def ensure_quest_in_inventory(session):
    items = session.profile('items')['items']
    quests = items['quests']

    if not quest_id in quests or quests[quest_id] <= 0:
        log.error(f"You do not have a {quest_id} quest!")
        sys.exit(ExitCodes.INVALID_USAGE.value)

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

# Parse arguments.

if len(sys.argv) < 3:
    log.info("Usage: python autoquest.py quest-id invite-time [force-start-after]")
    log.info("* quest-id is the quest to start")
    log.info("* invite-time is an HH:MM timestamp")
    log.info("* force-start-after is an integer number of minutes")
    log.info("")
    log.info("Available quests:")
    for quest_id, count in habitica.session().profile('items')['items']['quests'].items():
        if count > 0:
            log.info(f"* {count}x {quest_id}")
    sys.exit(ExitCodes.INVALID_USAGE.value)

quest_id = sys.argv[1]
invite_time = parse_timestamp(sys.argv[2])
if len(sys.argv) < 4:
    force_start_time = None
else:
    try:
        force_start_after = int(sys.argv[3])
        force_start_time = invite_time + datetime.timedelta(minutes=force_start_after)
    except ValueError:
        log.error(f"Invalid force-start-after value '{sys.argv[3]}'; expected integer")
        sys.exit(ExitCodes.INVALID_INTEGER.value)

# Verify that we own the quest scroll.
session = habitica.session()
ensure_quest_in_inventory(session)

# Wait until quest invite time.
wait_until(invite_time)

# Verify that we still own the quest scroll.
ensure_quest_in_inventory(session)

# Verify that we aren't already doing a quest.
party = session.party()
if party['quest']['active']:
    log.error(f"Quest already active: {party['quest']['key']}")
    sys.exit(ExitCodes.QUEST_ALREADY_ACTIVE.value)

# Invite party to the quest.
log.info(f"Inviting party to quest {quest_id}...")
result = session.invite_quest(quest_id)
log.info(result)

if force_start_time is not None:
    # Wait until quest force-start time.
    wait_until(force_start_time)

    # Force-start the quest, if it hasn't already started.
    party = session.party()
    if party['quest']['active']:
        active_quest_id = party['quest']['key']
        log.info(f"Quest {active_quest_id} is already active.")
        if quest_id != active_quest_id:
            log.error(f"This is not the quest you were looking for! O_O")
        else:
            log.info("All is well! ^_^")
    else:
        log.info(f"Quest still not started... force starting!")
        result = session.force_start_quest()
        log.info(result)

log.info("Quest shenanigans complete.")

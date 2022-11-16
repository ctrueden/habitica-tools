"""
A script to invite your party to a quest.

Usage: python quest-invite.py quest-id

where `quest-id` is the quest ID string.
"""

import enum, logging, sys

import habitica

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class ExitCodes(enum.Enum):
    INVALID_USAGE = enum.auto()
    QUEST_NOT_OWNED = enum.auto()
    QUEST_ALREADY_ACTIVE = enum.auto()
    INVITATION_ALREADY_PENDING = enum.auto()

# Parse arguments.

if len(sys.argv) < 2:
    print("Usage: python quest-invite.py quest-id")
    sys.exit(ExitCodes.INVALID_USAGE.value)

quest_id = sys.argv[1]

# Verify that we own the quest scroll.
session = habitica.session()
items = session.profile('items')['items']
quests = items['quests']
if not quest_id in quests or quests[quest_id] <= 0:
    log.error(f"You do not have a {quest_id} quest!")
    sys.exit(ExitCodes.QUEST_NOT_OWNED.value)

# Verify that we aren't already doing a quest.
party = session.party()
if party['quest']['active']:
    log.error(f"Quest already active: {party['quest']['key']}")
    sys.exit(ExitCodes.QUEST_ALREADY_ACTIVE.value)
if party['quest']['key']:
    log.error(f"Quest invitation already pending: {party['quest']['key']}")
    sys.exit(ExitCodes.INVITATION_ALREADY_PENDING.value)

# Invite party to the quest.
log.info(f"Inviting party to quest {quest_id}...")
result = session.invite_quest(quest_id)
log.info(result)

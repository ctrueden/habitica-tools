"""
A script for warriors to cast Brutal Smash repeatedly with optimal gear.

Usage: python autosmash.py [smash-count]

Where smash-count is a fixed number of smashes to perform.

When run with no arguments, the script smashes until pending damage exceeds
the current boss's HP, or the player runs out of mana, whichever comes first.
"""

import enum, logging, sys, time

import habitica

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class ExitCodes(enum.Enum):
    INVALID_INTEGER = enum.auto()
    NO_TASKS_TO_SMASH = enum.auto()
    NO_BOSS_QUEST_ACTIVE = enum.auto()
    INSUFFICIENT_MANA = enum.auto()

try:
    smash_count = None if len(sys.argv) < 2 else int(sys.argv[1])
except ValueError:
    log.error(f"Invalid smash-count value '{sys.argv[1]}'; expected integer")
    sys.exit(ExitCodes.INVALID_INTEGER.value)

session = habitica.session(log=log)

def smash(task, prefix="*"):
    """Smash the given task, logging the result."""
    time.sleep(2.8) # NB: Mitigate rate limit causing 401s.
    result = session.cast('smash', task['id'])
    session.log.info(f"{prefix} Smashed '{task['text']}' " +
        f"({round(task['value'], 1)} -> " +
        f"{round(result['task']['value'], 1)})")

# Get task IDs for smashing.
# Sort tasks by redness (value).
# We'll smash the reddest ones first.
tasks = sorted(session.tasks(), key=lambda t: t['value'])

if len(tasks) == 0:
    log.error("You have no tasks to use for smashing!")
    sys.exit(ExitCodes.NO_TASKS_TO_SMASH)

items = None
if smash_count is None:
    # Verify that a boss quest is active and discern its HP.
    log.info("Fetching quest info...")
    party = session.party()
    quest = party['quest']
    if (
        'active' not in quest or not quest['active'] or
        'progress' not in quest or not quest['progress'] or
        'hp' not in quest['progress'] or not quest['progress']['hp']
    ):
        log.error("No boss quest is active.")
        sys.exit(ExitCodes.NO_BOSS_QUEST_ACTIVE)
    boss_hp = quest['progress']['hp']
else:
    # Fetch profile. We need stats for the mana check,
    # but can also request items simultaneously.
    log.info("Fetching profile...")
    profile = session.profile('items,stats')
    items = profile['items']

    # Double check that we have enough mana.
    needed_mana = 10 * smash_count
    mana = profile['stats']['mp']
    if needed_mana > mana:
        log.error(f"You need {needed_mana} mana, but only have {mana}!")
        sys.exit(ExitCodes.INSUFFICIENT_MANA)
    log.info(f"Will use {needed_mana} of {mana} mana.")

if items is None:
    # Fetch items, for gear optimization.
    log.info("Fetching items...")
    items = session.profile('items')['items']

# Equip best STR gear.
log.info("Equipping best STR gear...")
str_gear = {
    'armor': 'armor_special_finnedOceanicArmor',
    'head': 'head_special_2',
    'shield': 'shield_special_lootBag',
    'weapon': 'weapon_warrior_6',
    'headAccessory': 'headAccessory_armoire_comicalArrow',
    'body': 'body_special_aetherAmulet',
#    'back': 'back_special_aetherCloak',
#    'eyewear': 'eyewear_special_aetherMask',
}
owned = items['gear']['owned']
equipped = items['gear']['equipped']
original_gear = {}
for slot, item in str_gear.items():
    if equipped[slot] != item:
        if item in owned and owned[item]:
            original_gear[slot] = equipped[slot]
            session.equip('equipped', item)
            log.info(f"* {slot}: {original_gear[slot]} -> {item}")
        else:
            log.warning(f'Cannot equip unowned item {item}')

# Autosmash!
log.info("Applying DPS...")
if smash_count is None:
    t = 0
    while True:
        # Update current status: pending damage and remaining mana.
        time.sleep(2) # NB: Mitigate rate limit causing 401s.
        profile = session.profile('party,stats')
        progress = profile['party']['quest']['progress']
        pending_damage = progress['up'] - progress['down']
        mana = profile['stats']['mp']
        log.info(f"* {round(pending_damage, 1)} damage queued " +
            "vs {round(boss_hp, 1)} HP -- {int(mana)} mana left")

        # Check for termination conditions.
        if pending_damage < boss_hp:
            log.info("Queued damage exceeds boss's remaining HP.")
            break
        if mana < 10:
            log.info("Insufficient mana to continue smashing.")
            break

        # There is still smashing to be done -- keep going!
        task = tasks[t % len(tasks)]
        t += 1
        smash(task, f"* [{t}]")
else:
    for t in range(smash_count):
        task = tasks[t % len(tasks)]
        smash(task, f"* [{t+1}/{smash_count}]")

# Restore original equipment.
log.info("Restoring original gear...")
for slot, item in original_gear.items():
    session.equip('equipped', item)
    log.info(f"* {slot}: re-equipped {item}")

log.info("Done! :-)")

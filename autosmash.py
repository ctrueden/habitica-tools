"""
A script to damage bosses repeatedly.
For warriors, it casts Brutal Smash repeatedly with optimal STR gear.
For mages, it casts Burst of Flames repeatedly, without altering gear.

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
    NO_SMASH_SKILL = enum.auto()

try:
    smash_count = None if len(sys.argv) < 2 else int(sys.argv[1])
except ValueError:
    log.error(f"Invalid smash-count value '{sys.argv[1]}'; expected integer")
    sys.exit(ExitCodes.INVALID_INTEGER.value)

session = habitica.session(log=log)

def smash(task, prefix="*"):
    """Smash the given task, logging the result."""
    time.sleep(2.8) # NB: Mitigate rate limit causing 401s.
    result = session.cast(skill, task['id'])
    session.log.info(f"{prefix} Smashed '{task['text']}' " +
        f"({round(task['value'], 1)} -> " +
        f"{round(result['task']['value'], 1)})")

# Get task IDs for smashing.
# Sort tasks by redness (value).
# We'll smash the reddest ones first.
tasks = sorted(session.tasks(), key=lambda t: t['value'])

if len(tasks) == 0:
    log.error("You have no tasks to use for smashing!")
    sys.exit(ExitCodes.NO_TASKS_TO_SMASH.value)

# Fetch profile. We need stats for the class, level, and mana checks.
# We fetch items opportunistically, for later gear optimization.
log.info("Fetching profile...")
profile = session.profile('items,stats')
stats = profile['stats']
items = profile['items']

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
        sys.exit(ExitCodes.NO_BOSS_QUEST_ACTIVE.value)
    boss_hp = quest['progress']['hp']
else:
    # Double check that we have enough mana.
    needed_mana = 10 * smash_count
    mana = stats['mp']
    if needed_mana > mana:
        log.error(f"You need {needed_mana} mana, but only have {mana}!")
        sys.exit(ExitCodes.INSUFFICIENT_MANA.value)
    log.info(f"Will use {needed_mana} of {mana} mana.")

skill = None
optimize_gear = False
if stats['class'] == 'wizard' and stats['lvl'] >= 11:
    skill = 'fireball' # Burst of Flames
elif stats['class'] == 'warrior' and stats['lvl'] >= 11:
    skill = 'smash' # Brutal Smash
    optimize_gear = True # Maximize STR while smashing.

if skill is None:
    log.error(f"You don't have a skill that can be used for smashing!")
    sys.exit(ExitCodes.NO_SMASH_SKILL.value)

owned = items['gear']['owned']
equipped = items['gear']['equipped']

def equip(gear):
    for slot, item in gear.items():
        if equipped[slot] != item:
            if item in owned and owned[item]:
                session.equip('equipped', item)
                log.info(f"* {slot}: {equipped[slot]} -> {item}")
                equipped[slot] = item
            else:
                log.warning(f'Cannot equip unowned item {item}')

if optimize_gear:
    # Equip best STR gear.
    log.info("Equipping best STR gear...")
    equip({
        'armor': 'armor_special_finnedOceanicArmor',
        'head': 'head_special_2',
        'shield': 'shield_special_lootBag',
        'weapon': 'weapon_warrior_6',
        'headAccessory': 'headAccessory_armoire_comicalArrow',
        'body': 'body_special_aetherAmulet',
        #'back': 'back_special_aetherCloak',
        #'eyewear': 'eyewear_special_aetherMask',
    })

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
            f"vs {round(boss_hp, 1)} HP -- {int(mana)} mana left")

        # Check for termination conditions.
        if pending_damage >= boss_hp:
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

if optimize_gear:
    # Restore original equipment.
    log.info("Equipping best INT gear...")
    equip({
        'armor': 'armor_special_2',
        'head': 'head_special_2',
        'shield': 'shield_special_diamondStave',
        'weapon': 'weapon_special_nomadsScimitar',
        #'headAccessory': 'headAccessory_armoire_comicalArrow',
        'body': 'body_armoire_lifeguardWhistle',
        'back': 'back_special_aetherCloak',
        'eyewear': 'eyewear_armoire_tragedyMask',
    })

log.info("Done! :-)")

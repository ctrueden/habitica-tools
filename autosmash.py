"""
A script for warriors to cast Brutal Smash repeatedly with optimal gear.

Usage: python autosmash.py 38

Where "38" is the number of smashes to perform.
"""

import logging
import sys

import habitica

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

if len(sys.argv) < 2:
    log.info("Usage: python autosmash.py smash-count")
    sys.exit(1)

smash_count = int(sys.argv[1])

session = habitica.session(log=log)

# Verify that a boss quest is active.
#party = session.party()
#quest = party['quest']
#assert quest['active'] is True
#assert quest['key'] == 'lostMasterclasser2'
#assert party['memberCount'] == quest['members'])
#hp = quest['progress']['hp']
# Unfortunately, pending damage is not part of this info, only current boss HP.

# Get task IDs for smashing.
# Sort tasks by redness (value).
# We'll smash the reddest ones first.
tasks = sorted(session.tasks(), key=lambda t: t['value'])

if len(tasks) == 0:
    log.error("You have no tasks to use for smashing!")
    sys.exit(2)

# Get needed bits of the profile.
log.info("Fetching profile...")
profile = session.profile('items,stats')

# Double check that we have enough mana.
needed_mana = 10 * smash_count
mana = profile['stats']['mp']
if needed_mana > mana:
    log.error("You need {needed_mana} mana, but only have {mana}!")
    sys.exit(3)
log.info("Will use {needed_mana} of {mana} mana.")

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
owned = profile['items']['gear']['owned']
equipped = profile['items']['gear']['equipped']
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
for t in range(smash_count):
    task = tasks[t % len(tasks)]
    result = session.cast('smash', task['id'])
    log.info(f"* Smashed '{task['text']}' " +
        f"({round(task['value'], 1)} -> " +
        f"{round(result['task']['value'], 1)}")

# Restore original equipment.
log.info("Restoring original gear...")
for slot, item in original_gear.items():
    session.equip('equipped', item)
    log.info(f"* {slot}: re-equipped {item}")

log.info("Done! :-)")

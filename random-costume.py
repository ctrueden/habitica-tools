"""
A script to randomize your costume.

Usage: python random-costume.py
"""

import logging
from random import choice, random

import habitica

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

session = habitica.session(log=log)

# Fetch profile.
log.info("Fetching profile...")
profile = session.profile('items')
items = profile['items']

owned = items['gear']['owned']
costume = items['gear']['costume']

gear = {
    'armor': None,
    'head': None,
    'shield': None,
    'weapon': None,
    'headAccessory': None,
    'body': None,
    'back': None,
    'eyewear': None,
}
log.info("Randomizing...")

pet_chance = 0.5
pet_choices = [p for p in items['pets'] if items['pets'][p] >= 0]
pet = choice(pet_choices) if len(pet_choices) > 0 and random() < pet_chance else items['currentPet']

mount_chance = 0.3
mount_choices = [m for m in items['mounts'] if items['mounts'][m] is True]
mount = choice(mount_choices) if len(mount_choices) > 0 and random() < mount_chance else items['currentMount']

for slot in gear:
    gear_choices = [g for g in owned if owned[g] and g.startswith(f'{slot}_')]
    if len(gear_choices) == 0: continue
    gear[slot] = choice(gear_choices)

# TODO: randomize background also.
# POST https://habitica.com/api/v4/user/unlock?path=background.frozen_blue_pond

log.info("Equipping...")
if pet:
    session.equip('pet', pet)
    log.info(f"* pet: {items['currentPet']} -> {pet}")
if mount:
    session.equip('mount', mount)
    log.info(f"* mount: {items['currentMount']} -> {mount}")
for slot, item in gear.items():
    if costume[slot] == item: continue
    session.equip('costume', item)
    log.info(f"* {slot}: {costume[slot]} -> {item}")

log.info("Done! :-)")

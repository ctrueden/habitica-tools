"""
A script for feeding all your pets.

Usage: python autofeed.py
"""

import logging
import math
import sys
import time

import habitica

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

food_mapping = {
    "Meat": "Base",
    "Milk": "White",
    "Potatoe": "Desert",
    "Strawberry": "Red",
    "Chocolate": "Shade",
    "Fish": "Skeleton",
    "RottenMeat": "Zombie",
    "CottonCandyPink": "CottonCandyPink",
    "CottonCandyBlue": "CottonCandyBlue",
    "Honey": "Golden",
}

base_pets = {
    'Wolf',
    'TigerCub',
    'PandaCub',
    'LionCub',
    'Fox',
    'FlyingPig',
    'Dragon',
    'Cactus',
    'BearCub',
}
# These wacky pets do not need feeding.
wacky_pets = \
    {f"{p}-Veggie" for p in base_pets} | \
    {f"{p}-Dessert" for p in base_pets} | \
    {f"{p}-VirtualPet" for p in base_pets} | \
    {f"{p}-TeaShop" for p in base_pets} | \
    {f"{p}-Fungi" for p in base_pets} | \
    {f"{p}-Cryptid" for p in base_pets}

# These special pets must never be fed.
special_pets = {
    'Wolf-Veteran',
    'Hydra-Base', # Guess
    'Turkey-Base',
    'BearCub-Polar',
    'MantisShrimp-Base',
    'JackOLantern-Base',
    'Mammoth-Base',
    'Tiger-Veteran',
    'Phoenix-Base',
    'Turkey-Gilded',
    'MagicalBee-Base',
    'Gryphon-RoyalPurple',
    'JackOLantern-Ghost',
    'Jackalope-RoyalPurple',
    'Orca-Base',
    'Hippogriff-Hopeful',
    'JackOLantern-Glow',
    'Gryphatrice-Jubilant',
}
do_not_feed = wacky_pets | special_pets

# These types of pets want only a certain kind of food.
# Whereas quest pets (e.g. "Sunshine") love all foods.
picky_pet_types = food_mapping.values()

def optimal_pet_type_for_food(food):
    if food in food_mapping:
        # E.g.: Fish -> Skeleton
        return food_mapping[food]
    if '_' in food:
        # E.g.: Cake_Base -> Base
        return food[food.rindex('_')+1:]
    return None

def autofeed(session, profile):
    foods = profile['items']['food']
    pets = profile['items']['pets']
    mounts = profile['items']['mounts']

    def should_feed(pet, needed_pet_type=None):
        score = pets[pet]
        if pet in do_not_feed:
            log.debug(f"Skipping wacky/special pet: {pet}")
            return False
        if score < 0:
            log.debug(f"We do not have {pet}")
            return False
        if score >= 50:
            log.debug(f"{pet} is already full")
            return False
        if pet in mounts and mounts[pet] is True:
            log.debug(f"We already have {pet} as a mount")
            return False
        dash = pet.find("-")
        if dash < 0:
            log.warning(f"Skipping weird pet: {pet}")
            return False
        pet_type = pet[dash+1:]
        if needed_pet_type is not None and pet_type != needed_pet_type:
            # This pet is not the type we are looking for.
            log.debug(f"Pet {pet} is not a {needed_pet_type}")
            return False
        return True

    def feed_pet(pet, food):
        score = pets[pet]
        hunger = 50 - score
        ideal_amount = math.ceil(hunger / 5)
        amount = min(foods[food], ideal_amount)
        log.info(f"Feeding {food} x{amount} to {pet}...")
        time.sleep(2.1) # NB: Mitigate rate limit causing 401s.
        session.feed(pet, food, amount)
        pets[pet] += 5 * amount
        foods[food] -= amount

    # Feed picky pets first.
    for food, count in foods.items():
        if count == 0: continue

        # Discern needed pet type for this food.
        needed_pet_type = optimal_pet_type_for_food(food)
        if needed_pet_type is None:
            if food != 'Saddle':
                log.warning(f'Skipping unknown food: {food}')
            continue

        # Now look for hungry pets of this type.
        for pet in pets:
            if should_feed(pet, needed_pet_type):
                # Found a matching pet! Now let's feed it.
                feed_pet(pet, food)
                if foods[food] == 0: break

    # Now feed any other hungry (but not picky) pets.
    for pet in pets:
        while should_feed(pet):
            # Find the most plentiful food.
            amount, best_food = max((foods[food], food) for food in foods)
            if amount == 0: return # We ran out of food!
            feed_pet(pet, best_food)

def main():
    session = habitica.session(log=log)
    log.info("Fetching profile...")
    profile = session.profile('items')
    autofeed(session, profile)
    log.info("Done! :-)")

if __name__ == "__main__":
    main()

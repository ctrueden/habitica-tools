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

# These wacky pets must never be fed.
garden_pets = {
    'Wolf-Veggie',
    'TigerCub-Veggie',
    'PandaCub-Veggie',
    'LionCub-Veggie',
    'Fox-Veggie',
    'FlyingPig-Veggie',
    'Dragon-Veggie',
    'Cactus-Veggie',
    'BearCub-Veggie',
}
confection_pets = {
    'Wolf-Dessert',
    'TigerCub-Dessert',
    'PandaCub-Dessert',
    'LionCub-Dessert',
    'Fox-Dessert',
    'FlyingPig-Dessert',
    'Dragon-Dessert',
    'Cactus-Dessert',
    'BearCub-Dessert',
}
virtual_pets = {
    'Wolf-VirtualPet',
    'TigerCub-VirtualPet',
    'PandaCub-VirtualPet',
    'LionCub-VirtualPet',
    'Fox-VirtualPet',
    'FlyingPig-VirtualPet',
    'Dragon-VirtualPet',
    'Cactus-VirtualPet',
    'BearCub-VirtualPet',
}
wacky_pets = garden_pets | confection_pets | virtual_pets

# These special pets must never be fed.
special_pets = {
    'Hydra-Base', # Guess
    'Turkey-Base',
    'BearCub-Polar',
    'MantisShrimp-Base', # Guess
    'JackOLantern-Base',
    'Mammoth-Base',
    'Phoenix-Base',
    'MagicalBee-Base',
    'Jackalope-RoyalPurple',
    'Hippogriff-Hopeful',
}

do_not_feed = wacky_pets | special_pets

# These types of pets want only a certain kind of food.
# Whereas quest pets (e.g. "Sunshine") love all foods.
picky_pet_types = {
    "Base", "White", "Desert", "Red", "Shade", "Skeleton",
    "Zombie", "CottonCandyPink", "CottonCandyBlue", "Golden"
}

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

    for food, count in foods.items():
        if count == 0: continue
        needed_pet_type = optimal_pet_type_for_food(food)
        if needed_pet_type is None:
            if food != 'Saddle':
                log.warning(f'Skipping unknown food: {food}')
            continue

        # Now look for hungry pets of this type!
        for pet, score in pets.items():
            if pet in do_not_feed:
                log.debug(f"Skipping wacky/special pet: {pet}")
                continue
            if score < 0:
                log.debug(f"We do not have {pet}")
                continue
            if score >= 50:
                log.debug(f"{pet} is already full")
                continue
            if pet in mounts and mounts[pet] is True:
                log.debug(f"We already have {pet} as a mount")
                continue
            dash = pet.find("-")
            if dash < 0:
                log.warning(f"Skipping weird pet: {pet}")
                continue
            pet_type = pet[dash+1:]
            if pet_type != needed_pet_type:
                # This pet is not the type we are looking for.
                log.debug(f"Pet {pet} is not a {needed_pet_type}")
                continue

            # Found a matching pet! Now let's feed it.
            hunger = 50 - score
            ideal_amount = math.ceil(hunger / 5)
            amount = min(count, ideal_amount)
            log.info(f"Feeding {food} x{amount} to {pet}...")
            time.sleep(2.1) # NB: Mitigate rate limit causing 401s.
            session.feed(pet, food, amount)
            pets[pet] += 5 * amount
            count -= amount
            if count == 0: break

def main():
    session = habitica.session(log=log)
    log.info("Fetching profile...")
    profile = session.profile('items')
    autofeed(session, profile)
    log.info("Done! :-)")

if __name__ == "__main__":
    main()

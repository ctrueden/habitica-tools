"""
A script for summarizing your pets and mounts, along
with which eggs and magic potions you have and need.

Usage: python pet-report.py
"""

import logging
import math
import sys
import time

from collections import defaultdict

import habitica

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

session = habitica.session(log=log)

log.info("Fetching profile...")
profile = session.profile('items')

pets = profile['items']['pets']
mounts = profile['items']['mounts']
eggs = profile['items']['eggs']
quests = profile['items']['quests']
potions = profile['items']['hatchingPotions']

# -- Pets --

pet_species = {
    'Alligator': 'alligator',
    'Alpaca': 'alpaca',
    'Armadillo': 'armadillo',
    'Axolotl': 'axolotl',
    'Badger': 'badger',
    'BearCub': None,
    'Beetle': 'beetle',
    'Bunny': 'bunny',
    'Butterfly': 'butterfly',
    'Cactus': None,
    'Cat': 'cat',
    'Chameleon': 'chameleon',
    'Cheetah': 'cheetah',
    'Cow': 'cow',
    'Cuttlefish': 'kraken',
    'Deer': 'ghost_stag',
    'Dog': 'dog',
    'Dolphin': 'dolphin',
    'Dragon': None,
    'Egg': 'egg',
    'Falcon': 'falcon',
    'Ferret': 'ferret',
    'FlyingPig': None,
    'Fox': None,
    'Frog': 'frog',
    'Giraffe': 'giraffe',
    'Gryphon': 'gryphon',
    'GuineaPig': 'guineapig',
    'Hedgehog': 'hedgehog',
    'Hippo': 'hippo',
    'Horse': 'horse',
    'Kangaroo': 'kangaroo',
    'LionCub': None,
    'Monkey': 'monkey',
    'Nudibranch': 'nudibranch',
    'Octopus': 'octopus',
    'Otter': 'otter',
    'Owl': 'owl',
    'PandaCub': None,
    'Parrot': 'harpy',
    'Peacock': 'peacock',
    'Penguin': 'penguin',
    #'PolarBear': 'N/A',
    'Platypus': 'platypus',
    'Pterodactyl': 'pterodactyl',
    'Raccoon': 'raccoon',
    'Rat': 'rat',
    'Robot': 'robot',
    'Rock': 'rock',
    'Rooster': 'rooster',
    'Sabretooth': 'sabretooth',
    'SeaSerpent': 'seaserpent',
    'Seahorse': 'dilatory_derby',
    'Sheep': 'sheep',
    'Slime': 'slime',
    'Sloth': 'sloth',
    'Snail': 'snail',
    'Snake': 'snake',
    'Spider': 'spider',
    'Squirrel': 'squirrel',
    'TRex': 'trex_undead', # also 'trex'
    'TigerCub': None,
    'Treeling': 'treeling',
    'Triceratops': 'triceratops',
    'Turtle': 'turtle',
    'Unicorn': 'unicorn',
    'Velociraptor': 'velociraptor',
    'Whale': 'whale',
    'Wolf': None,
    'Yarn': 'yarn',
}

pet_kinds_standard = {
    'Base', 'CottonCandyBlue', 'CottonCandyPink', 'Desert',
    'Golden', 'Red', 'Shade', 'Skeleton', 'White', 'Zombie'
}

pet_kinds_potion = {
    'Amber': 'amber',
    'Aquatic': 'aquatic',
    'Aurora': 'aurora',
    'AutumnLeaf': 'autumnLeaf',
    'BirchBark': 'birchBark',
    'BlackPearl': 'blackPearl',
    'Bronze': 'bronze',
    'Celestial': 'celestial',
    'Cupid': 'cupid',
    'Dessert': 'dessert',
    'Ember': 'ember',
    'Fairy': 'fairy',
    'Floral': 'floral',
    'Fluorite': 'fluorite',
    'Frost': 'frost',
    'Ghost': 'ghost',
    'Gingerbread': 'gingerbread',
    'Glass': 'glass',
    'Glow': 'glow',
    'Holly': 'holly',
    'IcySnow': 'icySnow',
    'Koi': 'koi',
    'Moonglow': 'moonglow',
    'MossyStone': 'stone',
    'Onyx': 'onyx',
    'Peppermint': 'peppermint',
    'PinkMarble': 'pinkMarble',
    'Polar': 'polar',
    'PolkaDot': 'polkaDot',
    'Porcelain': 'porcelain',
    'Rainbow': 'rainbow',
    'RoseQuartz': 'roseQuartz',
    'RoseGold': 'roseGold',
    'RoyalPurple': 'royalPurple',
    'Ruby': 'ruby',
    'SandSculpture': 'sandSculpture',
    'Shadow': 'shadow',
    'Shimmer': 'shimmer',
    'Silver': 'silver',
    'SolarSystem': 'solarSystem',
    'Spooky': 'spooky',
    'StainedGlass': 'stainedGlass',
    'StarryNight': 'starryNight',
    'Sunset': 'sunset',
    'Sunshine': 'sunshine',
    'Thunderstorm': 'thunderstorm',
    'Turquoise': 'turquoise',
    'Vampire': 'vampire',
    'Watery': 'watery',
    'Windup': 'windup',
}

pet_kinds_wacky = {
    'Cryptid': 'cryptid',
    'Dessert': 'waffle',
    'Fungi': 'fungi',
    'TeaShop': 'teaShop',
    'Veggie': 'veggie',
    'VirtualPet': 'virtualPet',
}

unique_pets = {
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

pet_kinds = pet_kinds_standard | pet_kinds_potion.keys() | pet_kinds_wacky.keys()

symbols = {
    # == Species ==
    'Alligator': '🐊',
    'Alpaca': '🦙',
    'Armadillo': '🐾',
    'Axolotl': '🦎', # 𓆈
    'Badger': '🦡',
    'BearCub': '🐻',
    'Beetle': '🪲',
    'Bunny': '🐇', # 🐰
    'Butterfly': '🦋',
    'Cactus': '🌵',
    'Cat': '🐈',
    'Chameleon': '𓆈', # 🦎
    'Cheetah': '🐆',
    'Cow': '🐄', # 🐮
    'Cuttlefish': '🐡', # 🐟🐠
    'Deer': '🦌',
    'Dog': '🐕',
    'Dolphin': '🐬',
    'Dragon': '🐉', # 🐲
    'Egg': '🥚',
    'Falcon': '🦅',
    'Ferret': '🐾',
    'FlyingPig': '🐖', # 🐷
    'Fox': '🦊',
    'Frog': '🐸',
    'Giraffe': '🦒',
    'Gryphon': '🦅', # 🦁
    'GuineaPig': '🐹',
    'Hedgehog': '🦔',
    'Hippo': '🦛',
    'Horse': '🐎', # 🐴
    'Kangaroo': '🦘',
    'LionCub': '🦁',
    'Monkey': '🐒', # 🐵
    'Nudibranch': '🐟', # 🐠🐡
    'Octopus': '🐙',
    'Otter': '🦦',
    'Owl': '🦉',
    'Parrot': '🦜',
    'Peacock': '🦚',
    'Penguin': '🐧',
    #'PolarBear': '🐻‍❄️',
    'Platypus': '🦫', # 🦆
    'Pterodactyl': '🐦', # 🦕
    'Raccoon': '🦝',
    'Rat': '🐀',
    'Robot': '🤖',
    'Rock': '🗿', # 🪨
    'Rooster': '🐓', # 🐔
    'Sabretooth': '🐅', # 🐯
    'SeaSerpent': '🐍',
    'Seahorse': '🐴',
    'Sheep': '🐑',
    'Slime': '💩' , # 🦠🫠
    'Sloth': '🦥',
    'Snail': '🐌',
    'Snake': '🐍',
    'Spider': '🕷',
    'Squirrel': '🐿',
    'TRex': '🦖',
    'TigerCub': '🐯', # 🐅
    'Treeling': '🌴', # 🌳🌲🎋
    'Triceratops': '🦕',
    'Turtle': '🐢',
    'Unicorn': '🦄',
    'Velociraptor': '🦖',
    'Whale': '🐋', # 🐳
    'Wolf': '🐺',
    'Yarn': '🧶',
    'Squid': '🦑', # NOT ACTUALLY ONE OF THEM

    # == Magic potions ==
    'Amber': '🔶',
    'Aquatic': '🌊',
    'Aurora': '🌆', # 🎇🎆
    'AutumnLeaf': '🍂',
    'BirchBark': '🌳', # 🎋
    'BlackPearl': '⚫',
    'Bronze': '🔱', # 🥉
    'Celestial': '🌠', # ☄️
    'Cupid': '💕',
    'Dessert': '🍪', # 🍩
    'Ember': '🔥',
    'Fairy': '🧚',
    'Floral': '🌷', # ⚘💐🌻🌹🌸🌺
    'Fluorite': '💎',
    'Frost': '☃️', # 🥶
    'Ghost': '👻',
    'Gingerbread': '🍪',
    'Glass': '🪟',
    'Glow': '🌟',
    'Holly': '🍒',
    'IcySnow': '❄️', # 🧊
    'Koi': '🐠',
    'Moonglow': '🎑', # 🌕
    'MossyStone': '🪨',
    'Onyx': '🖤',
    'Peppermint': '🍬',
    'PinkMarble': '🔮',
    'Polar': '🏔️',
    'PolkaDot': '👙',
    'Porcelain': '🚽',
    'Rainbow': '🌈',
    'RoseQuartz': '💎',
    'RoseGold': '💗',
    'RoyalPurple': '🟣',
    'Ruby': '🔴',
    'SandSculpture': '🏰', # 🏖️
    'Shadow': '🌑',
    'Shimmer': '✨', # 💖
    'Silver': '🪞', # 🥈
    'SolarSystem': '🪐', # 🌌
    'Spooky': '👻',
    'StainedGlass': '🖼️',
    'StarryNight': '🌃',
    'Sunset': '🌇',
    'Sunshine': '☀️',
    'Thunderstorm': '🌩️',
    'Turquoise': '💎',
    'Vampire': '🧛',
    'Watery': '🌊',
    'Windup': '🦾',
}

# -- Platform-specific spacing hacks --

# Most emoji are 2 characters wide in most fixed-width font scenarios.
# But a few are only 1 character wide in some cases (fonts? terminals? OSes?).
# This represents a lazy effort to pad out the ones that don't align otherwise.

padded_symbols = [
    'Chameleon', 'Spider', 'Squirrel'
]

from sys import platform
if platform != 'darwin':
    padded_symbols.extend((
        'Frost', 'IcySnow', 'Polar', 'StainedGlass', 'Sunshine', 'Thunderstorm'
    ))

for name in padded_symbols:
    symbols[name] += ' '

# -- Quest scrolls --

quest_scrolls_pet = set(pet_species.values()) - {None} | {'trex'}

quest_scrolls_potion = set(pet_kinds_potion.values()) - {None}

quest_scrolls_wacky = set(pet_kinds_wacky.values()) - {None}

quest_scrolls_other = {
    'atom1', # unlockable
    'atom2', # unlockable
    'atom3', # unlockable
    'basilist', # earnable
    'dilatory', # ???
    'dilatoryDistress1', # masterclasser
    'dilatoryDistress2', # masterclasser
    'dilatoryDistress3', # masterclasser
    'dustbunnies', # earnable
    'evilsanta', # ???
    'evilsanta2', # ???
    'goldenknight1', # unlockable
    'goldenknight2', # unlockable
    'goldenknight3', # unlockable
    'lostMasterclasser1', # masterclasser
    'lostMasterclasser2', # masterclasser
    'lostMasterclasser3', # masterclasser
    'lostMasterclasser4', # masterclasser
    'mayhemMistiflying1', # masterclasser
    'mayhemMistiflying2', # masterclasser
    'mayhemMistiflying3', # masterclasser
    'moon1', # unlockable: Lunar Battle
    'moon2', # unlockable: Lunar Battle
    'moon3', # unlockable: Lunar Battle
    'moonstone1', # unlockable: Recidivate Rising
    'moonstone2', # unlockable: Recidivate Rising
    'moonstone3', # unlockable: Recidivate Rising
    'stoikalmCalamity1', # masterclasser
    'stoikalmCalamity2', # masterclasser
    'stoikalmCalamity3', # masterclasser
    'taskwoodsTerror1', # masterclasser
    'taskwoodsTerror2', # masterclasser
    'taskwoodsTerror3', # masterclasser
    'vice1', # unlockable
    'vice2', # unlockable
    'vice3', # unlockable
    'atom1_soapBars', # old name?
    'dilatoryDistress1_blueFins', # old name?
    'dilatoryDistress1_fireCoral', # old name?
    'egg_plainEgg', # old name?
    'evilsanta2_branches', # old name?
    'evilsanta2_tracks', # old name?
    'goldenknight1_testimony', # old name?
    'lostMasterclasser1_ancientTome', # old name?
    'lostMasterclasser1_forbiddenTome', # old name?
    'lostMasterclasser1_hiddenTome', # old name?
    'mayhemMistiflying2_mistifly1', # old name?
    'mayhemMistiflying2_mistifly2', # old name?
    'mayhemMistiflying2_mistifly3', # old name?
    'moon1_shard', # old name?
    'moonstone1_moonstone', # old name?
    'onyx_leoRune', # old name?
    'onyx_onyxStone', # old name?
    'onyx_plutoRune', # old name?
    'robot_bolt', # old name?
    'robot_gear', # old name?
    'robot_spring', # old name?
    'ruby_aquariusRune', # old name?
    'ruby_rubyGem', # old name?
    'ruby_venusRune', # old name?
    'silver_cancerRune', # old name?
    'silver_moonRune', # old name?
    'silver_silverIngot', # old name?
    'stoikalmCalamity2_icicleCoin', # old name?
    'stone_capricornRune', # old name?
    'stone_marsRune', # old name?
    'stone_mossyStone', # old name?
    'taskwoodsTerror2_brownie', # old name?
    'taskwoodsTerror2_dryad', # old name?
    'taskwoodsTerror2_pixie', # old name?
    'turquoise_neptuneRune', # old name?
    'turquoise_sagittariusRune', # old name?
    'turquoise_turquoiseGem', # old name?
    'vice2_lightCrystal', # old name?
}

quest_scrolls = \
    quest_scrolls_pet | \
    quest_scrolls_potion | \
    quest_scrolls_wacky | \
    quest_scrolls_other

quest_scroll_bundles = {
    'aquaticAmigos': ['axolotl', 'kraken', 'octopus'],
    'birdBuddies': [], # TODO
    'cuddleBuddies': [], # TODO
    'delightfulDinos': ['triceratops', 'trex', 'pterodactyl'],
    'farmFriends': ['horse', 'sheep', 'cow'],
    'featheredFriends': [], # TODO
    'forestFriends': [], # TODO
    'hugabug': [], # TODO
    'jungleBuddies': ['monkey', 'treeling', 'sloth'],
    'mythicalMarvels': [], # TODO
    'oddballs': [], # TODO
    'rockingReptiles': [], # TODO
    'sandySidekicks': ['spider', 'snake', 'armadillo'],
    'splashyPals': ['turtle', 'whale', 'dilatory_derby'],
    'winterQuests': [], # TODO
    'witchyFamiliars': ['rat', 'spider', 'frog'],
}

colors = defaultdict(lambda: '') if any(arg == '--no-colors' for arg in sys.argv) else {
    'reset': '[0m',
    'black': '[0;30m',
    'red': '[0;31m',
    'green': '[0;32m',
    'yellow': '[0;33m',
    'blue': '[0;34m',
    'purple': '[0;35m',
    'cyan': '[0;36m',
    'white': '[0;37m',
}

print()
print("### Pet quest pets ###")
print()
print(f"|    | SPECIES      |  PETS | MOUNTS | EGGS | QUESTS | SHORTAGE |")
print(f"|----|:-------------|------:|-------:|-----:|-------:|---------:|")
standard_kinds_count = len(pet_kinds_standard)
for species, quest_scroll in sorted(pet_species.items()):
    if quest_scroll is None:
        # Standard pet, not pet quest pet.
        continue

    my_pets = {f"{p}:{hunger}" for p, hunger in pets.items() if p.startswith(f"{species}-") and hunger > 0}
    my_mounts = {f"{m}" for m, v in mounts.items() if m.startswith(f"{species}-") and v is True}
    egg_count = eggs[species] if species in eggs else 0
    quest_count = quests[quest_scroll] if quest_scroll in quests else 0
    shortage = 2 * standard_kinds_count - len(my_pets) - len(my_mounts) - egg_count - 3 * quest_count

    if shortage <= 0:
        color = 'blue'
        shortage = 'none'
    elif shortage < 10: color = 'green'
    elif shortage < 20: color = 'yellow'
    else: color = 'red'

    print(f"{colors[color]}" +
        f"| {symbols[species]} " +
        f"| {species:12} " +
        f"| {len(my_pets):>2}/{standard_kinds_count} " +
        f"|  {len(my_mounts):>2}/{standard_kinds_count} " +
        f"| {egg_count:>4} " +
        f"| {quest_count:>6} " +
        f"| {shortage:>8} " +
        f"|{colors['reset']}")

print()
print("### Magic hatching potion pets ###")
print()
print(f"|    | MAGIC POTION  | PETS | MOUNTS | POTIONS | QUESTS | SHORTAGE |")
print(f"|----|:--------------|-----:|-------:|--------:|-------:|---------:|")
standard_pets_count = len([species for species, quest_scroll in pet_species.items() if quest_scroll is None])
for kind, quest_scroll in sorted(pet_kinds_potion.items()):
    my_pets = {f"{p}:{hunger}" for p, hunger in pets.items() if p.endswith(f"-{kind}") and hunger > 0}
    my_mounts = {f"{m}" for m, v in mounts.items() if m.endswith(f"-{kind}") and v is True}
    potion_count = potions[kind] if kind in potions else 0
    quest_count = quests[quest_scroll] if quest_scroll in quests else 0
    shortage = 2 * standard_pets_count - len(my_pets) - len(my_mounts) - potion_count - 3 * quest_count

    if shortage <= 0:
        color = 'blue'
        shortage = 'none'
    elif shortage < 9: color = 'green'
    elif shortage < 18: color = 'yellow'
    else: color = 'red'

    print(f"{colors[color]}" +
        f"| {symbols[kind]} " +
        f"| {kind:13} " +
        f"| {len(my_pets):>2}/{standard_pets_count} " +
        f"|   {len(my_mounts):>2}/{standard_pets_count} " +
        f"| {potion_count:>7} " +
        f"| {quest_count:>6} " +
        f"| {shortage:>8} " +
        f"|{colors['reset']}")

for p in pets:
    if p not in unique_pets and p[p.rindex("-")+1:] not in pet_kinds:
        print(f"{colors['red']}[WARNING] Unknown pet type! {p}{colors['reset']}")

for qs in quests:
    if qs not in quest_scrolls:
        print(f"{colors['red']}[WARNING] Unknown quest scroll! {qs}{colors['reset']}")

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
    'Armadillo': 'armadillo',
    'Axolotl': 'axolotl',
    'Badger': 'badger',
    'BearCub': None,
    'Beetle': 'beetle',
    'Bunny': 'bunny',
    'Butterfly': 'butterfly',
    'Cactus': None,
    'Chameleon': 'chameleon',
    'Cheetah': 'cheetah',
    'Cow': 'cow',
    'Cuttlefish': 'kraken',
    'Deer': 'ghost_stag',
    'Dolphin': 'dolphin',
    'Dragon': None,
    'Egg': 'egg',
    'Falcon': 'falcon',
    'Ferret': 'ferret',
    'FlyingPig': None,
    'Fox': None,
    'Frog': 'frog',
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
    'Owl': 'owl',
    'PandaCub': None,
    'Parrot': 'harpy',
    'Peacock': 'peacock',
    'Penguin': 'penguin',
    #'PolarBear': 'N/A',
    'Pterodactyl': 'pterodactyl',
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
    'TRex': 'trex_undead', # also 'trex'?
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

pet_kinds_magic_potion = {
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

pet_kinds_special = { 'Fungi', 'Veggie', 'VirtualPet', 'TeaShop' }

unique_pets = {
    'Gryphatrice-Jubilant',
    'Hippogriff-Hopeful',
    'Tiger-Veteran',
    'Turkey-Gilded',
    'Wolf-Veteran',
}

pet_kinds = pet_kinds_standard | pet_kinds_magic_potion.keys() | pet_kinds_special

pet_symbols = {
    'Alligator': '🐊',
    'Armadillo': '🐾',
    'Axolotl': '🦎', # 𓆈
    'Badger': '🦡',
    'BearCub': '🐻',
    'Beetle': '🪲',
    'Bunny': '🐇', # 🐰
    'Butterfly': '🦋',
    'Cactus': '🌵',
    'Chameleon': '𓆈', # 🦎
    'Cheetah': '🐆',
    'Cow': '🐄', # 🐮
    'Cuttlefish': '🐡', # 🐟🐠
    'Deer': '🦌',
    'Dolphin': '🐬',
    'Dragon': '🐉', # 🐲
    'Egg': '🥚',
    'Falcon': '🦅',
    'Ferret': '🐾',
    'FlyingPig': '🐖', # 🐷
    'Fox': '🦊',
    'Frog': '🐸',
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
    'Owl': '🦉',
    'Parrot': '🦜',
    'Peacock': '🦚',
    'Penguin': '🐧',
    #'PolarBear': '🐻‍❄️',
    'Pterodactyl': '🐦', # 🦕
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
}

# -- Platform-specific spacing hacks --

# Most emoji are 2 characters wide in most fixed-width font scenarios.
# But a few are only 1 character wide in some cases (fonts? terminals? OSes?).
# This represents a best effort to pad out the ones that don't align otherwise.

padded_kinds = ['Frost', 'IcySnow', 'Polar', 'StainedGlass', 'Sunshine', 'Thunderstorm']
padded_species = ['Chameleon', 'Spider', 'Squirrel']

from sys import platform
if platform == 'darwin':
    # This change is needed only for iTerm2.
    # With Terminal, it misaligns these items.
    # But I use iTerm2, so nyeh.
    padded_kinds.extend(('Glass', 'MossyStone', 'Silver'))
    padded_species.extend(('Beetle',))

for kind in padded_kinds:
    pet_kinds_magic_potion[kind] += ' '
for species in padded_species:
    pet_symbols[species] += ' '

# -- Quest scrolls --

quest_scrolls_pet = {
    'armadillo', 'axolotl', 'badger', 'beetle', 'bunny', 'butterfly',
    'cheetah', 'cow', 'dilatory_derby', 'dolphin', 'egg', 'falcon', 'ferret',
    'frog', 'ghost_stag', 'gryphon', 'guineapig', 'harpy', 'hedgehog', 'hippo',
    'horse', 'kangaroo', 'kraken', 'monkey', 'nudibranch', 'octopus', 'owl',
    'peacock', 'penguin', 'pterodactyl', 'rat', 'robot', 'rock', 'rooster',
    'sabretooth', 'seaserpent', 'sheep', 'slime', 'sloth', 'snail', 'snake',
    'spider', 'squirrel', 'treeling', 'trex', 'trex_undead', 'triceratops',
    'turtle', 'unicorn', 'velociraptor', 'whale', 'yarn'
}

quest_scrolls_magic_hatching_potion = {
    'amber', 'blackPearl', 'bronze', 'fluorite', 'onyx', 'ruby', 'silver',
    'stone', 'turquoise'
}

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
    'waffle', # ???
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

quest_scrolls = quest_scrolls_pet | quest_scrolls_magic_hatching_potion | quest_scrolls_other

quest_scroll_bundles = {
    'aquaticAmigos': ['axolotl', 'kraken', 'octopus'],
    'birdBuddies': [], # TODO
    'cuddleBuddies': [], # TODO
    'delightfulDinos': [], # TODO
    'farmFriends': ['horse', 'sheep', 'cow'],
    'featheredFriends': [], # TODO
    'forestFriends': [], # TODO
    'hugabug': [], # TODO
    'jungleBuddies': ['monkey', 'treeling', 'sloth'],
    'mythicalMarvels': [], # TODO
    'oddballs': [], # TODO
    'rockingReptiles': [], # TODO
    'sandySidekicks': [], # TODO
    'splashyPals': [], # TODO
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
        f"| {pet_symbols[species]} " +
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
print(f"|    | MAGIC POTION  | PETS | MOUNTS | POTIONS | SHORTAGE |")
print(f"|----|:--------------|-----:|-------:|--------:|---------:|")
standard_pets_count = len([species for species, quest_scroll in pet_species.items() if quest_scroll is None])
for kind, symbol in sorted(pet_kinds_magic_potion.items()):
    my_pets = {f"{p}:{hunger}" for p, hunger in pets.items() if p.endswith(f"-{kind}") and hunger > 0}
    my_mounts = {f"{m}" for m, v in mounts.items() if m.endswith(f"-{kind}") and v is True}
    potion_count = potions[kind] if kind in potions else 0
    shortage = 2 * standard_pets_count - len(my_pets) - len(my_mounts) - potion_count

    if shortage <= 0:
        color = 'blue'
        shortage = 'none'
    elif shortage < 9: color = 'green'
    elif shortage < 18: color = 'yellow'
    else: color = 'red'

    print(f"{colors[color]}" +
        f"| {symbol} " +
        f"| {kind:13} " +
        f"| {len(my_pets):>2}/{standard_pets_count} " +
        f"|   {len(my_mounts):>2}/{standard_pets_count} " +
        f"| {potion_count:>7} " +
        f"| {shortage:>8} " +
        f"|{colors['reset']}")

for p, _ in pets.items():
    if p not in unique_pets and p[p.rindex("-")+1:] not in pet_kinds:
        print(f"{colors[color]}[WARNING] Unknown pet type! {p}{colors['reset']}")

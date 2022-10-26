"""
A script to list IDs of quests that you own.

Usage: python quest-list.py
"""

import habitica

session = habitica.session()
quests = session.profile('items')['items']['quests']

print("Available quests:")
for quest_id, count in quests.items():
    if count > 0:
        print(f"* {count}x {quest_id}")

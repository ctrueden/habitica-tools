"""
A script to force-start a quest, if not already started.

Usage: python quest-force.py
"""

import logging

import habitica

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

session = habitica.session()

party = session.party()
if party['quest']['active']:
    log.info(f"Quest {party['quest']['key']} is already active.")
else:
    log.info(f"Quest still not started... force starting!")
    result = session.force_start_quest()
    log.info(result)

"""
A script to run cron immediately.

Usage: python autocron.py
"""

import logging

import habitica

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def main():
    log.info("Connecting...")
    session = habitica.session(log=log)
    log.info("Cronning...")
    session.cron()
    log.info("Done! :-)")

if __name__ == "__main__":
    main()


#!/bin/sh
while [ $# -gt 0 ]
do
  echo
  python3 wait-until.py 22:45
  echo
  echo "== Starting pre-smash quest =="
  test "$1" && python3 quest-start.py "$1"
  shift

  echo
  python3 wait-until.py 23:50
  echo
  echo "== Smashing the boss =="
  python3 quest-force.py
  python3 autosmash.py

  echo
  python3 wait-until.py 01:30
  echo
  echo "== Starting post-smash quest =="
  test "$1" && python3 quest-start.py "$1"
  shift
done

#!/bin/sh

randomQuest() {
  python3 quest-list.py 2>&1 | grep '[0-9]x' | sed 's/.* //' |
    grep -v '\(dustbunnies\|atom1\|vice1\|basilist\|goldenknight1\|moon2\|moon3\|moonstone1\|vice2\|stoikalmCalamity1\|stoikalmCalamity2\|stoikalmCalamity3\|mayhemMistiflying1\|mayhemMistiflying2\|mayhemMistiflying3\|dilatoryDistress1\|dilatoryDistress2\|dilatoryDistress3\|taskwoodsTerror1\|taskwoodsTerror2\|taskwoodsTerror3\|lostMasterclasser2\|lostMasterclasser3\|lostMasterclasser4\|cow\)' |
    shuf | head -n1
}

startQuest() {
  quest=$(randomQuest)
  echo
  echo "== Starting $1 quest =="
  if [ "$quest" ]
  then
    python3 quest-start.py "$quest"
  else
    echo "No suitable quests owned!"
  fi
}

while true
do
  echo
  python3 wait-until.py 22:45
  startQuest pre-smash

  echo
  python3 wait-until.py 23:50
  echo
  echo "== Smashing the boss =="
  python3 quest-force.py
  python3 autosmash.py

  echo
  python3 wait-until.py 01:30
  startQuest post-smash
done

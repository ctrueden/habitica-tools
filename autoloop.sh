#!/bin/sh

randomQuest() {
  override=raccoon
  quests=$(python3 quest-list.py 2>&1)
  echo "$quests" | grep -q "$override" && echo "$override" ||
  echo "$quests" | grep '[0-9]x' | sed 's/.* //' |
    grep -v '\(dustbunnies\|atom1\|vice1\|basilist\|goldenknight1\|moonstone1\|vice2\|stoikalmCalamity1\|stoikalmCalamity2\|mayhemMistiflying1\|mayhemMistiflying2\|dilatoryDistress1\|dilatoryDistress2\|taskwoodsTerror1\|taskwoodsTerror2\|lostMasterclasser1\|lostMasterclasser2\|lostMasterclasser3\|lostMasterclasser4\|cow\|seaserpent\|treeling\)' |
    sort -R | head -n1
}

startQuest() {
  quest=$(randomQuest)
  #quest=lostMasterclasser2
  echo
  echo "== Starting $1 quest =="
  if [ "$quest" ]
  then
    python3 quest-invite.py "$quest"
  else
    echo "No suitable quests owned!"
  fi
}

while true
do
  echo
  python3 wait-until.py 22:45
  startQuest pre-smash-2245

  echo
  python3 wait-until.py 23:05
  startQuest pre-smash-2305

  echo
  python3 wait-until.py 23:25
  startQuest pre-smash-2325

  echo
  python3 wait-until.py 23:59
  echo
  echo "== Smashing the boss =="
  python3 quest-force.py
  python3 autosmash.py
  echo "Waiting 60 seconds..."
  sleep 60
  python3 autocron.py

  echo
  python3 wait-until.py 00:15
  startQuest post-smash-0015

  echo
  python3 wait-until.py 00:45
  startQuest post-smash-0045

  echo
  python3 wait-until.py 01:15
  startQuest post-smash-0115
done

# restlesscoder's Habitica Tools

This repository contains a general-purpose Habitica session class for Python
(`habitica.py`), along with a couple of scripts to automate repetitive tasks:

* `autosmash.py` - For warriors: repeatedly use Brutal Smash until you reach
  a particular amount of damage. Automatically equips STR-maximal gear before
  smashing, and restores your originally equipped gear afterward.

* `autofeed.py` - Automatically uses the optimal food on all pets that need
  feeding, to advance them toward becoming mounts as efficiently as possible.

* `autoquest.py` - Waits until the given time, then invites your party to the
  specified quest, then ensures it starts (forcing if needed) within the
  specified amount of time afteward.

The only dependency is `requests`.

## Configuring credentials

Create a file at `~/.config/habitica-tools/config.json` with the line:

```json
{"apiToken": "12345678-abcd-9876-0123-456789abcdef"}
```

Where `12345678-abcd-9876-0123-456789abcdef` is your Habitica user's
[API token](https://habitica.fandom.com/wiki/API_Options#API_Token).

Then, `chmod 600 config.json` to ensure no one but you can read the contents.

## Autosmash

```shell
python autosmash.py 15
```
where `15` is the number of smashes to perform. Brutal Smash will be used
sequentially on each task, starting from the lowest valued (reddest) task.

Before smashing, the script equips the best STR gear, and then
after smashing is complete, re-equips your original gear.

## Autofeed

```shell
python autofeed.py
```

No options. The script feeds the optimal food to the first pet that needs it,
repeatedly, until no more optimal food/pet pairings remain in your inventory.

## Autoquest

```shell
python autoquest.py quest-id invite-time force-start-after
```
where:
* `quest-id` is the quest ID string.
* `invite-time` is an `HH:MM` timestamp e.g. `23:10`.
* `force-start-after` is a number of minutes before forcing it to start.

If you run `python autoquest.py` with no arguments,
the program lists the IDs of quests that you own.

## Using the session API

```python
import habitica
session = habitica.session()
profile = session.profile()
quest_count = sum(v in profile['achievements']['quests'].values())
print(f"Your username is: {profile['auth']['local']['username']}")
print(f"You own {quest_count} quest scrolls.")
```

## Alternatives

* [Habitipy](https://github.com/ASMfreaK/habitipy)

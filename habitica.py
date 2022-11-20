"""
The habitica module provides a general-purpose Python library for
interacting with Habitica via its API (https://habitica.com/api).

It currently implements only a small subset of the available API functions.
But the groundwork is in place to add more functions easily as needed;
see https://habitica.com/apidoc/ for Habitica's API documentation.
"""
import json, os, time
import requests


dev_ids = {
    'restlesscoder': 'd7bff991-881d-4f47-b3f5-4b4885b41a5f'
}


def load_config():
    """
    Read configuration values from disk.

    Configuration is loaded from: ~/.config/habitica-tools/config.json

    In particular, this is useful for restoring persisted API tokens.

    :return: Dictionary of configuration key/value pairs.
    """
    config_file = os.path.expanduser('~/.config/habitica-tools/config.json')
    if os.path.exists(config_file):
        with open(config_file) as f:
            return json.load(f)
    return {}


def status():
    """
    Get Habitica's API status

    :return: A truthy value if everything is ok, a falsy value if not
    """
    response = requests.get('https://habitica.com/api/v3/status')
    if not response.ok:
        return False
    jsondata = response.json()
    return jsondata['success'] if 'success' in jsondata else False


def session(api_token=None, username=None, password=None, log=None):
    """
    Connect to Habitica.

    :return: Habitica session object for performing operations.
    """
    if not status():
        raise RuntimeError("The System is Down!")

    if api_token is None and username is None and password is None:
        config = load_config()
        if 'apiToken' in config:
            api_token = config['apiToken']

    return HabiticaSession(api_token, username, password, log)


class HabiticaSession:

    def __init__(self, api_token=None, username=None, password=None, log=None):
        self.api_token = api_token
        if username is not None and password is not None:
            self._login(username, password)

        if self.api_token is None:
            raise ValueError('You must specify either an API token, ' +
                'or a username + password for login')

        self.log = log


    # -- Group --


    def party(self):
        """
        Get the user's party.

        :return: Details about the user's party.
        """
        return self._get('https://habitica.com/api/v3/groups/party')


    # -- Quest --


    def invite_quest(self, quest_key, group_id='party'):
        """
        Invite users to a quest.

        :param group_id: The group_id (or 'party')
        :param quest_key:
        """
        return self._post(f'https://habitica.com/api/v3/groups/{group_id}/quests/invite/{quest_key}')


    def force_start_quest(self, group_id='party'):
        """
        Force-start a pending quest.

        :param group_id: The group_id (or 'party')
        """
        return self._post(f'https://habitica.com/api/v3/groups/{group_id}/quests/force-start')


    # -- Task --


    def tasks(self, task_type=None, due_date=None):
        """
        Get a user's tasks.

        :param task_type: Optional query parameter to return just a type of
                          tasks. By default all types will be returned except
                          completed todos that must be requested separately. The
                          "completedTodos" type returns only the 30 most
                          recently completed.

                          Allowed values: habits, dailys, todos, rewards, completedTodos 

        :param due_date: Optional date to use for computing the nextDue field
                         for each returned task.

        :return: An array of tasks
        """
        params = {}
        if task_type is not None:
            valid_task_types = (
                'habits', 'dailys', 'todos', 'rewards', 'completedTodos'
            )
            if not task_type in valid_task_types:
                raise ValueError(f'Invalid task type: {task_type}')
            params['type'] = task_type
        if due_date is not None:
            params['dueDate'] = due_date

        return self._get('https://habitica.com/api/v3/tasks/user', params)


    # -- User --


    def cast(self, spell_id, target_id=None):
        """
        Cast a skill (spell) on a target.

        :param spell_id: The skill to cast.
                         Allowed values: fireball, mpheal, earth, frost, smash,
                         defensiveStance, valorousPresence, intimidate,
                         pickPocket, backStab, toolsOfTrade, stealth, heal,
                         protectAura, brightness, healAll, snowball,
                         spookySparkles, seafoam, shinySeed 

        :param target_id: Query parameter, necessary if the spell is cast on a
                          party member or task. Not used if the spell is casted
                          on the user or the user's current party.

        :return: Results, in a dictionary.
        """
        valid_spell_ids = (
            'smash', 'defensiveStance', 'valorousPresence', 'intimidate',
            'fireball', 'mpheal', 'earth', 'frost',
            'pickPocket', 'backStab', 'toolsOfTrade', 'stealth',
            'heal', 'protectAura', 'brightness', 'healAll',
            'snowball', 'spookySparkles', 'seafoam', 'shinySeed',
        )
        if not spell_id in valid_spell_ids:
            raise ValueError(f'Invalid spell ID: {spell_id}')

        params = {}
        if target_id is not None:
            params['targetId'] = target_id

        return self._post(f'https://habitica.com/api/v3/user/class/cast/{spell_id}', params)


    def equip(self, item_type, item_key):
        """
        Equip or unequip an item.

        :param item_type: The type of item to equip or unequip.
                          Allowed values: mount, pet, costume, equipped

        :param item_key: The item to equip or unequip

        :return: Results, in a dictionary.
        """
        valid_item_types = ('mount', 'pet', 'costume', 'equipped')
        if not item_type in valid_item_types:
            raise ValueError(f'Invalid item type: {item_type}')

        return self._post(f'https://habitica.com/api/v3/user/equip/{item_type}/{item_key}')


    def feed(self, pet, food, amount=None):
        """
        Feed a pet.

        :param pet:
        :param food:
        :param amount: The amount of food to feed. Note: Pet can eat 50 units.
                       Preferred food offers 5 units per food, other food 2 units.

        :return: The pet value
        """
        params = {}
        if amount is not None:
            params['amount'] = amount
        return self._post(f'https://habitica.com/api/v3/user/feed/{pet}/{food}', params)
        #E.g. https://habitica.com/api/v3/user/feed/Armadillo-Shade/Chocolate?amount=9
        raise RuntimeError('unimplemented')


    def profile(self, user_fields=None):
        """
        Get the authenticated user's profile.

        The user profile contains data related to the authenticated user
        including (but not limited to):
        * Achievements
        * Authentications (including types and timestamps)
        * Challenges memberships (Challenge IDs)
        * Flags (including armoire, tutorial, tour etc...)
        * Guilds memberships (Guild IDs)
        * History (including timestamps and values, only for Experience and summed To Do values)
        * Inbox
        * Invitations (to parties/guilds)
        * Items (character's full inventory)
        * New Messages (flags for party/guilds that have new messages; also reported in Notifications)
        * Notifications
        * Party (includes current quest information)
        * Preferences (user selected prefs)
        * Profile (name, photo url, blurb)
        * Purchased (includes subscription data and some gem-purchased items)
        * PushDevices (identifiers for mobile devices authorized)
        * Stats (standard RPG stats, class, buffs, xp, etc..)
        * Tags
        * TasksOrder (list of all IDs for Dailys, Habits, Rewards and To Do's).

        :param user_fields: A list of comma-separated user fields to be
                            returned instead of the entire document.
                            Notifications are always returned.

        :return: The user object
        """
        params = {}
        if user_fields is not None:
            params['userFields'] = user_fields

        return self._get('https://habitica.com/api/v3/user', params)


    def _login(self, username, password):
        """
        Login a user with email / username and password.

        :param username: Username or email of the user
        :param password: The user's password
        """
        self._log.info(f'Logging in as {username}...')

        body = {
            'username': username,
            'password': password,
        }
        result = self._post('https://habitica.com/api/v3/user/auth/local/login', body=body)

        if 'apiToken' not in result:
            raise ValueError('Invalid login.')

        user_id = result['_id']
        self._info(f'Login successful - user_id: {user_id}')
        self.api_token = result['apiToken']


    @property
    def _headers(self):
        dev_id = dev_ids['restlesscoder']
        return {
            'X-Client': f'{dev_id}-habitica-tools',
            'X-API-User': dev_id,
            'X-API-Key': self.api_token,
        }

    def _get(self, url, params=None):
        if params is None: params = {}
        return self._result(self._try(
            lambda: requests.get(url, params=params, headers=self._headers)
        ))

    def _post(self, url, params=None, body=None):
        if params is None: params = {}
        if body is None: body = {}
        return self._result(self._try(
            lambda: requests.post(url, json=body, params=params, headers=self._headers)
        ))

    def _try(self, f, max_retries=5, cooldown=20):
        for i in range(1, max_retries + 1):
            try:
                return f()
            except Exception as exc:
                self._error(f"[{i}/{max_retries}] Error communicating with Habitica: {exc}")
                if i == max_retries:
                    raise exc
                time.sleep(cooldown)

    def _result(self, response):
        if not response.ok:
            raise RuntimeError(
                f'Server returned bad status: {response.status_code}'
            )
        jsondata = response.json()
        if 'message' in jsondata:
            self._info(jsondata['message'])
        if jsondata['success'] is False:
            raise ValueError('Operation failed.')
        return jsondata['data']


    def _info(self, message):
        if self.log is not None:
            self.log.info(message)

    def _warn(self, message):
        if self.log is not None:
            self.log.warning(message)

    def _error(self, message):
        if self.log is not None:
            self.log.error(message)

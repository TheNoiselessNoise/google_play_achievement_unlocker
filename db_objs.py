import os
from datetime import datetime
from inspect import getframeinfo, stack
from typing import List, Any, Union

class Wrapper:
    _id = None
    _changers = {}

    def attrs(self):
        return [x for x in self.__dict__ if not x.startswith("__") and not x.endswith("__") and x not in ["_changers"]]

    def values(self):
        return [getattr(self, x) for x in self.attrs()]

    def dump(self, changers=0):
        if changers == 0:
            changers = self._changers
        if changers is None:
            changers = {}

        caller = getframeinfo(stack()[1][0])
        fname, line = caller.filename, caller.lineno
        fname = os.path.relpath(fname, os.getcwd())

        name = self.__class__.__name__
        vals = {x: getattr(self, x) for x in self.attrs()}
        for k, v in changers.items():
            if k in vals:
                vals[k] = v(vals[k])
        dmp = "\n\t".join(f"{x} = {y}" for x, y in vals.items())
        print(f"{fname}:{line}:{name}:\n\t{dmp}")

    @staticmethod
    def join(*args, sep=" : "):
        return sep.join(str(x) for x in args)

    @property
    def id(self):
        return self._id

# device-known achievements
class AchievementDefinition(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0] or None
        self.game_id = args[1] or None
        self.external_achievement_id = args[2] or None
        self.type = args[3] or None
        self.name = args[4] or None
        self.description = args[5] or None
        self.unlocked_icon_image_id = args[6] or None
        self.revealed_icon_image_id = args[7] or None
        self.total_steps = args[8] or None
        self.formatted_total_steps = args[9] or None
        self.initial_state = args[10] or None
        self.sorting_rank = args[11] or None
        self.definition_xp_value = args[12] or None
        self.rarity_percent = args[13] or None

    def print_string(self):
        return self.join(self.external_achievement_id, self.name, self.description, f"{self.definition_xp_value}xp")

# all achievements that has been unlocked and when + progress of incremental achievements
class AchievementInstance(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._changers = {
            "last_updated_timestamp": lambda x: datetime.fromtimestamp(x / 1000)
        }

        self._id = args[0] or None
        self.definition_id = args[1] or None
        self.player_id = args[2] or None
        self.state = args[3] or None
        self.current_steps = args[4] or None
        self.formatted_current_steps = args[5] or None
        self.last_updated_timestamp = args[6] or None
        self.instance_xp_value = args[7] or None


# apps logged in to Google Play
class ClientContext(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._changers = {
            "account_name": lambda x: x[0:2] + "*" * (len(x) - x.find("@") - 2) + x[x.find("@")-2:]
        }

        self._id = args[0] or None
        self.package_name = args[1] or None
        self.package_uid = args[2] or None
        self.account_name = args[3] or None
        self.account_type = args[4] or None
        self.is_games_lite = args[5] or None

    def print_string(self, secure=False):
        account_name = self._changers["account_name"](self.account_name) if secure else self.account_name
        return self.join(self.id, self.package_name, account_name)

class GameInstance(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0] or None
        self.instance_game_id = args[1] or None
        self.real_time_support = args[2] or None
        self.turn_based_support = args[3] or None
        self.platform_type = args[4] or None
        self.instance_display_name = args[5] or None
        self.package_name = args[6] or None
        self.piracy_check = args[7] or None
        self.installed = args[8] or None
        self.preferred = args[9] or None
        self.gamepad_support = args[10] or None


class GamePlayerId(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0] or None
        self.game_player_ids_external_player_id = args[1] or None
        self.game_player_ids_external_game_id = args[2] or None
        self.game_player_ids_external_game_player_id = args[3] or None
        self.game_player_ids_external_primary_player_id = args[4] or None
        self.game_player_ids_created_in_epoch = args[5] or None


class Game(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0] or None
        self.external_game_id = args[1] or None
        self.display_name = args[2] or None
        self.primary_category = args[3] or None
        self.secondary_category = args[4] or None
        self.developer_name = args[5] or None
        self.game_description = args[6] or None
        self.game_icon_image_id = args[7] or None
        self.game_hi_res_image_id = args[8] or None
        self.featured_image_id = args[9] or None
        self.screenshot_image_ids = args[10] or None
        self.screenshot_image_widths = args[11] or None
        self.screenshot_image_heights = args[12] or None
        self.video_url = args[13] or None
        self.play_enabled_game = args[14] or None
        self.last_played_server_time = args[15] or None
        self.last_connection_local_time = args[16] or None
        self.last_synced_local_time = args[17] or None
        self.metadata_version = args[18] or None
        self.sync_token = args[19] or None
        self.metadata_sync_requested = args[20] or None
        self.target_instance = args[21] or None
        self.gameplay_acl_status = args[22] or None
        self.availability = args[23] or None
        self.owned = args[24] or None
        self.achievement_total_count = args[25] or None
        self.leaderboard_count = args[26] or None
        self.price_micros = args[27] or None
        self.formatted_price = args[28] or None
        self.full_price_micros = args[29] or None
        self.formatted_full_price = args[30] or None
        self.explanation = args[31] or None
        self.description_snippet = args[32] or None
        self.starRating = args[33] or None
        self.ratingsCount = args[34] or None
        self.muted = args[35] or None
        self.identity_sharing_confirmed = args[36] or None
        self.snapshots_enabled = args[37] or None
        self.theme_color = args[38] or None
        self.lastUpdatedTimestampMillis = args[39] or None

    def print_string(self, inst: GameInstance = None):
        middle = self.developer_name if inst is None else inst.package_name
        return self.join(self.external_game_id, middle, self.display_name)

class Image(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0] or None
        self.url = args[1] or None
        self.local = args[2] or None
        self.filesize = args[3] or None
        self.download_timestamp = args[4] or None


class Finder:
    def __init__(self, db_instance):
        self.db = db_instance

    def ach_def_by_id(self, x: Any) -> AchievementDefinition:
        return self.findby(x, ["_id"], self.db.achievement_definitions, first=True, exact=True)

    def ach_inst_by_id(self, x: Any) -> AchievementInstance:
        return self.findby(x, ["_id"], self.db.achievement_instances, first=True, exact=True)

    def client_context_by_id(self, x: Any) -> ClientContext:
        return self.findby(x, ["_id"], self.db.client_contexts, first=True, exact=True)

    def game_inst_by_id(self, x: Any) -> GameInstance:
        return self.findby(x, ["_id"], self.db.game_instances, first=True, exact=True)

    def game_player_id_by_id(self, x: Any) -> GamePlayerId:
        return self.findby(x, ["_id"], self.db.game_player_ids, first=True, exact=True)

    def game_by_id(self, x: Any) -> Game:
        return self.findby(x, ["_id"], self.db.games, first=True, exact=True)

    def image_by_id(self, x: Any) -> Image:
        return self.findby(x, ["_id"], self.db.images, first=True, exact=True)

    def ach_def_by_ach_inst(self, x: AchievementInstance) -> AchievementDefinition:
        return self.findby(x.definition_id, ["_id"], self.db.achievement_definitions, first=True, exact=True)

    def ach_defs_by_ach_insts(self, x: List[AchievementInstance]) -> List[AchievementDefinition]:
        return [self.ach_def_by_ach_inst(y) for y in x]

    def game_inst_by_game(self, x: Game) -> GameInstance:
        return self.findby(x.id, ["instance_game_id"], self.db.game_instances, first=True, exact=True)

    def game_insts_by_games(self, x: List[Game]) -> List[GameInstance]:
        return [self.game_inst_by_game(y) for y in x]

    def game_inst_by_game_id(self, x: Any) -> GameInstance:
        return self.findby(x, ["instance_game_id"], self.db.game_instances, first=True, exact=True)

    def game_inst_by_package_name(self, x: str) -> GameInstance:
        return self.findby(x, ["package_name"], self.db.game_instances, first=True, exact=True)

    def game_by_game_inst(self, x: GameInstance) -> Game:
        return self.findby(x.instance_game_id, ["_id"], self.db.games, first=True, exact=True)

    def game_by_external_id(self, x: Any) -> Game:
        return self.findby(x, ["external_game_id"], self.db.games, first=True, exact=True)

    def game_by_ach_inst(self, x: AchievementInstance) -> Game:
        game = None
        udef = self.ach_def_by_ach_inst(x)
        if udef is not None:
            game = self.findby(udef.game_id, ["_id"], self.db.games, first=True, exact=True)
        return game

    def game_by_name(self, search: Any) -> Union[Game, list]:
        return self.find(search, self.db.games, first=True, exact=True)

    def games_by_name(self, search: Any) -> Union[Game, list]:
        return self.find(search, self.db.games, exact=True)

    def game_by_ach_def(self, x: AchievementDefinition) -> Game:
        return self.findby(x.game_id, ["_id"], self.db.games, first=True, exact=True)

    def games_by_ach_defs(self, x: List[AchievementDefinition]) -> List[Game]:
        return [self.game_by_ach_def(y) for y in x]

    def ach_defs_by_game_id(self, x: Any) -> List[AchievementDefinition]:
        return self.findby(x, ["game_id"], self.db.achievement_definitions, exact=True)

    def ach_defs_by_game(self, x: Game) -> List[AchievementDefinition]:
        return self.ach_defs_by_game_id(x.id)

    def ach_inst_by_ach_def(self, x: AchievementDefinition) -> AchievementInstance:
        return self.findby(x.id, ["definition_id"], self.db.achievement_instances, first=True, exact=True)

    def ach_insts_by_ach_defs(self, x: List[AchievementDefinition]) -> List[AchievementInstance]:
        return [self.ach_inst_by_ach_def(y) for y in x]

    def ach_insts_by_game_id(self, x: Any) -> List[AchievementInstance]:
        insts = []
        ugame = self.game_by_id(x)
        if ugame is not None:
            udefs = self.ach_defs_by_game(ugame)
            if udefs is not None:
                insts = self.ach_insts_by_ach_defs(udefs)
        return insts

    def ach_insts_by_game(self, x: Game) -> List[AchievementInstance]:
        return self.ach_insts_by_game_id(x.id)

    def findby(self, s: Any, cols=None, objs=None, first=False, exact=False):
        if not objs:
            return []
        if not cols:
            return self.find(s, objs, first)

        found = []
        s = str(s).lower()
        for obj in objs:
            attrs = obj.attrs()
            attrs = [x for x in cols if x in attrs]
            values = [str(getattr(obj, x)).lower() for x in attrs]
            if any(s == x if exact else s in x for x in values):
                found.append(obj)

        return found[0] if len(found) and first else found

    @staticmethod
    def find(search: Any, objs: List[Wrapper], first=False, exact=False):
        s = str(search).lower()
        res = list(filter(
            lambda x: any(s == str(y).lower() if exact else s in str(y).lower() for y in x.values()), objs))
        return res[0] if len(res) and first else res


mapping = {
    "achievement_definitions": AchievementDefinition,
    "achievement_instances": AchievementInstance,
    "client_contexts": ClientContext,
    "game_instances": GameInstance,
    "game_player_ids": GamePlayerId,
    "games": Game,
    "images": Image
}


class DbFile:
    def __init__(self, connection):
        self.connection = connection
        self.cur = self.connection.cursor()

        # these are not needed, only for IDE
        self.achievement_definitions = []
        self.achievement_instances = []
        self.client_contexts = []
        self.game_instances = []
        self.game_player_ids = []
        self.games = []
        self.images = []

        ex = lambda y: self.cur.execute("select * from " + y + " order by _id")
        for table, cls in mapping.items():
            res = ex(table).fetchall()
            setattr(self, table, [cls(*x) for x in res])

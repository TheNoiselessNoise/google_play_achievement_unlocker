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

        self._id = args[0]
        self.game_id = args[1]
        self.external_achievement_id = args[2]
        self.type = args[3]
        self.name = args[4]
        self.description = args[5]
        self.unlocked_icon_image_id = args[6]
        self.revealed_icon_image_id = args[7]
        self.total_steps = args[8]
        self.formatted_total_steps = args[9]
        self.initial_state = args[10]
        self.sorting_rank = args[11]
        self.definition_xp_value = args[12]
        self.rarity_percent = args[13]

    def print_string(self):
        return self.join(self.external_achievement_id, self.name, self.description, f"{self.definition_xp_value}xp")

# all achievements that has been unlocked and when + progress of incremental achievements
class AchievementInstance(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._changers = {
            "last_updated_timestamp": lambda x: datetime.fromtimestamp(x / 1000)
        }

        self._id = args[0]
        self.definition_id = args[1]
        self.player_id = args[2]
        self.state = args[3]
        self.current_steps = args[4]
        self.formatted_current_steps = args[5]
        self.last_updated_timestamp = args[6]
        self.instance_xp_value = args[7]

class AchievementPendingOp(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0]
        self.client_context_id = args[1]
        self.external_achievement_id = args[2]
        self.achievement_type = args[3]
        self.new_state = args[4]
        self.steps_to_increment = args[5]
        self.min_steps_to_set = args[6]
        self.external_game_id = args[7]
        self.external_player_id = args[8]

# apps logged in to Google Play
class ClientContext(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._changers = {
            "account_name": lambda x: x[0:2] + "*" * (len(x) - x.find("@") - 2) + x[x.find("@")-2:]
        }

        self._id = args[0]
        self.package_name = args[1]
        self.package_uid = args[2]
        self.account_name = args[3]
        self.account_type = args[4]
        self.is_games_lite = args[5]

    def print_string(self, secure=False):
        account_name = self._changers["account_name"](self.account_name) if secure else self.account_name
        return self.join(self.id, self.package_name, account_name)

class GameInstance(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0]
        self.instance_game_id = args[1]
        self.real_time_support = args[2]
        self.turn_based_support = args[3]
        self.platform_type = args[4]
        self.instance_display_name = args[5]
        self.package_name = args[6]
        self.piracy_check = args[7]
        self.installed = args[8]
        self.preferred = args[9]
        self.gamepad_support = args[10]


class GamePlayerId(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0]
        self.game_player_ids_external_player_id = args[1]
        self.game_player_ids_external_game_id = args[2]
        self.game_player_ids_external_game_player_id = args[3]
        self.game_player_ids_external_primary_player_id = args[4]
        self.game_player_ids_created_in_epoch = args[5]


class Game(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0]
        self.external_game_id = args[1]
        self.display_name = args[2]
        self.primary_category = args[3]
        self.secondary_category = args[4]
        self.developer_name = args[5]
        self.game_description = args[6]
        self.game_icon_image_id = args[7]
        self.game_hi_res_image_id = args[8]
        self.featured_image_id = args[9]
        self.screenshot_image_ids = args[10]
        self.screenshot_image_widths = args[11]
        self.screenshot_image_heights = args[12]
        self.video_url = args[13]
        self.play_enabled_game = args[14]
        self.last_played_server_time = args[15]
        self.last_connection_local_time = args[16]
        self.last_synced_local_time = args[17]
        self.metadata_version = args[18]
        self.sync_token = args[19]
        self.metadata_sync_requested = args[20]
        self.target_instance = args[21]
        self.gameplay_acl_status = args[22]
        self.availability = args[23]
        self.owned = args[24]
        self.achievement_total_count = args[25]
        self.leaderboard_count = args[26]
        self.price_micros = args[27]
        self.formatted_price = args[28]
        self.full_price_micros = args[29]
        self.formatted_full_price = args[30]
        self.explanation = args[31]
        self.description_snippet = args[32]
        self.starRating = args[33]
        self.ratingsCount = args[34]
        self.muted = args[35]
        self.identity_sharing_confirmed = args[36]
        self.snapshots_enabled = args[37]
        self.theme_color = args[38]
        self.lastUpdatedTimestampMillis = args[39]

    def print_string(self, inst: GameInstance = None):
        middle = self.developer_name if inst is None else inst.package_name
        return self.join(self.external_game_id, middle, self.display_name)

class Image(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0]
        self.url = args[1]
        self.local = args[2]
        self.filesize = args[3]
        self.download_timestamp = args[4]

class Player(Wrapper):
    def __init__(self, *args):
        super().__init__()

        self._id = args[0]
        self.external_player_id = args[1]
        self.profile_name = args[2]
        self.profile_icon_image_id = args[3]
        self.profile_hi_res_image_id = args[4]
        self.last_updated = args[5]
        self.is_in_circles = args[6]
        self.current_xp_total = args[7]
        self.current_level = args[8]
        self.current_level_min_xp = args[9]
        self.current_level_max_xp = args[10]
        self.next_level = args[11]
        self.next_level_max_xp = args[12]
        self.last_level_up_timestamp = args[13]
        self.player_title = args[14]
        self.has_all_public_acls = args[15]
        self.has_debug_access = args[16]
        self.is_profile_visible = args[17]
        self.most_recent_activity_timestamp = args[18]
        self.most_recent_external_game_id = args[19]
        self.most_recent_game_name = args[20]
        self.most_recent_game_icon_id = args[21]
        self.most_recent_game_hi_res_id = args[22]
        self.most_recent_game_featured_id = args[23]
        self.gamer_tag = args[24]
        self.real_name = args[25]
        self.banner_image_landscape_id = args[26]
        self.banner_image_portrait_id = args[27]
        self.total_unlocked_achievements = args[28]
        self.play_together_friend_status = args[29]
        self.play_together_nickname = args[30]
        self.play_together_invitation_nickname = args[31]
        self.profile_creation_timestamp = args[32]
        self.nickname_abuse_report_token = args[33]
        self.friends_list_visibility = args[34]
        self.always_auto_sign_in = args[35]

    def print_string(self):
        return self.join(self.external_player_id, self.profile_name, f"Level {self.current_level}")


class Finder:
    def __init__(self, db_instance):
        self.db = db_instance

    def ach_def_by_id(self, x: Any) -> AchievementDefinition:
        return self.findby(x, ["_id"], self.db.achievement_definitions, first=True, exact=True)

    def ach_def_by_external_id(self, x: Any) -> AchievementDefinition:
        return self.findby(x, ["external_achievement_id"], self.db.achievement_definitions, first=True, exact=True)

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

    def client_context_by_game_inst(self, x: GameInstance) -> ClientContext:
        return self.findby(x.package_name, ["package_name"], self.db.client_contexts, first=True, exact=True)

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
    "images": Image,
    "players": Player
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
        self.players = []

        for table, cls in mapping.items():
            res = self.ex(table).fetchall()
            setattr(self, table, [cls(*x) for x in res])

    def ex(self, table):
        return self.cur.execute("select * from " + table + " order by _id")

    def remove_duplicate_pending_ops(self, by_col="external_achievement_id"):
        ops = [AchievementPendingOp(*x) for x in self.ex("achievement_pending_ops").fetchall()]
        seen = set()
        removed = 0
        for op in ops:
            if getattr(op, by_col) in seen:
                self.cur.execute("delete from achievement_pending_ops where _id = ?", (op.id,))
                removed += 1
            else:
                seen.add(getattr(op, by_col))
        self.connection.commit()
        return removed

    def empty_pending_ops(self):
        self.cur.execute("delete from achievement_pending_ops")
        self.connection.commit()

    def add_pending_op(self, op: dict):
        sql = "insert into achievement_pending_ops values ({})".format(
            ",".join("?" for _ in range(len(op))))
        self.cur.execute(sql, list(op.values()))
        self.connection.commit()

    def get_next_pending_op_id(self):
        res = self.cur.execute("select max(_id) from achievement_pending_ops").fetchone()[0]
        return 0 if res is None else res + 1

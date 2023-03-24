import os
from datetime import datetime
from gpau_objects.funcs import *
from inspect import getframeinfo, stack
from typing import List, Any, Optional

class Dummy:
    input = None
    quiet = False
    secure_mode = False
    readme = False
    auto_inc_achs = False
    rem_dup_ops = False
    rem_all_ops = False

    # package
    app = None
    app_id = None

    # player
    player_id = None

    # listing
    list_cc = False
    list_games = False
    list_players = False

    # package listing
    list_achs = False
    list_nor_achs = False
    list_inc_achs = False
    list_sec_achs = False

    # searching
    search_games = None
    search_achs = None

    # unlocking
    unlock_id = None
    unlock_all = False
    unlock_listed = False

class Wrapper:
    _id = None
    _changers = {}
    _args = []

    _hidden_attrs = [
        "_changers",
        "_args",
        "_hidden_attrs"
    ]

    def __init__(self, *args):
        self._args = args

    def attrs(self):
        return [x for x in self.__dict__ if not x.startswith("__") and not x.endswith("__") and x not in self._hidden_attrs]

    def values(self):
        return [getattr(self, x) for x in self.attrs()]

    def dict(self):
        return {x: getattr(self, x) for x in self.attrs()}

    def dump(self, changers=None):
        caller = getframeinfo(stack()[1][0])
        fname, line = caller.filename, caller.lineno
        fname = os.path.relpath(fname, os.getcwd())
        inst = self.apply_changers(changers)
        vals = {x: getattr(inst, x) for x in inst.attrs()}
        dmp = "\n\t".join(f"{x} = {y}" for x, y in vals.items())
        name = self.__class__.__name__
        print(f"{fname}:{line}:{name}:\n\t{dmp}")

    @staticmethod
    def join(*args, sep=" : "):
        return sep.join(str(x) for x in args)

    @property
    def id(self):
        return self._id

    def apply_changers(self, changers=None):
        if changers is None:
            changers = list(self._changers.keys())

        d = self.dict()
        for n, f in self._changers.items():
            if n in d and n in changers:
                d[n] = f(d[n])
        return self.__class__(*list(d.values()))

class AchievementDefinition(Wrapper):
    def __init__(self, *args):
        super().__init__(*args)

        self._id = get_arg(0, args)
        self.game_id = get_arg(1, args)
        self.external_achievement_id = get_arg(2, args)
        self.type = get_arg(3, args)
        self.name = get_arg(4, args)
        self.description = get_arg(5, args)
        self.unlocked_icon_image_id = get_arg(6, args)
        self.revealed_icon_image_id = get_arg(7, args)
        self.total_steps = get_arg(8, args)
        self.formatted_total_steps = get_arg(9, args)
        self.initial_state = get_arg(10, args)
        self.sorting_rank = get_arg(11, args)
        self.definition_xp_value = get_arg(12, args)
        self.rarity_percent = get_arg(13, args)

    def is_normal(self):
        return self.type == 0

    def is_incremental(self):
        return self.type == 1

    def is_secret(self):
        return self.initial_state == 2

    def print_string(self):
        typ = "[INC" if self.is_incremental() else "[NOR"
        typ += "|SEC]" if self.is_secret() else "]"
        return self.join(typ, self.external_achievement_id, self.name, self.description, f"{self.definition_xp_value}xp")

class AchievementInstance(Wrapper):
    def __init__(self, *args):
        super().__init__(*args)

        self._changers = {
            "last_updated_timestamp": lambda x: datetime.fromtimestamp(x / 1000)
        }

        self._id = get_arg(0, args)
        self.definition_id = get_arg(1, args)
        self.player_id = get_arg(2, args)
        self.state = get_arg(3, args)
        self.current_steps = get_arg(4, args)
        self.formatted_current_steps = get_arg(5, args)
        self.last_updated_timestamp = get_arg(6, args)
        self.instance_xp_value = get_arg(7, args)

class AchievementPendingOp(Wrapper):
    def __init__(self, *args):
        super().__init__(*args)

        self._id = get_arg(0, args)
        self.client_context_id = get_arg(1, args)
        self.external_achievement_id = get_arg(2, args)
        self.achievement_type = get_arg(3, args)
        self.new_state = get_arg(4, args)
        self.steps_to_increment = get_arg(5, args)
        self.min_steps_to_set = get_arg(6, args)
        self.external_game_id = get_arg(7, args)
        self.external_player_id = get_arg(8, args)

class ClientContext(Wrapper):
    def __init__(self, *args):
        super().__init__(*args)

        self._changers = {
            "account_name": lambda x: x[0:2] + "*" * (len(x) - x.find("@") - 2) + x[x.find("@")-2:]
        }

        self._id = get_arg(0, args)
        self.package_name = get_arg(1, args)
        self.package_uid = get_arg(2, args)
        self.account_name = get_arg(3, args)
        self.account_type = get_arg(4, args)
        self.is_games_lite = get_arg(5, args)

    def print_string(self, secure=False):
        cc = self.apply_changers() if secure else self
        return self.join(cc.id, cc.package_name, cc.account_name)

class GameInstance(Wrapper):
    def __init__(self, *args):
        super().__init__(*args)

        self._id = get_arg(0, args)
        self.instance_game_id = get_arg(1, args)
        self.real_time_support = get_arg(2, args)
        self.turn_based_support = get_arg(3, args)
        self.platform_type = get_arg(4, args)
        self.instance_display_name = get_arg(5, args)
        self.package_name = get_arg(6, args)
        self.piracy_check = get_arg(7, args)
        self.installed = get_arg(8, args)
        self.preferred = get_arg(9, args)
        self.gamepad_support = get_arg(10, args)


class GamePlayerId(Wrapper):
    def __init__(self, *args):
        super().__init__(*args)

        self._id = get_arg(0, args)
        self.game_player_ids_external_player_id = get_arg(1, args)
        self.game_player_ids_external_game_id = get_arg(2, args)
        self.game_player_ids_external_game_player_id = get_arg(3, args)
        self.game_player_ids_external_primary_player_id = get_arg(4, args)
        self.game_player_ids_created_in_epoch = get_arg(5, args)


class Game(Wrapper):
    def __init__(self, *args):
        super().__init__(*args)

        self._id = get_arg(0, args)
        self.external_game_id = get_arg(1, args)
        self.display_name = get_arg(2, args)
        self.primary_category = get_arg(3, args)
        self.secondary_category = get_arg(4, args)
        self.developer_name = get_arg(5, args)
        self.game_description = get_arg(6, args)
        self.game_icon_image_id = get_arg(7, args)
        self.game_hi_res_image_id = get_arg(8, args)
        self.featured_image_id = get_arg(9, args)
        self.screenshot_image_ids = get_arg(10, args)
        self.screenshot_image_widths = get_arg(11, args)
        self.screenshot_image_heights = get_arg(12, args)
        self.video_url = get_arg(13, args)
        self.play_enabled_game = get_arg(14, args)
        self.last_played_server_time = get_arg(15, args)
        self.last_connection_local_time = get_arg(16, args)
        self.last_synced_local_time = get_arg(17, args)
        self.metadata_version = get_arg(18, args)
        self.sync_token = get_arg(19, args)
        self.metadata_sync_requested = get_arg(20, args)
        self.target_instance = get_arg(21, args)
        self.gameplay_acl_status = get_arg(22, args)
        self.availability = get_arg(23, args)
        self.owned = get_arg(24, args)
        self.achievement_total_count = get_arg(25, args)
        self.leaderboard_count = get_arg(26, args)
        self.price_micros = get_arg(27, args)
        self.formatted_price = get_arg(28, args)
        self.full_price_micros = get_arg(29, args)
        self.formatted_full_price = get_arg(30, args)
        self.explanation = get_arg(31, args)
        self.description_snippet = get_arg(32, args)
        self.starRating = get_arg(33, args)
        self.ratingsCount = get_arg(34, args)
        self.muted = get_arg(35, args)
        self.identity_sharing_confirmed = get_arg(36, args)
        self.snapshots_enabled = get_arg(37, args)
        self.theme_color = get_arg(38, args)
        self.lastUpdatedTimestampMillis = get_arg(39, args)

    def print_string(self, inst: GameInstance = None):
        middle = self.developer_name if inst is None else inst.package_name
        return self.join(self.external_game_id, middle, self.display_name)

class Image(Wrapper):
    def __init__(self, *args):
        super().__init__(*args)

        self._id = get_arg(0, args)
        self.url = get_arg(1, args)
        self.local = get_arg(2, args)
        self.filesize = get_arg(3, args)
        self.download_timestamp = get_arg(4, args)

class Player(Wrapper):
    def __init__(self, *args):
        super().__init__(*args)

        self._id = get_arg(0, args)
        self.external_player_id = get_arg(1, args)
        self.profile_name = get_arg(2, args)
        self.profile_icon_image_id = get_arg(3, args)
        self.profile_hi_res_image_id = get_arg(4, args)
        self.last_updated = get_arg(5, args)
        self.is_in_circles = get_arg(6, args)
        self.current_xp_total = get_arg(7, args)
        self.current_level = get_arg(8, args)
        self.current_level_min_xp = get_arg(9, args)
        self.current_level_max_xp = get_arg(10, args)
        self.next_level = get_arg(11, args)
        self.next_level_max_xp = get_arg(12, args)
        self.last_level_up_timestamp = get_arg(13, args)
        self.player_title = get_arg(14, args)
        self.has_all_public_acls = get_arg(15, args)
        self.has_debug_access = get_arg(16, args)
        self.is_profile_visible = get_arg(17, args)
        self.most_recent_activity_timestamp = get_arg(18, args)
        self.most_recent_external_game_id = get_arg(19, args)
        self.most_recent_game_name = get_arg(20, args)
        self.most_recent_game_icon_id = get_arg(21, args)
        self.most_recent_game_hi_res_id = get_arg(22, args)
        self.most_recent_game_featured_id = get_arg(23, args)
        self.gamer_tag = get_arg(24, args)
        self.real_name = get_arg(25, args)
        self.banner_image_landscape_id = get_arg(26, args)
        self.banner_image_portrait_id = get_arg(27, args)
        self.total_unlocked_achievements = get_arg(28, args)
        self.play_together_friend_status = get_arg(29, args)
        self.play_together_nickname = get_arg(30, args)
        self.play_together_invitation_nickname = get_arg(31, args)
        self.profile_creation_timestamp = get_arg(32, args)
        self.nickname_abuse_report_token = get_arg(33, args)
        self.friends_list_visibility = get_arg(34, args)
        self.always_auto_sign_in = get_arg(35, args)

    def print_string(self):
        return self.join(self.external_player_id, self.profile_name, f"Level {self.current_level}")


class Finder:
    def __init__(self, db_instance):
        from gpau_objects.dbfile import DbFile
        self.db: DbFile = db_instance

    def ach_def_by_id(self, x: Any) -> Optional[AchievementDefinition]:
        return self.db.select_by_cls_fe(AchievementDefinition, ["_id"], [x])

    def ach_def_by_external_id(self, x: Any) -> Optional[AchievementDefinition]:
        return self.db.select_by_cls_fe(AchievementDefinition, ["external_achievement_id"], [x])

    def ach_inst_by_id(self, x: Any) -> Optional[AchievementInstance]:
        return self.db.select_by_cls_fe(AchievementInstance, ["_id"], [x])

    def client_context_by_id(self, x: Any) -> Optional[ClientContext]:
        return self.db.select_by_cls_fe(ClientContext, ["_id"], [x])

    def game_inst_by_id(self, x: Any) -> Optional[GameInstance]:
        return self.db.select_by_cls_fe(GameInstance, ["_id"], [x])

    def game_player_id_by_id(self, x: Any) -> Optional[GamePlayerId]:
        return self.db.select_by_cls_fe(GamePlayerId, ["_id"], [x])

    def game_by_id(self, x: Any) -> Optional[Game]:
        return self.db.select_by_cls_fe(Game, ["_id"], [x])

    def image_by_id(self, x: Any) -> Optional[Image]:
        return self.db.select_by_cls_fe(Image, ["_id"], [x])

    def ach_def_by_ach_inst(self, x: AchievementInstance) -> Optional[AchievementDefinition]:
        return self.db.select_by_cls_fe(AchievementDefinition, ["_id"], [x.definition_id])

    def ach_defs_by_ach_insts(self, x: List[AchievementInstance]) -> List[Optional[AchievementDefinition]]:
        return [self.ach_def_by_ach_inst(y) for y in x]

    def game_inst_by_game(self, x: Game) -> Optional[GameInstance]:
        return self.db.select_by_cls_fe(GameInstance, ["instance_game_id"], [x.id])

    def game_insts_by_games(self, x: List[Game]) -> List[Optional[GameInstance]]:
        return [self.game_inst_by_game(y) for y in x]

    def game_inst_by_game_id(self, x: Any) -> Optional[GameInstance]:
        return self.db.select_by_cls_fe(GameInstance, ["instance_game_id"], [x])

    def game_inst_by_package_name(self, x: str) -> Optional[GameInstance]:
        return self.db.select_by_cls_fe(GameInstance, ["package_name"], [x])

    def game_by_game_inst(self, x: GameInstance) -> Optional[Game]:
        return self.db.select_by_cls_fe(Game, ["_id"], [x.instance_game_id])

    def game_by_external_id(self, x: Any) -> Optional[Game]:
        return self.db.select_by_cls_fe(Game, ["external_game_id"], [x])

    def game_by_ach_inst(self, x: AchievementInstance) -> Optional[Game]:
        udef = self.ach_def_by_ach_inst(x)
        if udef:
            return self.db.select_by_cls_fe(Game, ["_id"], [udef.game_id])
        return None

    def game_by_name(self, search: Any) -> Optional[Game]:
        return self.db.search_by_cls_fe(search, cls=Game)

    def games_by_name(self, search: Any) -> List[Game]:
        return self.db.search_by_cls(search, cls=Game, exact=True)

    def game_by_ach_def(self, x: AchievementDefinition) -> Optional[Game]:
        return self.db.select_by_cls_fe(Game, ["_id"], [x.game_id])

    def games_by_ach_defs(self, x: List[AchievementDefinition]) -> List[Optional[Game]]:
        return [self.game_by_ach_def(y) for y in x]

    def ach_defs_by_game_id(self, x: Any) -> List[Optional[AchievementDefinition]]:
        return self.db.select_by_cls(AchievementDefinition, ["game_id"], [x], exact=True)

    def ach_defs_by_game(self, x: Game) -> List[Optional[AchievementDefinition]]:
        return self.ach_defs_by_game_id(x.id)

    def ach_inst_by_ach_def(self, x: AchievementDefinition) -> Optional[AchievementInstance]:
        return self.db.select_by_cls_fe(AchievementInstance, ["definition_id"], [x.id])

    def ach_insts_by_ach_defs(self, x: List[AchievementDefinition]) -> List[Optional[AchievementInstance]]:
        return [self.ach_inst_by_ach_def(y) for y in x]

    def ach_insts_by_game_id(self, x: Any) -> List[Optional[AchievementInstance]]:
        ugame = self.game_by_id(x)
        if ugame:
            udefs = self.ach_defs_by_game(ugame)
            if udefs:
                return self.ach_insts_by_ach_defs(udefs)
        return []

    def ach_insts_by_game(self, x: Game) -> List[Optional[AchievementInstance]]:
        return self.ach_insts_by_game_id(x.id)

    def client_context_by_game_inst(self, x: GameInstance) -> Optional[ClientContext]:
        return self.db.select_by_cls_fe(ClientContext, ["package_name"], [x.package_name])

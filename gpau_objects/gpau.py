import glob
import traceback
import sqlite3 as sql
from gpau_objects.structure import *
from gpau_objects.dbfile import DbFile
from gpau_objects.funcs import *

class GooglePlayAchievementUnlocker:
    default_db_regex = "/data/data/com.google.android.gms/databases/games_*.db"
    # default_db_regex = "dbs/games_*.db"

    def __init__(self, a):
        self.args: Dummy = a
        self.db: Optional[DbFile] = None
        self.finder: Optional[Finder] = None
        self.quiet_mode_inc_achs = False
        self.reload()

    def get_db_files(self):
        return glob.glob(self.default_db_regex)

    def load_db_file(self, file=None):
        if file is None:
            file = self.get_db_files()[0]

        errors = []

        if not os.path.isfile(file):
            errors.append("Input is not a file")
        if not os.access(file, os.R_OK):
            errors.append("Input is not readable")

        try:
            self.db = DbFile(sql.connect(file))
            self.finder = Finder(self.db)
        except Exception:
            errors.append(traceback.format_exc())

        return errors

    def reload(self):
        self.check_player()

        if self.args.input is None:
            files = self.get_db_files()
            if len(files) == 0:
                self.ptx("No database file found")
            self.args.input = files[0]

        errors = self.load_db_file(self.args.input)

        if errors:
            self.ptx("\n".join(errors))

    def pt(self, msg, _ex=False):
        if not self.args.quiet_mode:
            if _ex:
                ex(msg)
                return
            print(msg)

    def ptx(self, msg):
        self.pt(msg, _ex=True)

    def run(self):
        if self.args.readme:
            ex("""
HOW TO USE?
1) Disconnect from the internet
2) Unlock the achievements you want
3) Reconnect to the internet
4) Run Google Play Games to sync the achievements
5) Profit

ACHIEVEMENT FLAGS?
NOR - normal
INC - incremental
SEC - secret

GAME WON'T APPEAR IN --list-cc? Try one of these:
1) Play the game for a couple of minutes
2) In-app button to logout and login again
3) Earn any achievement
4) Re/Open Google Play App
5) Clear Cache/All data and login again
6) Restart phone\n""")

        try:
            if self.args.rem_all_ops:
                self.pt("Removing all pending achievement ops...")
                self.db.empty_pending_ops()

            achs: List[AchievementDefinition] = []

            if self.args.list_cc:
                ccs = self.db.select(cls=ClientContext)
                print("\n".join([x.print_string() for x in ccs]))
            elif self.args.list_games:
                games = self.db.select(cls=Game)
                game_insts = [self.finder.game_inst_by_game(x) for x in games]
                print("\n".join([g.print_string(gi) for g, gi in zip(games, game_insts) if gi]))
            elif self.args.list_players:
                self.list_players()

            if self.args.list_achs:
                package = self.get_app()
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(package.id)]
                achs = ach_defs
            elif self.args.list_u_achs:
                package = self.get_app()
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(package.id) if x.is_unlocked()]
                achs = self.finder.ach_defs_by_ach_insts(ach_insts)
            elif self.args.list_nu_achs:
                package = self.get_app()
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(package.id) if x.is_locked()]
                achs = self.finder.ach_defs_by_ach_insts(ach_insts)
            elif self.args.list_nor_achs:
                package = self.get_app()
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(package.id) if x.is_normal()]
                achs = ach_defs
            elif self.args.list_inc_achs:
                package = self.get_app()
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(package.id) if x.is_incremental()]
                achs = ach_defs
            elif self.args.list_sec_achs:
                package = self.get_app()
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(package.id) if x.is_secret()]
                achs = ach_defs

            opt_pkg = self.get_app(optional=True)

            if self.args.search_games:
                search = self.args.search_games[0]
                found_games = self.db.search(search, cls=Game)
                print("\n".join([x.print_string(self.finder.game_inst_by_game(x)) for x in found_games]))
            elif self.args.search_achs:
                achs = self.find_achievements(self.args.search_achs[0], opt_pkg)
            elif self.args.search_u_achs:
                achs = self.find_achievements(self.args.search_u_achs[0], opt_pkg, locked=False)
            elif self.args.search_nu_achs:
                achs = self.find_achievements(self.args.search_nu_achs[0], opt_pkg, unlocked=False)
            elif self.args.search_nor_achs:
                achs = self.find_achievements(self.args.search_nor_achs[0], opt_pkg, inc=False, sec=False)
            elif self.args.search_inc_achs:
                achs = self.find_achievements(self.args.search_inc_achs[0], opt_pkg, nor=False, sec=False)
            elif self.args.search_sec_achs:
                achs = self.find_achievements(self.args.search_sec_achs[0], opt_pkg, nor=False, inc=False)

            if len(achs):
                print("\n".join([x.print_string() for x in achs]))

            if self.args.unlock_id:
                self.unlock_achievement(self.finder.ach_def_by_external_id(self.args.unlock_id[0]))
            elif self.args.unlock_all:
                ach_insts = self.finder.ach_insts_by_game_id(self.get_app().id)
                for ach_inst in ach_insts:
                    self.unlock_achievement(self.finder.ach_def_by_ach_inst(ach_inst))
            elif self.args.unlock_listed:
                for ach in achs:
                    self.unlock_achievement(ach)

            if self.args.rem_dup_ops:
                self.pt("Removing duplicate pending achievement ops...")
                removed = self.db.remove_duplicate_pending_ops()
                self.pt(f"Removed: {removed}")

        except Exception:
            ex(f"{traceback.format_exc()}\nSomething bad has happened, probably a bug or uncut edge case.\nPlease report this to the developer.")

    def unlock_achievement(self, ach_def: AchievementDefinition = None):
        if ach_def is None:
            return

        ach_inst = self.finder.ach_inst_by_ach_def(ach_def)
        if ach_inst is None:
            self.ptx("Achievement definition doesn't have an associated achievement instance")
        if ach_inst.is_unlocked():
            self.pt(f"Achievement {ach_def.external_achievement_id} is already unlocked...")
            return

        game = self.finder.game_by_ach_inst(ach_inst)
        game_inst = self.finder.game_inst_by_game(game)
        client_context = self.finder.client_context_by_game_inst(game_inst)

        if not client_context:
            self.ptx("No client context found for this game")

        self.pt(f"Unlocking achievement {ach_def.external_achievement_id} ({game_inst.package_name})...")

        steps_to_increment = ""
        if ach_def.is_incremental():
            if self.args.auto_inc_achs:
                steps_to_increment = ach_def.total_steps - ach_inst.current_steps
            else:
                if not self.quiet_mode_inc_achs and self.args.quiet_mode:
                    ex("Setting incremental achievements can't be used with quiet mode flag (-q)\nIf you want to automatically set incremental achievements use flag --auto-inc-achs", _ex=False)
                    self.quiet_mode_inc_achs = True
                print(f"### {ach_def.name} | {ach_def.description} | {ach_def.definition_xp_value}xp")
                print(f"### Progress: {ach_inst.current_steps}/{ach_def.total_steps}")
                steps_to_increment = self.get_increment_value()

        self.db.add_pending_op({
            "_id": self.db.get_next_pending_op_id(),
            "client_context_id": client_context.id,
            "external_achievement_id": ach_def.external_achievement_id,
            "achievement_type": ach_def.type,
            "new_state": 0,
            "steps_to_increment": steps_to_increment,
            "min_steps_to_set": "",
            "external_game_id": game.external_game_id,
            "external_player_id": self.get_player_id(),
        })

    def get_increment_value(self):
        print(end='\r')
        value = input("### Steps to increment by: ")
        try:
            value = int(value)
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            ex("Value must be a number bigger than -1", _ex=False)
            return self.get_increment_value()

    def find_achievements(self, search, package=None, unlocked=True, locked=True, nor=True, inc=True, sec=True) -> List[AchievementDefinition]:
        achs = self.finder.ach_defs_by_game(package) if package else self.db.select(cls=AchievementDefinition)
        found_achs = self.db.search_instances_by(search, ["name", "description"], achs)
        ach_insts = self.finder.ach_insts_by_ach_defs(found_achs)

        ach_defs_filtered = [
            x for x, w in zip(found_achs, ach_insts)
            if (w.is_unlocked() and unlocked) or (w.is_locked() and locked)
        ]

        ach_defs_filtered = [
            x for x in ach_defs_filtered
            if (x.is_normal() and nor) or (x.is_incremental() and inc) or (x.is_secret() and sec)
        ]

        return ach_defs_filtered

    def get_player_id(self):
        players: List[Player] = self.db.select(cls=Player)
        if not players:
            self.ptx("Couldn't find any player")
        return players[0].external_player_id

    def list_players(self):
        players = self.get_players()

        index = 1
        for db_file, db_player in players.items():
            file_name = os.path.basename(db_file)
            self.pt(f"[{index}] ({file_name}) {db_player.print_string()}")
            index += 1

    def get_players(self):
        current_db_file = self.args.input

        players = {}
        for db_file in self.get_db_files():
            errors = self.load_db_file(db_file)

            if not errors:
                db_players = self.db.select(cls=Player)

                if db_players:
                    players[db_file] = db_players[0]

        # load back the original db file
        self.load_db_file(current_db_file)

        return players

    def check_player(self):
        player = self.args.player

        if player is None:
            return

        db_players = self.get_players()

        try:
            player = int(player)

            if player < 1 or player > len(db_players):
                raise ValueError
        except ValueError:
            self.ptx(f"Player must be a number from 1 to {len(db_players)}")

        self.args.input = list(db_players.keys())[player - 1]

    def get_app(self, optional=False) -> Optional[Game]:
        if self.args.app is None and self.args.app_id is None:
            if optional:
                return None
            self.ptx("No package specified (use -a or -aid)")

        if self.args.app is not None:
            app = self.finder.game_inst_by_package_name(self.args.app)
            if not app:
                if optional:
                    return None
                self.ptx("Package not found")
            return self.finder.game_by_game_inst(app)

        app = self.finder.game_by_external_id(self.args.app_id)
        if not app:
            if optional:
                return None
            self.ptx("Package not found")
        return app

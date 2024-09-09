import os
import glob
import traceback
import sqlite3 as sql
from gpau_objects.structure import *
from gpau_objects.common import *
from gpau_objects.dbfile import DbFile

class GooglePlayAchievementUnlocker:
    default_db_regex = "/data/data/com.google.android.gms/databases/games_*.db"
    # default_db_regex = "dbs/games_*.db"

    readme_text = """
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
6) Restart phone\n"""

    def __init__(self, a):
        self.args: Dummy = a
        self.inst_db: Optional[DbFile] = None
        self.inst_finder: Optional[Finder] = None
        self.reload()

    @property
    def db(self) -> DbFile:
        assert self.inst_db is not None, "Database not loaded"
        return self.inst_db
    
    @property
    def finder(self) -> Finder:
        assert self.inst_finder is not None, "Finder not loaded"
        return self.inst_finder
    
    def get_db_files(self):
        return glob.glob(self.default_db_regex)

    def reload(self):
        self.check_player()

        if self.args.input is None:
            files = self.get_db_files()
            if len(files) == 0:
                Logger.error_exit("No database file found")
            self.args.input = files[0]

        errors = self.load_db_file(self.args.input)

        if errors:
            Logger.error_exit("\n".join(errors))

    def load_db_file(self, file=None):
        if file is None:
            file = self.get_db_files()[0]

        errors = []

        if not os.path.isfile(file):
            errors.append("Input is not a file")
        if not os.access(file, os.R_OK):
            errors.append("Input is not readable")

        try:
            self.inst_db = DbFile(sql.connect(file))
            self.inst_finder = Finder(self.db)
        except Exception:
            errors.append(traceback.format_exc())

        return errors

    def run(self):
        if self.args.readme:
            Logger.error_exit(self.readme_text)

        try:
            if self.args.rem_all_ops:
                Logger.info("Removing all pending achievement ops...")
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
            elif self.args.list_ops:
                ops: List[AchievementPendingOp] = [x for x in self.db.select(cls=AchievementPendingOp) if x]
                print("\n".join([x.print_string() for x in ops]))

            if self.args.list_achs:
                app = self.get_app()
                assert app is not None, "Package not found"
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(app.id) if x]
                achs = ach_defs
            elif self.args.list_u_achs:
                app = self.get_app()
                assert app is not None, "Package not found"
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(app.id) if x and x.is_unlocked()]
                achs = [x for x in self.finder.ach_defs_by_ach_insts(ach_insts) if x]
            elif self.args.list_nu_achs:
                app = self.get_app()
                assert app is not None, "Package not found"
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(app.id) if x and x.is_locked()]
                achs = [x for x in self.finder.ach_defs_by_ach_insts(ach_insts) if x]
            elif self.args.list_nor_achs:
                app = self.get_app()
                assert app is not None, "Package not found"
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(app.id) if x and x.is_normal()]
                achs = ach_defs
            elif self.args.list_inc_achs:
                app = self.get_app()
                assert app is not None, "Package not found"
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(app.id) if x and x.is_incremental()]
                achs = ach_defs
            elif self.args.list_sec_achs:
                app = self.get_app()
                assert app is not None, "Package not found"
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(app.id) if x and x.is_secret()]
                achs = ach_defs

            opt_app = self.get_app(optional=True)

            if self.args.search_games:
                search = self.args.search_games[0]
                found_games: List[Game] = self.db.search(search, cls=Game)
                print("\n".join([x.print_string(self.finder.game_inst_by_game(x)) for x in found_games]))
            elif self.args.search_achs:
                achs = self.find_achievements(self.args.search_achs[0], opt_app)
            elif self.args.search_u_achs:
                achs = self.find_achievements(self.args.search_u_achs[0], opt_app, locked=False)
            elif self.args.search_nu_achs:
                achs = self.find_achievements(self.args.search_nu_achs[0], opt_app, unlocked=False)
            elif self.args.search_nor_achs:
                achs = self.find_achievements(self.args.search_nor_achs[0], opt_app, inc=False, sec=False)
            elif self.args.search_inc_achs:
                achs = self.find_achievements(self.args.search_inc_achs[0], opt_app, nor=False, sec=False)
            elif self.args.search_sec_achs:
                achs = self.find_achievements(self.args.search_sec_achs[0], opt_app, nor=False, inc=False)

            if len(achs):
                print("\n".join([x.print_string() for x in achs]))

            if self.args.unlock_id:
                self.unlock_achievement(self.finder.ach_def_by_external_id(self.args.unlock_id[0]))
            elif self.args.unlock_all:
                app = self.get_app()
                assert app is not None, "Package not found"
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(app.id) if x]
                for ach_inst in ach_insts:
                    self.unlock_achievement(self.finder.ach_def_by_ach_inst(ach_inst))
            elif self.args.unlock_listed:
                for ach in achs:
                    self.unlock_achievement(ach)

            if self.args.rem_dup_ops:
                Logger.info("Removing duplicate pending achievement ops...")
                removed = self.db.remove_duplicate_pending_ops()
                Logger.info(f"Removed: {removed}")

        except Exception:
            Logger.error_exit(f"{traceback.format_exc()}\nSomething bad has happened, probably a bug or uncut edge case.\nPlease report this to the developer.")

    def unlock_achievement(self, ach_def: Optional[AchievementDefinition]=None):
        if ach_def is None:
            return

        ach_inst = self.finder.ach_inst_by_ach_def(ach_def)
        if ach_inst is None:
            Logger.error("Achievement definition doesn't have an associated achievement instance")
            return
        
        if ach_inst.is_unlocked():
            Logger.info(f"Achievement {ach_def.external_achievement_id} is already unlocked...")
            return

        game = self.finder.game_by_ach_inst(ach_inst)
        assert game is not None, "Game not found"
        game_inst = None if not game else self.finder.game_inst_by_game(game)
        client_context = None if not game_inst else self.finder.client_context_by_game_inst(game_inst)

        if not client_context:
            Logger.error("No client context found for this game")
            return

        package_name = "NO_INSTANCE" if not game_inst else game_inst.package_name
        Logger.info(f"Unlocking achievement {ach_def.external_achievement_id} ({package_name})...")

        steps_to_increment = ""
        if ach_def.is_incremental():
            if self.args.auto_inc_achs:
                steps_to_increment = ach_def.total_steps - ach_inst.current_steps
            else:
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
            if int(value) < 0:
                raise ValueError
            return value
        except ValueError:
            Logger.error("Value must be a number bigger than -1")
            return self.get_increment_value()

    def find_achievements(self, search, package=None, unlocked=True, locked=True, nor=True, inc=True, sec=True) -> List[AchievementDefinition]:
        achs = self.finder.ach_defs_by_game(package) if package else self.db.select(cls=AchievementDefinition)
        found_achs: List[AchievementDefinition] = self.db.search_instances_by(search, ["name", "description"], achs)

        ach_insts = self.finder.ach_insts_by_ach_defs(found_achs)

        ach_defs_filtered = [
            x for x, w in zip(found_achs, ach_insts)
            if (w and w.is_unlocked() and unlocked) or (w and w.is_locked() and locked)
        ]

        ach_defs_filtered = [
            x for x in ach_defs_filtered
            if (x.is_normal() and nor) or (x.is_incremental() and inc) or (x.is_secret() and sec)
        ]

        return ach_defs_filtered

    def get_player_id(self):
        players: List[Player] = self.db.select(cls=Player)
        if not players:
            Logger.error_exit("Couldn't find any player")
        return players[0].external_player_id

    def list_players(self):
        players = self.get_players()

        index = 1
        for db_file, db_player in players.items():
            file_name = os.path.basename(db_file)
            print(f"[{index}] ({file_name}) {db_player.print_string()}")
            index += 1

    def get_players(self) -> Dict[str, Player]:
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
            ip = int(player)

            if ip < 1 or ip > len(db_players):
                raise ValueError
            
            self.args.input = list(db_players.keys())[ip - 1]
        except ValueError:
            Logger.error_exit(f"Player must be a number from 1 to {len(db_players)}")

    def get_app(self, optional=False) -> Optional[Game]:
        if self.args.app is None and self.args.app_id is None:
            if optional:
                return None
            Logger.error_exit("No package specified (use -a or -aid)")

        if self.args.app is not None:
            app_inst = self.finder.game_inst_by_package_name(self.args.app)
            
            if not app_inst:
                if optional:
                    return None
                Logger.error_exit("Package not found")

            if app_inst:
                return self.finder.game_by_game_inst(app_inst)
            
        app = self.finder.game_by_external_id(self.args.app_id)
        
        if not app:
            if optional:
                return None
            Logger.error_exit("Package not found")
        
        return app

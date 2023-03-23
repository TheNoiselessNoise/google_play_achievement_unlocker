import glob
import traceback
import sqlite3 as sql
from gpau_objects.structure import *
from gpau_objects.dbfile import DbFile
from gpau_objects.funcs import *

class GooglePlayAchievementUnlocker:
    default_db_regex = "/data/data/com.google.android.gms/databases/games_*.db"

    def __init__(self, a):
        self.args: Dummy = a
        self.db: Optional[DbFile] = None
        self.finder: Optional[Finder] = None

        if self.args.input is None:
            if not self.args.quiet:
                print('No input specified, trying to find default database...')
            files = glob.glob(self.default_db_regex)
            if len(files) == 0:
                ex("No database file found\n" if not self.args.quiet else "")
            if not os.access(files[0], os.R_OK) and not self.args.quiet:
                ex("Found database file, but can't read it\n" if not self.args.quiet else "")
            if not self.args.quiet:
                print(f"Using database file: {files[0]}")
            self.db = DbFile(sql.connect(files[0]))
        else:
            if not os.path.isfile(self.args.input):
                ex('Input is not a file\n')
            if not os.access(self.args.input, os.R_OK):
                ex('Input is not readable\n')
            self.db = DbFile(sql.connect(self.args.input))

        self.finder = Finder(self.db)

    def run(self):
        if self.args.readme:
            ex(f"""
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
                if not self.args.quiet:
                    print('Removing all pending achievement ops...')
                self.db.empty_pending_ops()

            found_achievements = []
            if self.args.list_cc:
                ccs = self.db.select(cls=ClientContext)
                print('\n'.join([x.print_string(self.args.secure_mode) for x in ccs]))
            elif self.args.list_games:
                games = self.db.select(cls=Game)
                game_insts = [self.finder.game_inst_by_game(x) for x in games]
                print('\n'.join([g.print_string(gi) for g, gi in zip(games, game_insts) if gi]))
            elif self.args.list_players:
                players = self.db.select(cls=Player)
                print('\n'.join([x.print_string() for x in players]))

            if self.args.list_achs:
                package = self.get_app()
                ach_insts = self.finder.ach_insts_by_game_id(package.id)
                found_achievements = self.finder.ach_defs_by_ach_insts(ach_insts)
                print('\n'.join([self.finder.ach_def_by_ach_inst(x).print_string(x) for x in ach_insts]))
            elif self.args.list_nor_achs:
                package = self.get_app()
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(package.id) if x.type == 0]
                found_achievements = ach_defs
                print('\n'.join([x.print_string(self.finder.ach_inst_by_ach_def(x)) for x in ach_defs]))
            elif self.args.list_inc_achs:
                package = self.get_app()
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(package.id) if x.type == 1]
                found_achievements = ach_defs
                print('\n'.join([x.print_string(self.finder.ach_inst_by_ach_def(x)) for x in ach_defs]))
            elif self.args.list_sec_achs:
                package = self.get_app()
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(package.id) if x.state == 2]
                found_achievements = self.finder.ach_defs_by_ach_insts(ach_insts)
                print('\n'.join([self.finder.ach_def_by_ach_inst(x).print_string(x) for x in ach_insts]))

            if self.args.search_games:
                search = self.args.search_games[0]
                found_games = self.db.search(search, cls=Game)
                print('\n'.join([x.print_string(self.finder.game_inst_by_game(x)) for x in found_games]))
            elif self.args.search_achs:
                package = self.get_app(optional=True)
                search = self.args.search_achs[0]
                found_achievements = self.find_achievements(search, package)

            if self.args.unlock_id:
                self.unlock_achievement(self.finder.ach_def_by_external_id(self.args.unlock_id[0]))
            elif self.args.unlock_all:
                package = self.get_app()
                ach_insts = self.finder.ach_insts_by_game_id(package.id)
                for ach_inst in ach_insts:
                    self.unlock_achievement(self.finder.ach_def_by_ach_inst(ach_inst))
            elif self.args.unlock_listed:
                for ach in found_achievements:
                    self.unlock_achievement(ach)

            if self.args.rem_dup_ops:
                if not self.args.quiet:
                    print('Removing duplicate pending achievement ops...')
                removed = self.db.remove_duplicate_pending_ops()
                if not self.args.quiet:
                    print(f'Removed: {removed}')

        except Exception:
            ex(f"{traceback.format_exc()}\nSomething bad has happened, probably a bug or uncut edge case.\nPlease report this to the developer.\n")

    def unlock_achievement(self, ach_def: AchievementDefinition = None):
        # ach_inst = self.finder.ach_inst_by_ach_def(ach_def)
        # if ach_def.type == 1 and not self.args.auto_inc_achs:
        #     print("-->", ach_def.print_string(ach_inst))
        #     print("Value:", self.get_increment_value(ach_def, ach_inst))

        if ach_def is None:
            return
        ach_inst = self.finder.ach_inst_by_ach_def(ach_def)
        game = self.finder.game_by_ach_inst(ach_inst)
        game_inst = self.finder.game_inst_by_game(game)
        client_context = self.finder.client_context_by_game_inst(game_inst)
        if not client_context:
            ex('No client context found for this game\n' if not self.args.quiet else "")
        if ach_inst.state is None:
            if not self.args.quiet:
                print(f"Achievement {ach_def.id} is already unlocked...")
            return
        if not self.args.quiet:
            print(f"Unlocking achievement {ach_def.external_achievement_id} ({game_inst.package_name})...")

        steps_to_increment = ''
        if ach_def.type == 1:
            if self.args.auto_inc_achs:
                steps_to_increment = ach_def.total_steps - ach_inst.current_steps
            else:
                steps_to_increment = self.get_increment_value(ach_def, ach_inst)

        self.db.add_pending_op({
            '_id': self.db.get_next_pending_op_id(),
            'client_context_id': client_context.id,
            'external_achievement_id': ach_def.external_achievement_id,
            'achievement_type': ach_def.type,
            'new_state': 0,
            'steps_to_increment': steps_to_increment,
            'min_steps_to_set': '',
            'external_game_id': game.external_game_id,
            'external_player_id': self.get_player_id(),
        })

    def get_increment_value(self, ach_def: AchievementDefinition, ach_inst: AchievementInstance):
        print(end='\r')
        current = ach_inst.current_steps
        total = ach_def.total_steps
        value = input(f"Achievement is incremental, current: {current}, total: {total}?\n")
        try:
            value = int(value)
            if value < 0:
                print("Value must be positive")
                raise ValueError
            return value
        except ValueError:
            return self.get_increment_value(ach_def, ach_inst)

    def find_achievements(self, search, package=None, unlocked=True, locked=True):
        achs = self.finder.ach_defs_by_game(package) if package else self.db.select(cls=AchievementDefinition)
        found_achs = self.db.search_instances_by(search, ["name", "description"], achs)
        ach_insts = self.finder.ach_insts_by_ach_defs(found_achs)
        if package is None:
            games = self.finder.games_by_ach_defs(found_achs)
            game_insts = self.finder.game_insts_by_games(games)
            print('\n'.join([
                Wrapper.join(y.external_game_id, y.display_name, z.package_name, x.print_string(w))
                for x, y, z, w in zip(found_achs, games, game_insts, ach_insts)
                if (w.state is None and unlocked) or (w.state is not None and locked)]))
        else:
            print('\n'.join([x.print_string(w) for x, w in zip(found_achs, ach_insts)]))
        return found_achs

    def get_player_id(self):
        if self.args.player_id:
            return self.args.player_id[0]
        players: List[Player] = self.db.select(cls=Player)
        if not players:
            ex("Couldn't find any player")
        return players[0].external_player_id

    def get_app(self, optional=False) -> Optional[Game]:
        if self.args.app is None and self.args.app_id is None:
            if optional:
                return None
            ex('No package specified (use -a or -aid)\n')

        if self.args.app is not None:
            app = self.finder.game_inst_by_package_name(self.args.app)
            if not app:
                if optional:
                    return None
                ex('Package not found\n')
            return self.finder.game_by_game_inst(app)

        app = self.finder.game_by_external_id(self.args.app_id)
        if not app:
            if optional:
                return None
            ex('Package not found\n')
        return app

import os
import sys
import glob
import argparse
import sqlite3 as sql
from db_objs import DbFile, Finder, Wrapper, AchievementDefinition

parser = argparse.ArgumentParser(epilog="By @TheNoiselessNoise")
parser.add_argument('-i', dest='input', metavar='input', help='path to the .db file')
parser.add_argument('-q', dest='quiet', action='store_true', help='quiet mode')
parser.add_argument('-sm', dest='secure_mode', action='store_true', help='secure mode')
parser.add_argument('--readme', dest='readme', action='store_true', help='How to use this?')
parser.add_argument('--auto-inc-achs', dest='auto_inc_achs', action='store_true', help='Automatically set the incremental achievements to max')
parser.add_argument('--rem-dup-ops', dest='rem_dup_ops', action='store_true', help='Remove duplicate achievement pending ops')
parser.add_argument('--rem-all-ops', dest='rem_all_ops', action='store_true', help='Remove all achievement pending ops')
package_group = parser.add_mutually_exclusive_group()
package_group.add_argument('-a', dest='app', metavar='app_name', help='app name')
package_group.add_argument('-aid', dest='app_id', metavar='app_id', help='app id')
player_group = parser.add_mutually_exclusive_group()
player_group.add_argument('-pid', dest='player_id', metavar='player_id', help='external player id')
list_group = parser.add_argument_group()
list_group.add_argument('--list-cc', action='store_true', help='list all client contexts')
list_group.add_argument('--list-games', action='store_true', help='list all games')
list_group.add_argument('--list-players', action='store_true', help='list all players')
package_list_group = parser.add_argument_group()
package_list_group.add_argument('--list-achs', action='store_true', help='list all achievements')
package_list_group.add_argument('--list-u-achs', action='store_true', help='list all unlocked achievements')
package_list_group.add_argument('--list-nu-achs', action='store_true', help='list all not unlocked achievements')
package_list_group.add_argument('--list-nor-achs', action='store_true', help='list all normal achievements')
package_list_group.add_argument('--list-inc-achs', action='store_true', help='list all incremental achievements')
package_list_group.add_argument('--list-sec-achs', action='store_true', help='list all secret achievements')
search_group = parser.add_argument_group()
search_group.add_argument('--search-games', metavar='search', type=str, nargs=1, help='search for a game by input')
search_group.add_argument('--search-achs', metavar='search', type=str, nargs=1, help='search for an achievements by input')
search_group.add_argument('--search-u-achs', metavar='search', type=str, nargs=1, help='search for unlocked achievements by input')
search_group.add_argument('--search-nu-achs', metavar='search', type=str, nargs=1, help='search for not unlocked achievements by input')
unlock_group = parser.add_mutually_exclusive_group()
unlock_group.add_argument('--unlock-id', dest='unlock_id', metavar='external_id', type=str, nargs=1, help='unlocks an achievement by its external id')
unlock_group.add_argument('--unlock-all', dest='unlock_all', action='store_true', help='unlocks all achievements in given package')
unlock_group.add_argument('--unlock-listed', dest='unlock_listed', action='store_true', help='unlocks all listed achievements')
args = parser.parse_args()

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
    list_u_achs = False
    list_nu_achs = False
    list_nor_achs = False
    list_inc_achs = False
    list_sec_achs = False

    # searching
    search_games = None
    search_achs = None
    search_u_achs = None
    search_nu_achs = None

    # unlocking
    unlock_id = None
    unlock_all = False
    unlock_listed = False

def ex(msg, _ex=True):
    sys.stderr.write(msg)
    if _ex:
        sys.exit(1)

class GooglePlayAchievementUnlocker:
    default_db_regex = "/data/data/com.google.android.gms/databases/games_*.db"

    def __init__(self, a):
        self.args: Dummy = a

        if self.args.readme:
            ex(f"""
1) Disconnect from the internet
2) Unlock the achievements you want
3) Reconnect to the internet
4) Run Google Play Games to sync the achievements
5) Profit\n""")

        try:
            if self.args.input is None:
                if not self.args.quiet:
                    print('No input specified, trying to find default database...')
                files = glob.glob(self.default_db_regex)
                if len(files) == 0:
                    ex("No database file found" if not self.args.quiet else "")
                if not os.access(files[0], os.R_OK) and not self.args.quiet:
                    ex("Found database file, but can't read it" if not self.args.quiet else "")
                if not self.args.quiet:
                    print(f"Using database file: {files[0]}")
                self.db = DbFile(sql.connect(files[0]))
            else:
                if not os.path.isfile(self.args.input):
                    ex('Input is not a file')
                if not os.access(self.args.input, os.R_OK):
                    ex('Input is not readable')
                self.db = DbFile(sql.connect(self.args.input))

            self.finder = Finder(self.db)

            if self.args.rem_all_ops:
                if not self.args.quiet:
                    print('Removing all pending achievement ops...')
                self.db.empty_pending_ops()

            found_achievements = []
            if self.args.list_cc:
                print('\n'.join([x.print_string(self.args.secure_mode) for x in self.db.client_contexts]))
            elif self.args.list_games:
                print('\n'.join([x.print_string(self.finder.game_inst_by_game(x)) for x in self.db.games]))
            elif self.args.list_players:
                print('\n'.join([x.print_string() for x in self.db.players]))
            elif self.args.list_achs:
                package = self.get_app()
                ach_insts = self.finder.ach_insts_by_game_id(package.id)
                found_achievements = self.finder.ach_defs_by_ach_insts(ach_insts)
                print('\n'.join([self.finder.ach_def_by_ach_inst(x).print_string() for x in ach_insts]))
            elif self.args.list_u_achs:
                package = self.get_app()
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(package.id) if x.state is None]
                found_achievements = self.finder.ach_defs_by_ach_insts(ach_insts)
                print('\n'.join([self.finder.ach_def_by_ach_inst(x).print_string() for x in ach_insts]))
            elif self.args.list_nu_achs:
                package = self.get_app()
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(package.id) if x.state is not None]
                found_achievements = self.finder.ach_defs_by_ach_insts(ach_insts)
                print('\n'.join([self.finder.ach_def_by_ach_inst(x).print_string() for x in ach_insts]))
            elif self.args.list_nor_achs:
                package = self.get_app()
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(package.id) if x.type == 0]
                found_achievements = ach_defs
                print('\n'.join([x.print_string() for x in ach_defs]))
            elif self.args.list_inc_achs:
                package = self.get_app()
                ach_defs = [x for x in self.finder.ach_defs_by_game_id(package.id) if x.type == 1]
                found_achievements = ach_defs
                print('\n'.join([x.print_string() for x in ach_defs]))
            elif self.args.list_sec_achs:
                package = self.get_app()
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(package.id) if x.state == 2]
                found_achievements = self.finder.ach_defs_by_ach_insts(ach_insts)
                print('\n'.join([self.finder.ach_def_by_ach_inst(x).print_string() for x in ach_insts]))
            elif self.args.search_games:
                search = self.args.search_games[0]
                found_games = self.finder.find(search, self.db.games)
                print('\n'.join([x.print_string(self.finder.game_inst_by_game(x)) for x in found_games]))
            elif self.args.search_achs:
                package = self.get_app(optional=True)
                search = self.args.search_achs[0]
                found_achievements = self.find_achievements(search, package)
            elif self.args.search_u_achs:
                package = self.get_app(optional=True)
                search = self.args.search_u_achs[0]
                found_achievements = self.find_achievements(search, package, locked=False)
            elif self.args.search_nu_achs:
                package = self.get_app(optional=True)
                search = self.args.search_nu_achs[0]
                found_achievements = self.find_achievements(search, package, unlocked=False)

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

        except Exception as e:
            line = sys.exc_info()[2].tb_lineno
            ex(f"Error: {e} at line {line}\nSomething bad has happened, probably a bug or uncut edge case.\nPlease report this to the developer.")

    def unlock_achievement(self, ach_def: AchievementDefinition = None):
        if ach_def is None:
            return
        ach_inst = self.finder.ach_inst_by_ach_def(ach_def)
        game = self.finder.game_by_ach_inst(ach_inst)
        game_inst = self.finder.game_inst_by_game(game)
        client_context = self.finder.client_context_by_game_inst(game_inst)
        if not client_context:
            ex('No client context found for this game' if not self.args.quiet else "")
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
                steps_to_increment = self.get_increment_value()

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

    def get_increment_value(self):
        print(end='\r')
        value = input("Achievement is incremental, how many steps to increment? ")
        try:
            value = int(value)
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            return self.get_increment_value()

    def find_achievements(self, search, package, unlocked=True, locked=True):
        achs = self.finder.ach_defs_by_game(package) if package else self.db.achievement_definitions
        found_achs = self.finder.findby(search, ["name", "description"], achs)
        games = self.finder.games_by_ach_defs(found_achs)
        game_insts = self.finder.game_insts_by_games(games)
        ach_insts = self.finder.ach_insts_by_ach_defs(found_achs)
        print('\n'.join([
            Wrapper.join(y.external_game_id, y.display_name, z.package_name, x.print_string())
            for x, y, z, w in zip(found_achs, games, game_insts, ach_insts)
            if (w.state is None and unlocked) or (w.state is not None and locked)]))
        return found_achs

    def get_player_id(self):
        if self.args.player_id:
            return self.args.player_id[0]
        return self.db.players[0].external_player_id

    def get_app(self, optional=False):
        if self.args.app is None and self.args.app_id is None:
            if optional:
                return None
            ex('No package specified (use -a or -aid)')

        if self.args.app is not None:
            app = self.finder.game_inst_by_package_name(self.args.app)
            if not app:
                if optional:
                    return None
                ex('Package not found')
            return self.finder.game_by_game_inst(app)

        app = self.finder.game_by_external_id(self.args.app_id)
        if not app:
            if optional:
                return None
            ex('Package not found')
        return app


if __name__ == "__main__":
    if len(sys.argv[1:]) == 0:
        print(parser.print_help())
        exit(1)

    GooglePlayAchievementUnlocker(args)



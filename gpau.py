import os
import sys
import glob
from colored import fg, bg, attr
import argparse
import sqlite3 as sql
from db_objs import DbFile, Finder, Wrapper

parser = argparse.ArgumentParser(epilog="By @TheNoiselessNoise")
parser.add_argument('-i', dest='input', metavar='input', help='path to the .db file')
parser.add_argument('-q', dest='quiet', action='store_true', help='quiet mode')
parser.add_argument('-sm', dest='secure_mode', action='store_true', help='secure mode')
parser.add_argument('--readme', dest='readme', action='store_true', help='How to use this?')
package_group = parser.add_mutually_exclusive_group()
package_group.add_argument('-p', dest='package', metavar='package', help='package name')
package_group.add_argument('-pid', dest='package_id', metavar='package_id', help='package id')
list_group = parser.add_argument_group()
list_group.add_argument('--list-games', action='store_true', help='list all games')
list_group.add_argument('--list-cc', action='store_true', help='list all client contexts')
package_list_group = parser.add_argument_group()
package_list_group.add_argument('--list-achs', action='store_true', help='list all achievements')
package_list_group.add_argument('--list-u-achs', action='store_true', help='list all unlocked achievements')
package_list_group.add_argument('--list-nu-achs', action='store_true', help='list all not unlocked achievements')
search_group = parser.add_argument_group()
search_group.add_argument('--search-games', metavar='search', type=str, nargs=1, help='search for a game by input')
search_group.add_argument('--search-achs', metavar='search', type=str, nargs=1, help='search for an achievements by input')
search_group.add_argument('--search-u-achs', metavar='search', type=str, nargs=1, help='search for unlocked achievements by input')
search_group.add_argument('--search-nu-achs', metavar='search', type=str, nargs=1, help='search for not unlocked achievements by input')
args = parser.parse_args()

class Dummy:
    input = None
    quiet = False
    secure_mode = False
    readme = False

    # package
    package = None
    package_id = None

    # listing
    list_games = False
    list_cc = False

    # package listing
    list_achs = False
    list_u_achs = False
    list_nu_achs = False

    # searching
    search_games = None
    search_achs = None
    search_u_achs = None
    search_nu_achs = None

def ex(msg, _ex=True):
    sys.stderr.write(msg)
    if _ex:
        sys.exit(1)

class GooglePlayAchievementUnlocker:
    default_db_regex = "/data/data/com.google.android.gms/databases/games_*.db"

    def __init__(self, a):
        self.args: Dummy = a

        if self.args.readme:
            print(f"""{fg('red')}1){attr('reset')} Disconnect from the internet
{fg('orange_3')}2){attr('reset')} Unlock the achievements you want
{fg('yellow')}3){attr('reset')} Reconnect to the internet
{fg('light_green')}4){attr('reset')} Run Google Play Games to sync the achievements
{fg('light_blue')}5){attr('reset')} Profit""")
            sys.exit(0)

        try:
            if self.args.input is None:
                if not self.args.quiet:
                    print('No input specified, trying to find default database...')
                files = glob.glob(self.default_db_regex)
                if len(files) == 0:
                    ex("No database file found")
                if not os.access(files[0], os.R_OK):
                    ex("Found database file, but can't read it")
                print('Found database file: ' + files[0])
                self.db = DbFile(files[0])
            else:
                if not os.path.isfile(self.args.input):
                    ex('Input is not a file')
                if not os.access(self.args.input, os.R_OK):
                    ex('Input is not readable')
                self.db = DbFile(sql.connect(self.args.input))

            self.finder = Finder(self.db)

            if self.args.list_games:
                print('\n'.join([x.print_string(self.finder.game_inst_by_game(x)) for x in self.db.games]))
            elif self.args.list_cc:
                print('\n'.join([x.print_string(self.args.secure_mode) for x in self.db.client_contexts]))
            elif self.args.list_achs:
                package = self.get_package()
                ach_insts = self.finder.ach_insts_by_game_id(package.id)
                print('\n'.join([self.finder.ach_def_by_ach_inst(x).print_string() for x in ach_insts]))
            elif self.args.list_u_achs:
                package = self.get_package()
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(package.id) if x.state is None]
                print('\n'.join([self.finder.ach_def_by_ach_inst(x).print_string() for x in ach_insts]))
            elif self.args.list_nu_achs:
                package = self.get_package()
                ach_insts = [x for x in self.finder.ach_insts_by_game_id(package.id) if x.state is not None]
                print('\n'.join([self.finder.ach_def_by_ach_inst(x).print_string() for x in ach_insts]))
            elif self.args.search_games:
                search = self.args.search_games[0]
                found_games = self.finder.find(search, self.db.games)
                print('\n'.join([x.print_string(self.finder.game_inst_by_game(x)) for x in found_games]))
            elif self.args.search_achs:
                package = self.get_package(optional=True)
                search = self.args.search_achs[0]
                self.find_achievements(search, package)
            elif self.args.search_u_achs:
                package = self.get_package(optional=True)
                search = self.args.search_u_achs[0]
                self.find_achievements(search, package, locked=False)
            elif self.args.search_nu_achs:
                package = self.get_package(optional=True)
                search = self.args.search_nu_achs[0]
                self.find_achievements(search, package, unlocked=False)

        except Exception as e:
            print(e)
            ex("Something bad has happened, probably a bug or uncut edge case.\nPlease report this to the developer.")

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

    def get_package(self, optional=False):
        if self.args.package is None and self.args.package_id is None:
            if optional:
                return None
            ex('No package specified (use -p or -pid)')

        if self.args.package is not None:
            package = self.finder.game_inst_by_package_name(self.args.package)
            if package is None:
                if optional:
                    return None
                ex('Package not found')
            return self.finder.game_by_game_inst(package)

        package = self.finder.game_by_external_id(self.args.package_id)
        if package is None:
            if optional:
                return None
            ex('Package not found')
        return package


if __name__ == "__main__":
    if len(sys.argv[1:]) == 0:
        print(parser.print_help())
        exit(1)

    GooglePlayAchievementUnlocker(args)



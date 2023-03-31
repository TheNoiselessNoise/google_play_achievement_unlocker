import argparse
from gpau_objects.structure import *
from gpau_objects.gpau import GooglePlayAchievementUnlocker

DEBUG = False

parser = argparse.ArgumentParser(epilog="By @TheNoiselessNoise")
if not DEBUG:
    parser.add_argument('-i', dest='input', metavar='input', help='path to the .db file')
    parser.add_argument('-q', dest='quiet_mode', action='store_true', help='quiet mode')
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
    list_group = parser.add_mutually_exclusive_group()
    list_group.add_argument('--list-cc', action='store_true', help='list all client contexts')
    list_group.add_argument('--list-games', action='store_true', help='list all games')
    list_group.add_argument('--list-players', action='store_true', help='list all players')
    package_list_group = parser.add_mutually_exclusive_group()
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
    search_group.add_argument('--search-nor-achs', metavar='search', type=str, nargs=1, help='search for normal achievements by input')
    search_group.add_argument('--search-inc-achs', metavar='search', type=str, nargs=1, help='search for incremental achievements by input')
    search_group.add_argument('--search-sec-achs', metavar='search', type=str, nargs=1, help='search for secret achievements by input')
    unlock_group = parser.add_mutually_exclusive_group()
    unlock_group.add_argument('--unlock-id', dest='unlock_id', metavar='external_id', type=str, nargs=1, help='unlocks an achievement by its external id')
    unlock_group.add_argument('--unlock-all', dest='unlock_all', action='store_true', help='unlocks all achievements in given package')
    unlock_group.add_argument('--unlock-listed', dest='unlock_listed', action='store_true', help='unlocks all listed achievements')
    args = parser.parse_args()
else:
    args = Dummy()
    # args.input = "games_2db19fbf.db"
    # args.secure_mode = True
    # args.list_cc = True
    # args.list_achs = True
    # args.list_games = True
    # args.list_players = True
    # args.list_u_achs = True
    # args.list_nu_achs = True
    # args.list_nor_achs = True
    # args.list_inc_achs = True
    # args.list_sec_achs = True
    # args.search_games = ["Among Us"]
    # args.search_achs = ["I CAN BE YOUR ANGLE"]
    # args.search_u_achs = ["for"]
    # args.search_nu_achs = ["Brutal"]
    # args.search_nor_achs = ["Brutal"]
    # args.search_inc_achs = [""]
    # args.search_sec_achs = ["Brutal"]
    # args.unlock_all = True
    # args.unlock_listed = True
    # args.rem_all_ops = True
    # args.app = "com.gamefirst.free.strategy.god.simulator"
    # args.app = "com.miniclip.plagueinc"
    # args.app = "com.innersloth.spacemafia"
    # args.app = "com.ndemiccreations.rebelinc"
    # args.app = "com.direlight.grimvalor"

    # gpau = GooglePlayAchievementUnlocker(args)
    # game: Game = gpau.get_app()
    # ach_defs = gpau.finder.ach_defs_by_game_id(game.id)
    # print(game)

    # find games
    # games: Game = gpau.finder.games_by_name("Grimvalor")
    # game_insts: List[GameInstance] = gpau.finder.game_insts_by_games(games)
    # print([getattr(x, "package_name") for x in game_insts])
    # exit()

    # gpau.run()
    # game: Game = gpau.get_app()
    # ach_defs: List[AchievementDefinition] = gpau.finder.ach_defs_by_game_id(game.id)
    # ach_insts: List[AchievementInstance] = gpau.finder.ach_insts_by_ach_defs(ach_defs)
    exit()

if __name__ == "__main__":
    if not DEBUG:
        if len(sys.argv[1:]) == 0:
            print(parser.print_help())
            exit(1)

    GooglePlayAchievementUnlocker(args).run()

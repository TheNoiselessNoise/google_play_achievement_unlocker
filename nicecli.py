import sys
import time
import argparse
from gpau_objects.funcs import ex
from gpau_objects.structure import *
from terminaltables import AsciiTable
from gpau_objects.gpau import GooglePlayAchievementUnlocker as Gpau

parser = argparse.ArgumentParser(epilog='By @TheNoiselessNoise')
parser.add_argument('-i', dest='input', metavar='input', help='path to the .db file')
parser.add_argument('--games', action='store_true', help='Show all games registered in cc')
parser.add_argument('--all-games', action='store_true', help='Show all games')
parser.add_argument('--all-games-n', action='store_true', help='Show all games (not 100%)')
parser.add_argument('--sort', dest='sort', type=str, help='Sort by specified column name (default: Name)', default="Name")
ach_group = parser.add_argument_group('Achievements')
ach_group.add_argument('--show', action='store_true', help='Show all achievements of specified game')
ach_group.add_argument('-g', dest='game', type=str, help='Package name or cc id of a game')

skip_pkgs = ["com.google.android.play.games", "com.google.android.gms"]

class CliDummy:
    input = None
    games = False
    all_games = False
    all_games_n = False
    sort = "Name"
    show = False
    game = None

def table(data, title = None):
    t = AsciiTable(data)
    if title is not None:
        t.title = title
    print(t.table)

def sort_rows(rows, sort: str = None):
    sort = sort.lower()
    col_names = [x.lower() for x in rows[0]]
    if sort not in col_names:
        return rows
    sindex = col_names.index(sort)
    _rows = sorted(rows[1:], key=lambda x: x[sindex])
    return [rows[0]] + _rows

def show_games(g: Gpau, sort: str = None):
    ccs: List[ClientContext] = g.db.select_by_cls(ClientContext)

    games = [(g.finder.game_inst_by_package_name(cc.package_name), cc) for cc in ccs if cc.package_name not in skip_pkgs]

    rows = [["CC ID", "Name", "Achievements"]]
    for ginst, cc in games:
        game = g.finder.game_by_game_inst(ginst)
        ach_defs = g.finder.ach_defs_by_game(game)
        ach_insts = g.finder.ach_insts_by_ach_defs(ach_defs)
        uachs = [x for x in ach_insts if x.is_unlocked()]

        ach_str = f"{len(uachs)}/{len(ach_insts)}" if len(ach_insts) else "--NO--ACHS--"
        rows.append([cc.id, game.display_name, ach_str])

    table(sort_rows(rows, sort), "Games registered in cc")

def show_all_games(g: Gpau, sort: str = None, not_100: bool = False):
    __start_time = time.time()
    games = [game for game in g.db.select_by_cls(Game)]

    rows = [["Game ID", "Name", "Unlocked", "Achievements", "In CC"]]
    index = 0
    for game in games:
        index += 1

        if not game.display_name:
            inst = g.finder.game_inst_by_game(game)
            if not inst:
                continue
            game.display_name = inst.package_name
        ach_defs = g.finder.ach_defs_by_game(game)
        ach_insts = g.finder.ach_insts_by_ach_defs(ach_defs)
        uachs = [x for x in ach_insts if x.is_unlocked()]

        game_inst = g.finder.game_inst_by_game(game)
        cc = g.finder.client_context_by_game_inst(game_inst) if game_inst else None
        in_cc = "Yes" if cc else "No"

        print(f"Processed {index}/{len(games)} games in {time.time() - __start_time:.2f}s", end="\r")
        if not_100 and (not ach_defs or len(uachs) == len(ach_insts)):
            continue

        rows.append([game.id, game.display_name, len(uachs), len(ach_insts), in_cc])

    table(sort_rows(rows, sort))

def show_all_games_n(g: Gpau, sort: str = None):
    show_all_games(g, sort=sort, not_100=True)

def get_achievement_type(ach_def: AchievementDefinition):
    types = []
    if ach_def.is_incremental():
        types.append("Inc")
    types.append("Sec" if ach_def.is_secret() else "Nor")
    return "/".join(types)

def show_achs(name, g: Gpau, sort: str = None):
    game = find_game(name, g)
    if not game:
        ex(f"Game with name or cc id '{name}' not found")

    game_inst = g.finder.game_inst_by_game(game)
    ach_defs = g.finder.ach_defs_by_game(game)
    ach_insts = g.finder.ach_insts_by_ach_defs(ach_defs)

    rows = [["Type", "Name", "Description", "State"]]

    if not ach_defs:
        rows.append(["-"*len(x) for x in rows[0]])

    for d, i in zip(ach_defs, ach_insts):
        if i is None:
            rows.append([get_achievement_type(d), d.name, d.description, "NO_INSTANCE"])
            continue

        if i.is_unlocked():
            state = "UNLOCKED"
        elif d.is_incremental():
            state = f"{i.current_steps}/{d.total_steps}"
        else:
            state = "LOCKED"

        rows.append([get_achievement_type(d), d.name, d.description, state])

    table(sort_rows(rows, sort), f"{game.display_name} ({game_inst.package_name})")

def find_game(name_or_ccid, g: Gpau):
    if name_or_ccid.isdigit():
        cc = g.finder.client_context_by_id(name_or_ccid)
        return find_game(cc.package_name, g) if cc else None
    gi = g.finder.game_inst_by_package_name(name_or_ccid)
    return g.finder.game_by_game_inst(gi) if gi else None

def main(args):
    args: CliDummy = args

    dummy = Dummy()
    dummy.input = args.input
    g = Gpau(dummy)

    if args.games:
        show_games(g, args.sort)
    elif args.all_games:
        show_all_games(g, args.sort)
    elif args.all_games_n:
        show_all_games_n(g, args.sort)
    elif args.show and args.game:
        show_achs(args.game, g, args.sort)

if __name__ == '__main__':
    if not len(sys.argv[1:]):
        parser.print_help()
        sys.exit()
    main(parser.parse_args())

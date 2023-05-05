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
parser.add_argument('--all-games-n', action='store_true', help='Show all games not 100%% completed')
parser.add_argument('--sort', dest='sort', type=str, help='Sort by specified column name, default: Name', default="Name")
ach_group = parser.add_argument_group('Achievements')
ach_group.add_argument('--info', action='store_true', help='Show info about specified game, needs -g as Game ID')
ach_group.add_argument('--show', action='store_true', help='Show all achievements of specified game, needs -g as Package Name or Game ID')
ach_group.add_argument('--unlock', type=str, metavar='ach_ex_id', help='Unlock specified achievement, Achievement external ID')
ach_group.add_argument('--unlock-list', nargs='+', metavar='ach_ex_id', help='Unlock specified achievements, Achievement external IDs separated by space')
ach_group.add_argument('--unlock-all', action='store_true', help='Unlock all achievements, needs -g as CC ID')
ach_group.add_argument('-g', dest='game', type=str, help='Package Name, Game ID or CC ID')

skip_pkgs = ["com.google.android.play.games", "com.google.android.gms"]

class CliDummy:
    input       = None
    games       = False
    all_games   = False
    all_games_n = False
    sort        = "Name"

    info        = False
    show        = False
    unlock      = False
    unlock_list = None
    unlock_all  = False

    game        = None  # Package Name, Game ID or CC ID

def table(data, title=None):
    t = AsciiTable(data)
    if title is not None:
        print("\n+" + "-" * (len(title) + 2) + "+")
        print(f"| {title} |")
    print(("\n" if title is None else "") + t.table + "\n")

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

    rows = [["CC ID", "Game ID", "Package Name", "Name", "Achievements"]]
    for ginst, cc in games:
        game = g.finder.game_by_game_inst(ginst)
        ach_defs = g.finder.ach_defs_by_game(game)
        ach_insts = g.finder.ach_insts_by_ach_defs(ach_defs)
        uachs = [x for x in ach_insts if x.is_unlocked()]

        ach_str = f"{len(uachs)}/{len(ach_insts)}" if len(ach_insts) else "-" * len(rows[0][-1])
        package_name = "NO_INSTANCE" if ginst is None else ginst.package_name
        rows.append([cc.id, game.id, package_name, game.display_name, ach_str])

    table(sort_rows(rows, sort), "Games registered in cc")

def show_all_games(g: Gpau, sort: str = None, not_100: bool = False):
    __start_time = time.time()
    games = [game for game in g.db.select_by_cls(Game)]

    rows = [["Game ID", "Package Name", "Name", "Unlocked", "Achievements", "In CC"]]
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

        package_name = "NO_INSTANCE" if game_inst is None else game_inst.package_name
        rows.append([game.id, package_name, game.display_name, len(uachs), len(ach_insts), in_cc])

    table(sort_rows(rows, sort))

def show_all_games_n(g: Gpau, sort: str = None):
    show_all_games(g, sort=sort, not_100=True)

def get_achievement_type(ach_def: AchievementDefinition):
    types = []
    if ach_def.is_incremental():
        types.append("Inc")
    types.append("Sec" if ach_def.is_secret() else "Nor")
    return "/".join(types)

def get_achievement_state(ach_def: AchievementDefinition, ach_inst: AchievementInstance):
    if ach_inst.is_unlocked():
        return "UNLOCKED"
    elif ach_def.is_incremental():
        return f"{ach_inst.current_steps}/{ach_def.total_steps}"
    return "LOCKED"

def show_achs(g: Gpau, name, sort: str = None):
    game = find_game(g, name, use_game_id=True)
    if not game:
        ex(f"Game with Package Name or Game ID '{name}' not found")

    game_inst = g.finder.game_inst_by_game(game)
    ach_defs = g.finder.ach_defs_by_game(game)
    ach_insts = g.finder.ach_insts_by_ach_defs(ach_defs)

    rows = [["Type", "External ID", "Name", "Description", "State"]]

    if not ach_defs:
        rows.append(["-"*len(x) for x in rows[0]])

    for d, i in zip(ach_defs, ach_insts):
        ach_type = get_achievement_type(d)
        ach_exid = d.external_achievement_id
        ach_name = d.name
        ach_desc = d.description.strip()
        ach_state = "NO_INSTANCE" if i is None else get_achievement_state(d, i)

        rows.append([ach_type, ach_exid, ach_name, ach_desc, ach_state])

    table(sort_rows(rows, sort), f"{game.display_name} ({game_inst.package_name})")

def find_game(g: Gpau, name_or_ccid, use_game_id=False):
    if name_or_ccid.isdigit():
        if use_game_id:
            gi = g.finder.game_inst_by_game_id(name_or_ccid)
            return g.finder.game_by_game_inst(gi) if gi else None

        cc = g.finder.client_context_by_id(name_or_ccid)
        return find_game(g, cc.package_name) if cc else None

    gi = g.finder.game_inst_by_package_name(name_or_ccid)
    return g.finder.game_by_game_inst(gi) if gi else None

def unlock_all_achs(g: Gpau, ccid):
    g.args.auto_inc_achs = True

    game = find_game(g, ccid)
    if not game:
        ex(f"Game with Package Name or CC ID '{ccid}' not found")

    ach_defs = g.finder.ach_defs_by_game(game)
    for ach_def in ach_defs:
        g.unlock_achievement(ach_def)

def unlock_ach(g: Gpau, ach_external_id):
    g.args.auto_inc_achs = True

    ach_def = g.finder.ach_def_by_external_id(ach_external_id)
    if not ach_def:
        ex(f"Achievement with External ID '{ach_external_id}' not found", _ex=False)

    g.unlock_achievement(ach_def)

def unlock_achs(g: Gpau, ach_external_ids):
    for ach in ach_external_ids:
        unlock_ach(g, ach)

def show_game_info(g: Gpau, gid):
    game = find_game(g, gid, use_game_id=True)
    if not game:
        ex(f"Game with Game ID '{gid}' not found")
    game.dump()

    game_inst = g.finder.game_inst_by_game(game)
    if not game_inst:
        ex(f"Game doesn't have any Instance")
    game_inst.dump()

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
    elif args.info and args.game:
        show_game_info(g, args.game)
    elif args.show and args.game:
        show_achs(g, args.game, args.sort)
    elif args.unlock:
        unlock_ach(g, args.unlock)
    elif args.unlock_list:
        unlock_achs(g, args.unlock_list)
    elif args.unlock_all and args.game:
        unlock_all_achs(g, args.game)

if __name__ == '__main__':
    if not len(sys.argv[1:]):
        parser.print_help()
        sys.exit()
    main(parser.parse_args())

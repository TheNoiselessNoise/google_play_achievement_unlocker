import os
import sys
import time
import argparse
from argparse import Namespace
from gpau_objects.common import Logger
from terminaltables import AsciiTable # type: ignore[import-untyped]
from gpau_objects.gpau import GooglePlayAchievementUnlocker as Gpau
from gpau_objects.structure import *
from typing import List, Tuple, Optional, Union

parser = argparse.ArgumentParser(epilog='By @TheNoiselessNoise')
parser.add_argument('-i', dest='input', metavar='input', help='path to the .db file')
parser.add_argument('--games', action='store_true', help='Show all games registered in cc')
parser.add_argument('--players', action='store_true', help='Show all players')
parser.add_argument('--ops', action='store_true', help='Show all achievement pending ops')
parser.add_argument('--all-games', action='store_true', help='Show all games')
parser.add_argument('--all-games-n', action='store_true', help='Show all games not 100%% completed')
parser.add_argument('--sort', dest='sort', type=str, help='Sort by specified column name, default: Name')
ach_group = parser.add_argument_group('Achievements')
ach_group.add_argument('--info', action='store_true', help='Show info about specified game, needs -g as Game ID')
ach_group.add_argument('--show', action='store_true', help='Show all achievements of specified game, needs -g as Package Name or Game ID')
ach_group.add_argument('--unlock', type=str, metavar='ach_ex_id', help='Unlock specified achievement, Achievement external ID')
ach_group.add_argument('--unlock-list', nargs='+', metavar='ach_ex_id', help='Unlock specified achievements, Achievement external IDs separated by space')
ach_group.add_argument('--unlock-all', action='store_true', help='Unlock all achievements, needs -g as CC ID')
ach_group.add_argument('-g', dest='game', type=str, help='Package Name, Game ID or CC ID')
ach_group.add_argument('-p', dest='player', type=str, help='Player #')

skip_pkgs = ["com.google.android.play.games", "com.google.android.gms"]

class CliDummy:
    input       : Optional[str]       = None
    games       : bool                = False
    players     : bool                = False
    ops         : bool                = False
    all_games   : bool                = False
    all_games_n : bool                = False
    sort        : Optional[str]       = None

    info        : bool                = False
    show        : bool                = False
    unlock      : Optional[str]       = None
    unlock_list : Optional[List[str]] = None
    unlock_all  : bool                = False

    game        : Optional[str]       = None  # Package Name, Game ID or CC ID
    player      : Optional[str]       = None  # Player #

def table(data: List[List[str]], title: Optional[str]=None):
    if len(data) == 1:
        if title:
            title += " (NOTHING FOUND)"
        data.append(["-"*len(x) for x in data[0]])

    t = AsciiTable(data)
    if title is not None:
        print("\n+" + "-" * (len(title) + 2) + "+")
        print(f"| {title} |")
    print(f"{t.table}\n" if title else f"\n{t.table}")

def sort_rows(rows: List[List[str]], sort: Optional[str]=None):
    if sort is None:
        return rows
    sort = sort.lower()
    col_names = [x.lower() for x in rows[0]]
    if sort not in col_names:
        return rows
    sindex = col_names.index(sort)
    _rows = sorted(rows[1:], key=lambda x: x[sindex])
    return [rows[0]] + _rows

def show_games(g: Gpau, sort: Optional[str]=None):
    ccs: List[ClientContext] = g.db.select_by_cls(ClientContext)

    games: List[Tuple[Optional[GameInstance], ClientContext]] = []

    for cc in ccs:
        game_inst = g.finder.game_inst_by_package_name(cc.package_name)
        games.append((game_inst, cc))

    rows: List[List[str]] = [["CC ID", "Game ID", "Package Name", "Name", "Achievements"]]

    for ginst, cc in games:
        game = None if not ginst else g.finder.game_by_game_inst(ginst)
        
        ach_defs = [] if not game else [x for x in g.finder.ach_defs_by_game(game) if x]
        ach_insts = [x for x in g.finder.ach_insts_by_ach_defs(ach_defs) if x]
        uachs = [x for x in ach_insts if x.is_unlocked()]

        ach_str = f"{len(uachs)}/{len(ach_insts)}" if len(ach_insts) else "-" * len(rows[0][-1])
        game_id = str(game.id if game else "NO_GAME")
        package_name = "NO_INSTANCE" if ginst is None else ginst.package_name
        display_name = game.display_name if game else "NO_GAME"
        rows.append([str(cc.id), game_id, package_name, display_name, ach_str])

    table(sort_rows(rows, sort), "Games registered in cc")

def show_players(g: Gpau, sort: Optional[str]=None):
    rows: List[List[str]] = [["#", "File", "Player ID", "Name", "Level"]]

    index = 1
    for db_file, db_player in g.get_players().items():
        file_name = os.path.basename(db_file)
        player_id = db_player.external_player_id
        player_name = db_player.profile_name
        player_level = db_player.current_level
        rows.append([str(index), file_name, player_id, player_name, player_level])
        index += 1

    table(sort_rows(rows, sort), "Players")

def show_ops(g: Gpau):
    rows: List[List[str]] = [["CC ID", "Achievement ID", "Game ID", "Player ID"]]

    ops: List[AchievementPendingOp] = [x for x in g.db.select_by_cls(AchievementPendingOp) if x]

    for op in ops:
        rows.append([str(op.client_context_id), str(op.external_achievement_id), str(op.external_game_id), str(op.external_player_id)])

    table(rows, "Achievement Pending Ops")

def show_all_games(g: Gpau, sort: Optional[str]=None, not_100: bool=False):
    __start_time: float = time.time()
    games: List[Game] = [x for x in g.db.select_by_cls(Game) if x]

    rows: List[List[str]] = [["Game ID", "Package Name", "Name", "Unlocked", "Achievements", "In CC"]]
    index: int = 0
    for game in games:
        index += 1

        if not game.display_name:
            inst = g.finder.game_inst_by_game(game)
            if not inst:
                continue
            game.display_name = inst.package_name

        ach_defs = [x for x in g.finder.ach_defs_by_game(game) if x]
        ach_insts = g.finder.ach_insts_by_ach_defs(ach_defs)
        uachs = [x for x in ach_insts if x and x.is_unlocked()]

        game_inst = g.finder.game_inst_by_game(game)
        cc = g.finder.client_context_by_game_inst(game_inst) if game_inst else None
        in_cc = "Yes" if cc else "No"

        print(f"Processed {index}/{len(games)} games in {time.time() - __start_time:.2f}s", end="\r")
        if not_100 and (not ach_defs or len(uachs) == len(ach_insts)):
            continue

        package_name = "NO_INSTANCE" if game_inst is None else game_inst.package_name
        rows.append([str(game.id), package_name, game.display_name, str(len(uachs)), str(len(ach_insts)), in_cc])

    title = "All Games"
    if not_100:
        title += " (NOT 100% Completed)"
    table(sort_rows(rows, sort), title)

def show_all_games_n(g: Gpau, sort: Optional[str]=None):
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

def show_achs(g: Gpau, name: str, sort: Optional[str]=None):
    game = find_game(g, name, use_game_id=True)
    if not game:
        Logger.error_exit(f"Game with Package Name or Game ID '{name}' not found")

    game_inst = g.finder.game_inst_by_game(game)
    ach_defs = [x for x in g.finder.ach_defs_by_game(game) if x]
    ach_insts = g.finder.ach_insts_by_ach_defs(ach_defs)

    rows: List[List[str]] = [["Type", "External ID", "Name", "Description", "State"]]

    if not ach_defs:
        rows.append(["-"*len(x) for x in rows[0]])

    for d, i in zip(ach_defs, ach_insts):
        ach_type = get_achievement_type(d)
        ach_exid = d.external_achievement_id
        ach_name = d.name
        ach_desc = d.description.strip()
        ach_state = "NO_INSTANCE" if i is None else get_achievement_state(d, i)

        rows.append([ach_type, ach_exid, ach_name, ach_desc, ach_state])

    display_name = game.display_name if game.display_name else "NO_GAME"
    package_name = "NO_INSTANCE" if game_inst is None else game_inst.package_name
    table(sort_rows(rows, sort), f"{display_name} ({package_name})")

def find_game(g: Gpau, name_or_ccid: str, use_game_id=False):
    if name_or_ccid.isdigit():
        if use_game_id:
            gi = g.finder.game_inst_by_game_id(name_or_ccid)
            return g.finder.game_by_game_inst(gi) if gi else None

        cc = g.finder.client_context_by_id(name_or_ccid)
        return find_game(g, cc.package_name) if cc else None

    gi = g.finder.game_inst_by_package_name(name_or_ccid)
    return g.finder.game_by_game_inst(gi) if gi else None

def unlock_all_achs(g: Gpau, ccid: str):
    g.args.auto_inc_achs = True

    game = find_game(g, ccid)
    if not game:
        Logger.error_exit(f"Game with Package Name or CC ID '{ccid}' not found")

    ach_defs = [x for x in g.finder.ach_defs_by_game(game) if x]
    for ach_def in ach_defs:
        g.unlock_achievement(ach_def)

def unlock_ach(g: Gpau, ach_external_id: str):
    g.args.auto_inc_achs = True

    ach_def = g.finder.ach_def_by_external_id(ach_external_id)
    if not ach_def:
        Logger.warning(f"Achievement with External ID '{ach_external_id}' not found")
        return

    g.unlock_achievement(ach_def)

def unlock_achs(g: Gpau, ach_external_ids: List[str]):
    for ach in ach_external_ids:
        unlock_ach(g, ach)

def show_game_info(g: Gpau, gid: str):
    game = find_game(g, gid, use_game_id=True)
    if not game:
        Logger.error_exit(f"Game with Game ID '{gid}' not found")
    game.dump()

    game_inst = g.finder.game_inst_by_game(game)
    if not game_inst:
        Logger.warning(f"Game doesn't have any Instance")
        return
    game_inst.dump()

def main(cli_args):
    args: Union[Namespace, CliDummy] = cli_args

    dummy = Dummy()
    dummy.input = args.input
    dummy.player = args.player
    g = Gpau(dummy)

    if args.games:
        show_games(g, args.sort)
    elif args.players:
        show_players(g, args.sort)
    elif args.ops:
        show_ops(g)
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

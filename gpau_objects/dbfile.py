from gpau_objects.structure import AchievementPendingOp, Wrapper, AchievementDefinition, AchievementInstance, ClientContext, GameInstance, GamePlayerId, Game, Image, Player
from gpau_objects.common import Logger
from sqlite3 import Connection
from typing import Dict, List, Any

class DbFile:
    mapping = {
        "achievement_pending_ops": AchievementPendingOp,
        "achievement_definitions": AchievementDefinition,
        "achievement_instances": AchievementInstance,
        "client_contexts": ClientContext,
        "game_instances": GameInstance,
        "game_player_ids": GamePlayerId,
        "games": Game,
        "images": Image,
        "players": Player
    }

    def __init__(self, connection: Connection):
        self.connection = connection
        self.cur = self.connection.cursor()

    def __get_table_by_cls(self, cls: type):
        try:
            cls_index = list(self.mapping.values()).index(cls)
            return list(self.mapping.keys())[cls_index]
        except ValueError:
            name = cls.__name__ if isinstance(cls, type) else cls
            Logger.error_exit(f"Given class '{name}' doesn't have associated table")

    def select_by_cls(self, cls: type=None, cols: List[str]=None, values: List[Any]=None, first: bool=False, exact: bool=False):
        return self.select(cls=cls, cols=cols, values=values, first=first, exact=exact)

    def select_by_cls_fe(self, cls: type=None, cols: List[str]=None, values: List[Any]=None):
        return self.select(cls=cls, cols=cols, values=values, first=True, exact=True)

    def search_by_cls(self, search: str, cls: type=None, first: bool=False, exact: bool=False):
        return self.search(search=search, cls=cls, first=first, exact=exact)

    def search_by_cls_fe(self, search: str, cls: type=None):
        return self.search(search=search, cls=cls, first=True, exact=True)

    def search(self, search: str, table: str=None, cls: type=None, first: bool=False, exact: bool=False):
        if cls is not None:
            table = self.__get_table_by_cls(cls)

        s = str(search).lower()
        sql = f"select * from {table} where (1=0"
        for col in cls().attrs():
            if exact:
                sql += f" or lower({col})='{s}'"
            else:
                sql += f" or lower({col}) like '%{s}%'"
        sql += ") order by _id"

        res = self.cur.execute(sql).fetchall()
        res = [x if cls is None else cls(*x) for x in res]

        if len(res):
            return res[0] if first else res
        return None if first else []

    @staticmethod
    def search_instances(search: Any, objs: List[Wrapper], first: bool=False, exact: bool=False):
        s = str(search).lower()
        res = list(filter(
            lambda x: any(s == str(y).lower() if exact else s in str(y).lower() for y in x.values()), objs))

        if len(res):
            return res[0] if first else res
        return None if first else []

    def search_instances_by(self, s: Any, cols: List[str]=None, objs: List[Wrapper]=None, first: bool=False, exact: bool=False):
        if not objs:
            return []
        if not cols:
            return self.search_instances(s, objs, first)

        res = []
        s = str(s).lower()
        for obj in objs:
            attrs = obj.attrs()
            attrs = [x for x in cols if x in attrs]
            values = [str(getattr(obj, x)).lower() for x in attrs]
            if any(s == x if exact else s in x for x in values):
                res.append(obj)

        if len(res):
            return res[0] if first else res
        return None if first else []

    def select(self, table: str=None, cols: List[str]=None, values: List[Any]=None, cls: type=None, first: bool=False, exact: bool=False):
        if cls is not None:
            table = self.__get_table_by_cls(cls)

        cil = isinstance(cols, list)
        if not cil: cols = []
        vil = isinstance(values, list)
        if not vil: values = []
        if cil and vil and len(cols) != len(values):
            Logger.error_exit("Given cols doesn't have appropriate number of values")

        sql = f"select * from {table} where 1=1"
        for c, v in zip(cols, values):
            if exact:
                sql += f" and {c}='{v}'"
            else:
                sql += f" and {c} like '%{v}%'"
        sql += " order by _id"

        res = self.cur.execute(sql).fetchall()
        res = [x if cls is None else cls(*x) for x in res]

        if len(res):
            return res[0] if first else res
        return None if first else []

    def ex(self, table: str):
        return self.cur.execute("select * from " + table + " order by _id")

    def remove_duplicate_pending_ops(self, by_col: str="external_achievement_id"):
        ops = [AchievementPendingOp(*x) for x in self.ex("achievement_pending_ops").fetchall()]
        seen = set()
        removed = 0
        for op in ops:
            if getattr(op, by_col) in seen:
                self.cur.execute("delete from achievement_pending_ops where _id = ?", (op.id,))
                removed += 1
            else:
                seen.add(getattr(op, by_col))
        self.connection.commit()
        return removed

    def empty_pending_ops(self):
        self.cur.execute("delete from achievement_pending_ops")
        self.connection.commit()

    def add_pending_op(self, op: Dict[str, Any]):
        sql = "insert into achievement_pending_ops values ({})".format(
            ",".join("?" for _ in range(len(op))))
        self.cur.execute(sql, list(op.values()))
        self.connection.commit()

    def get_next_pending_op_id(self):
        res = self.cur.execute("select max(_id) from achievement_pending_ops").fetchone()[0]
        return 0 if res is None else res + 1

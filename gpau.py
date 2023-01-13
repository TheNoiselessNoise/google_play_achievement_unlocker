import os
import sys
import argparse
import sqlite3 as sql
from db_objs import DbFile, Finder, AchievementDefinition, AchievementInstance

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", metavar="<db>", help="input db file")
args = parser.parse_args()

class GooglePlayAchievementUnlocker:
    def __init__(self, path):
        self.db = DbFile(sql.connect(path))
        self.finder = Finder(self.db)

        # get unlocked achievement of the game
        """
        game = self.finder.game_by_name("Merger")
        
        # game related AchievementDefinitions
        defs = self.finder.ach_defs_by_game(game)
        
        # game related AchievementInstances based on
        # AchievementDefinitions
        insts = self.finder.ach_insts_by_ach_defs(defs)
        
        for d, i in zip(defs, insts):
            d: AchievementDefinition = d
            i: AchievementInstance = i
            
            # if state of AchievementInstance is None
            # achievement is unlocked
            if i.state is None:
                d.dump()
                i.dump()
        """
              
        # TODO: find out what the other states are (0,1,2)
        uinst = self.finder.ach_inst_by_id(72)
        ugame = self.finder.game_by_ach_inst(uinst)
        
        ugame.dump()
        
    
if __name__ == "__main__":
    if len(sys.argv[1:]) == 0:
        print(parser.print_help())
        exit(1)
        
    if not os.path.isfile(args.input):
        print("Error: Input is not a file")
        exit(1)
        
    gpau = GooglePlayAchievementUnlocker(args.input)
    
    
        
    
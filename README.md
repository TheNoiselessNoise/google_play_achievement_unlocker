# Google Play Achievement Unlocker (root)
Unlock Google Play achievements easily.\
But beware! There's no lock mechanism.\
You have been warned... cheater.

## Android App (root)
<img src="logo.png" width="128"/>
[GPAU Android](https://github.com/TheNoiselessNoise/google_play_achievement_unlocker_app)

### How to use? (Termux)
```bash
tsu
python gpau.py
```

### Information
- default db file is `/data/data/com.google.android.gms/databases/games_*.db`

### Example
_unlock all 'secret' achievements in provided app_
```bash
python gpau.py --list-sec-achs --unlock-listed -a com.miniclip.plagueinc
```

### Nice CLI (simplifies basic usage)

_show all games registered in cc_
```bash
python nicecli.py --games
```

_show all games not 100% completed_
```bash
python nicecli.py --all-games-n
```

_unlock single achievement_
```bash
python nicecli.py --unlock CgkIoKSYmJkOEAIQ5AE
```

_unlock multiple achievements_
```bash
python nicecli.py --unlock-list CgkIoKSYmJkOEAIQ5AE CgkIoKSYmJkOEAIQxgE
```

_unlock all achievements in provided app_
```bash
python nicecli.py --unlock-all -g com.miniclip.plagueinc
```

_and much more..._
```bash
python gpau.py --help
python nicecli.py --help
```

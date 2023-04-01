# Google Play Achievement Unlocker (root)
Unlock Google Play achievements easily.\
But beware! There's no lock mechanism.\
You have been warned... cheater.

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
python3 gpau.py --list-sec-achs --unlock-listed -a com.grumpyrhinogames.necromerger
```
```
CgkI0IOM87sIEAIQQA : Undead Alien I : Discover a lvl 1 Undead Alien. : 500xp
CgkI0IOM87sIEAIQQQ : Undead Alien II : Discover a max lvl Undead Alien. : 500xp
CgkI0IOM87sIEAIQQg : Guzzler I : Discover a Guzzler. : 500xp
CgkI0IOM87sIEAIQQw : Peaceful Spirit I : Discover a lvl 1 Peaceful Spirit. : 500xp
CgkI0IOM87sIEAIQRA : Peaceful Spirit II : Discover a max lvl Peaceful Spirit. : 500xp
CgkI0IOM87sIEAIQRQ : Vengeful Spirit I : Discover a lvl 1 Vengeful Spirit. : 500xp
CgkI0IOM87sIEAIQRg : Vengeful Spirit II : Discover a max lvl Vengeful Spirit. : 500xp
CgkI0IOM87sIEAIQRw : Shield Bot : Discover the Shield Bot. : 500xp
CgkI0IOM87sIEAIQSA : Soul Stalker : Discover the Soul Stalker. : 500xp
Unlocking achievement CgkI0IOM87sIEAIQQA (com.grumpyrhinogames.necromerger)...
Unlocking achievement CgkI0IOM87sIEAIQQQ (com.grumpyrhinogames.necromerger)...
Unlocking achievement CgkI0IOM87sIEAIQQg (com.grumpyrhinogames.necromerger)...
Unlocking achievement CgkI0IOM87sIEAIQQw (com.grumpyrhinogames.necromerger)...
Unlocking achievement CgkI0IOM87sIEAIQRA (com.grumpyrhinogames.necromerger)...
Unlocking achievement CgkI0IOM87sIEAIQRQ (com.grumpyrhinogames.necromerger)...
Unlocking achievement CgkI0IOM87sIEAIQRg (com.grumpyrhinogames.necromerger)...
Unlocking achievement CgkI0IOM87sIEAIQRw (com.grumpyrhinogames.necromerger)...
Unlocking achievement CgkI0IOM87sIEAIQSA (com.grumpyrhinogames.necromerger)...
```

_show all games not 100% completed_
```bash
python3 nicecli.py --all-games-n
```
```
+---------+-------------+----------+--------------+-------+
| Game ID | Name        | Unlocked | Achievements | In CC |
+---------+-------------+----------+--------------+-------+
| 16      | Among Us    | 7        | 33           | No    |
| 141     | Grimvalor   | 7        | 27           | Yes   |
| 244     | Plague Inc. | 63       | 200          | Yes   |
| 245     | Rebel Inc.  | 8        | 71           | No    |
+---------+-------------+----------+--------------+-------+
```
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
python gpau.py --list-sec-achs -a com.grumpyrhinogames.necromerger --unlock-listed --rem-dup-ops
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
Removing duplicate pending achievement ops...
Removed: 9
```
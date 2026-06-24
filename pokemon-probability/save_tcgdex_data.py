#!/usr/bin/env python3
"""
TCGdex Data Saver - Saves data fetched via webfetch to CSV/JSON
Run this after webfetch calls populate the data
"""
import json
import csv
import os

OUTPUT_DIR = "/Users/calvinchu/Desktop/mimo/pokemon-probability"

# All sets data from api.tcgdex.net/v2/en/sets
SETS_DATA = [
    {"id":"base1","name":"Base Set","cards":102,"releaseDate":"1999-01-09"},
    {"id":"base2","name":"Jungle","cards":64,"releaseDate":"1999-06-16"},
    {"id":"base3","name":"Fossil","cards":62,"releaseDate":"1999-10-10"},
    {"id":"base4","name":"Base Set 2","cards":130,"releaseDate":"2000-02-23"},
    {"id":"base5","name":"Team Rocket","cards":82,"releaseDate":"2000-04-24"},
    {"id":"gym1","name":"Gym Heroes","cards":132,"releaseDate":"2000-08-14"},
    {"id":"gym2","name":"Gym Challenge","cards":132,"releaseDate":"2000-11-08"},
    {"id":"neo1","name":"Neo Genesis","cards":111,"releaseDate":"1999-12-16"},
    {"id":"neo2","name":"Neo Discovery","cards":75,"releaseDate":"2000-06-26"},
    {"id":"neo3","name":"Neo Revelation","cards":64,"releaseDate":"2000-09-21"},
    {"id":"neo4","name":"Neo Destiny","cards":105,"releaseDate":"2001-02-28"},
    {"id":"lc","name":"Legendary Collection","cards":110,"releaseDate":"2001-05-24"},
    {"id":"ecard1","name":"Expedition Base Set","cards":165,"releaseDate":"2001-09-15"},
    {"id":"ecard2","name":"Aquapolis","cards":147,"releaseDate":"2002-02-13"},
    {"id":"ecard3","name":"Skyridge","cards":144,"releaseDate":"2002-06-14"},
    {"id":"ex1","name":"Ruby & Sapphire","cards":109,"releaseDate":"2003-07-30"},
    {"id":"ex2","name":"Sandstorm","cards":100,"releaseDate":"2003-09-17"},
    {"id":"ex3","name":"Dragon","cards":97,"releaseDate":"2003-11-24"},
    {"id":"ex4","name":"Team Magma vs Team Aqua","cards":95,"releaseDate":"2004-03-15"},
    {"id":"ex5","name":"Hidden Legends","cards":101,"releaseDate":"2004-06-14"},
    {"id":"ex6","name":"FireRed & LeafGreen","cards":112,"releaseDate":"2004-08-25"},
    {"id":"ex7","name":"Team Rocket Returns","cards":109,"releaseDate":"2004-11-08"},
    {"id":"ex8","name":"Deoxys","cards":107,"releaseDate":"2005-02-14"},
    {"id":"ex9","name":"Emerald","cards":106,"releaseDate":"2005-05-11"},
    {"id":"ex10","name":"Unseen Forces","cards":115,"releaseDate":"2005-08-17"},
    {"id":"ex11","name":"Delta Species","cards":113,"releaseDate":"2005-11-09"},
    {"id":"ex12","name":"Legend Maker","cards":92,"releaseDate":"2006-02-15"},
    {"id":"ex13","name":"Holon Phantoms","cards":110,"releaseDate":"2006-05-24"},
    {"id":"ex14","name":"Crystal Guardians","cards":100,"releaseDate":"2006-08-16"},
    {"id":"ex15","name":"Dragon Frontiers","cards":101,"releaseDate":"2006-11-08"},
    {"id":"ex16","name":"Power Keepers","cards":108,"releaseDate":"2007-02-14"},
    {"id":"dp1","name":"Diamond & Pearl","cards":130,"releaseDate":"2007-05-23"},
    {"id":"dp2","name":"Mysterious Treasures","cards":123,"releaseDate":"2007-08-22"},
    {"id":"dp3","name":"Secret Wonders","cards":132,"releaseDate":"2007-11-07"},
    {"id":"dp4","name":"Great Encounters","cards":106,"releaseDate":"2008-02-13"},
    {"id":"dp5","name":"Majestic Dawn","cards":100,"releaseDate":"2008-05-14"},
    {"id":"dp6","name":"Legends Awakened","cards":146,"releaseDate":"2008-08-13"},
    {"id":"dp7","name":"Stormfront","cards":100,"releaseDate":"2008-11-05"},
    {"id":"pl1","name":"Platinum","cards":127,"releaseDate":"2009-02-04"},
    {"id":"pl2","name":"Rising Rivals","cards":111,"releaseDate":"2009-05-20"},
    {"id":"pl3","name":"Supreme Victors","cards":147,"releaseDate":"2009-08-19"},
    {"id":"pl4","name":"Arceus","cards":99,"releaseDate":"2009-11-04"},
    {"id":"hgss1","name":"HeartGold SoulSilver","cards":123,"releaseDate":"2010-02-10"},
    {"id":"hgss2","name":"Unleashed","cards":95,"releaseDate":"2010-05-12"},
    {"id":"hgss3","name":"Undaunted","cards":90,"releaseDate":"2010-08-18"},
    {"id":"hgss4","name":"Triumphant","cards":102,"releaseDate":"2010-11-02"},
    {"id":"col1","name":"Call of Legends","cards":95,"releaseDate":"2011-02-09"},
    {"id":"bw1","name":"Black & White","cards":114,"releaseDate":"2011-04-25"},
    {"id":"bw2","name":"Emerging Powers","cards":98,"releaseDate":"2011-08-31"},
    {"id":"bw3","name":"Noble Victories","cards":101,"releaseDate":"2011-11-16"},
    {"id":"bw4","name":"Next Destinies","cards":99,"releaseDate":"2012-02-08"},
    {"id":"bw5","name":"Dark Explorers","cards":108,"releaseDate":"2012-05-09"},
    {"id":"bw6","name":"Dragons Exalted","cards":124,"releaseDate":"2012-08-15"},
    {"id":"bw7","name":"Boundaries Crossed","cards":149,"releaseDate":"2012-11-07"},
    {"id":"bw8","name":"Plasma Storm","cards":135,"releaseDate":"2013-02-06"},
    {"id":"bw9","name":"Plasma Freeze","cards":116,"releaseDate":"2013-05-08"},
    {"id":"bw10","name":"Plasma Blast","cards":101,"releaseDate":"2013-08-14"},
    {"id":"bw11","name":"Legendary Treasures","cards":113,"releaseDate":"2013-11-06"},
    {"id":"xy1","name":"XY","cards":146,"releaseDate":"2014-02-05"},
    {"id":"xy2","name":"Flashfire","cards":106,"releaseDate":"2014-05-07"},
    {"id":"xy3","name":"Furious Fists","cards":111,"releaseDate":"2014-08-13"},
    {"id":"xy4","name":"Phantom Forces","cards":119,"releaseDate":"2014-11-05"},
    {"id":"xy5","name":"Primal Clash","cards":160,"releaseDate":"2015-02-04"},
    {"id":"xy6","name":"Roaring Skies","cards":108,"releaseDate":"2015-05-06"},
    {"id":"xy7","name":"Ancient Origins","cards":98,"releaseDate":"2015-08-12"},
    {"id":"xy8","name":"BREAKthrough","cards":162,"releaseDate":"2015-11-04"},
    {"id":"xy9","name":"BREAKpoint","cards":122,"releaseDate":"2016-02-03"},
    {"id":"g1","name":"Generations","cards":83,"releaseDate":"2016-02-22"},
    {"id":"xy10","name":"Fates Collide","cards":124,"releaseDate":"2016-05-02"},
    {"id":"xy11","name":"Steam Siege","cards":114,"releaseDate":"2016-08-03"},
    {"id":"xy12","name":"Evolutions","cards":108,"releaseDate":"2016-11-02"},
    {"id":"sm1","name":"Sun & Moon","cards":149,"releaseDate":"2017-02-03"},
    {"id":"sm2","name":"Guardians Rising","cards":145,"releaseDate":"2017-05-05"},
    {"id":"sm3","name":"Burning Shadows","cards":147,"releaseDate":"2017-08-04"},
    {"id":"sm4","name":"Crimson Invasion","cards":111,"releaseDate":"2017-11-03"},
    {"id":"sm5","name":"Ultra Prism","cards":156,"releaseDate":"2018-02-02"},
    {"id":"sm6","name":"Forbidden Light","cards":131,"releaseDate":"2018-05-04"},
    {"id":"sm7","name":"Celestial Storm","cards":168,"releaseDate":"2018-08-03"},
    {"id":"sm8","name":"Lost Thunder","cards":214,"releaseDate":"2018-11-02"},
    {"id":"sm9","name":"Team Up","cards":181,"releaseDate":"2019-02-01"},
    {"id":"sm10","name":"Unbroken Bonds","cards":214,"releaseDate":"2019-05-03"},
    {"id":"sm11","name":"Unified Minds","cards":236,"releaseDate":"2019-08-02"},
    {"id":"sm12","name":"Cosmic Eclipse","cards":236,"releaseDate":"2019-11-01"},
    {"id":"swsh1","name":"Sword & Shield","cards":202,"releaseDate":"2020-02-07"},
    {"id":"swsh2","name":"Rebel Clash","cards":192,"releaseDate":"2020-05-01"},
    {"id":"swsh3","name":"Darkness Ablaze","cards":189,"releaseDate":"2020-08-14"},
    {"id":"swsh3.5","name":"Champion's Path","cards":73,"releaseDate":"2020-09-25"},
    {"id":"swsh4","name":"Vivid Voltage","cards":185,"releaseDate":"2020-11-13"},
    {"id":"swsh4.5","name":"Shining Fates","cards":72,"releaseDate":"2021-02-19"},
    {"id":"swsh5","name":"Battle Styles","cards":163,"releaseDate":"2021-03-19"},
    {"id":"swsh6","name":"Chilling Reign","cards":198,"releaseDate":"2021-06-18"},
    {"id":"swsh7","name":"Evolving Skies","cards":203,"releaseDate":"2021-08-27"},
    {"id":"cel25","name":"Celebrations","cards":25,"releaseDate":"2021-10-08"},
    {"id":"swsh8","name":"Fusion Strike","cards":264,"releaseDate":"2021-11-12"},
    {"id":"swsh9","name":"Brilliant Stars","cards":172,"releaseDate":"2022-02-25"},
    {"id":"swsh10","name":"Astral Radiance","cards":189,"releaseDate":"2022-05-27"},
    {"id":"swsh10.5","name":"Pokemon GO","cards":78,"releaseDate":"2022-07-01"},
    {"id":"swsh11","name":"Lost Origin","cards":196,"releaseDate":"2022-09-09"},
    {"id":"swsh12","name":"Silver Tempest","cards":195,"releaseDate":"2022-11-11"},
    {"id":"swsh12.5","name":"Crown Zenith","cards":159,"releaseDate":"2023-01-20"},
    {"id":"sv01","name":"Scarlet & Violet","cards":198,"releaseDate":"2023-03-31"},
    {"id":"sv02","name":"Paldea Evolved","cards":193,"releaseDate":"2023-06-09"},
    {"id":"sv03","name":"Obsidian Flames","cards":197,"releaseDate":"2023-08-11"},
    {"id":"sv03.5","name":"Pokemon 151","cards":165,"releaseDate":"2023-09-22"},
    {"id":"sv04","name":"Paradox Rift","cards":182,"releaseDate":"2023-11-03"},
    {"id":"sv04.5","name":"Paldean Fates","cards":91,"releaseDate":"2024-01-26"},
    {"id":"sv05","name":"Temporal Forces","cards":162,"releaseDate":"2024-03-22"},
    {"id":"sv06","name":"Twilight Masquerade","cards":167,"releaseDate":"2024-05-24"},
    {"id":"sv06.5","name":"Shrouded Fable","cards":64,"releaseDate":"2024-08-02"},
    {"id":"sv07","name":"Stellar Crown","cards":142,"releaseDate":"2024-09-13"},
    {"id":"sv08","name":"Surging Sparks","cards":191,"releaseDate":"2024-11-08"},
    {"id":"sv08.5","name":"Prismatic Evolutions","cards":131,"releaseDate":"2025-01-17"},
    {"id":"sv09","name":"Journey Together","cards":159,"releaseDate":"2025-03-28"},
    {"id":"sv10","name":"Destined Rivals","cards":182,"releaseDate":"2025-05-30"},
    {"id":"sv10.5w","name":"White Flare","cards":86,"releaseDate":"2025-07-18"},
    {"id":"sv10.5b","name":"Black Bolt","cards":86,"releaseDate":"2025-07-18"},
    {"id":"me01","name":"Mega Evolution","cards":132,"releaseDate":"2025-09-26"},
    {"id":"me02","name":"Phantasmal Flames","cards":94,"releaseDate":"2025-11-14"},
    {"id":"me02.5","name":"Ascended Heroes","cards":217,"releaseDate":"2026-01-30"},
    {"id":"me03","name":"Perfect Order","cards":88,"releaseDate":"2026-03-27"},
    {"id":"me04","name":"Chaos Rising","cards":86,"releaseDate":"2026-05-22"},
]

# Base Set cards from API
BASE_SET_CARDS = [
    {"id":"base1-1","localId":"1","name":"Alakazam","category":"Pokémon","supertype":"Pokémon","hp":"100","types":["Psychic"],"stage":"Stage 2","evolvesFrom":"Kadabra"},
    {"id":"base1-2","localId":"2","name":"Blastoise","category":"Pokémon","supertype":"Pokémon","hp":"100","types":["Water"],"stage":"Stage 2","evolvesFrom":"Wartortle"},
    {"id":"base1-3","localId":"3","name":"Chansey","category":"Pokémon","supertype":"Pokémon","hp":"120","types":["Colorless"],"stage":"Basic"},
    {"id":"base1-4","localId":"4","name":"Charizard","category":"Pokémon","supertype":"Pokémon","hp":"120","types":["Fire","Colorless"],"stage":"Stage 2","evolvesFrom":"Charmeleon"},
    {"id":"base1-5","localId":"5","name":"Clefairy","category":"Pokémon","supertype":"Pokémon","hp":"70","types":["Colorless"],"stage":"Basic"},
    {"id":"base1-6","localId":"6","name":"Gyarados","category":"Pokémon","supertype":"Pokémon","hp":"100","types":["Water"],"stage":"Stage 1","evolvesFrom":"Magikarp"},
    {"id":"base1-7","localId":"7","name":"Hitmonchan","category":"Pokémon","supertype":"Pokémon","hp":"70","types":["Fighting"],"stage":"Basic"},
    {"id":"base1-8","localId":"8","name":"Machamp","category":"Pokémon","supertype":"Pokémon","hp":"100","types":["Fighting"],"stage":"Stage 2","evolvesFrom":"Machoke"},
    {"id":"base1-9","localId":"9","name":"Magneton","category":"Pokémon","supertype":"Pokémon","hp":"90","types":["Lightning"],"stage":"Stage 1","evolvesFrom":"Magnemite"},
    {"id":"base1-10","localId":"10","name":"Mewtwo","category":"Pokémon","supertype":"Pokémon","hp":"60","types":["Psychic"],"stage":"Basic"},
    {"id":"base1-11","localId":"11","name":"Nidoking","category":"Pokémon","supertype":"Pokémon","hp":"90","types":["Grass","Fighting"],"stage":"Stage 2","evolvesFrom":"Nidorino"},
    {"id":"base1-12","localId":"12","name":"Ninetales","category":"Pokémon","supertype":"Pokémon","hp":"80","types":["Fire"],"stage":"Stage 1","evolvesFrom":"Vulpix"},
    {"id":"base1-13","localId":"13","name":"Poliwrath","category":"Pokémon","supertype":"Pokémon","hp":"80","types":["Water","Fighting"],"stage":"Stage 2","evolvesFrom":"Poliwhirl"},
    {"id":"base1-14","localId":"14","name":"Raichu","category":"Pokémon","supertype":"Pokémon","hp":"80","types":["Lightning"],"stage":"Stage 1","evolvesFrom":"Pikachu"},
    {"id":"base1-15","localId":"15","name":"Venusaur","category":"Pokémon","supertype":"Pokémon","hp":"100","types":["Grass"],"stage":"Stage 2","evolvesFrom":"Ivysaur"},
    {"id":"base1-16","localId":"16","name":"Zapdos","category":"Pokémon","supertype":"Pokémon","hp":"90","types":["Lightning"],"stage":"Basic"},
    {"id":"base1-17","localId":"17","name":"Beedrill","category":"Pokémon","supertype":"Pokémon","hp":"80","types":["Grass","Fighting"],"stage":"Stage 2","evolvesFrom":"Kakuna"},
    {"id":"base1-18","localId":"18","name":"Dragonair","category":"Pokémon","supertype":"Pokémon","hp":"80","types":["Colorless"],"stage":"Stage 1","evolvesFrom":"Dratini"},
    {"id":"base1-19","localId":"19","name":"Dugtrio","category":"Pokémon","supertype":"Pokémon","hp":"70","types":["Fighting"],"stage":"Stage 1","evolvesFrom":"Diglett"},
    {"id":"base1-20","localId":"20","name":"Electabuzz","category":"Pokémon","supertype":"Pokémon","hp":"70","types":["Lightning"],"stage":"Basic"},
    {"id":"base1-21","localId":"21","name":"Electrode","category":"Pokémon","supertype":"Pokémon","hp":"70","types":["Lightning"],"stage":"Stage 1","evolvesFrom":"Voltorb"},
    {"id":"base1-22","localId":"22","name":"Pidgeotto","category":"Pokémon","supertype":"Pokémon","hp":"60","types":["Colorless"],"stage":"Stage 1","evolvesFrom":"Pidgey"},
    {"id":"base1-23","localId":"23","name":"Arcanine","category":"Pokémon","supertype":"Pokémon","hp":"70","types":["Fire"],"stage":"Stage 1","evolvesFrom":"Growlithe"},
    {"id":"base1-24","localId":"24","name":"Charmeleon","category":"Pokémon","supertype":"Pokémon","hp":"70","types":["Fire"],"stage":"Stage 1","evolvesFrom":"Charmander"},
    {"id":"base1-25","localId":"25","name":"Dewgong","category":"Pokémon","supertype":"Pokémon","hp":"80","types":["Water"],"stage":"Stage 1","evolvesFrom":"Seel"},
    {"id":"base1-26","localId":"26","name":"Dratini","category":"Pokémon","supertype":"Pokémon","hp":"40","types":["Colorless"],"stage":"Basic"},
    {"id":"base1-27","localId":"27","name":"Farfetch'd","category":"Pokémon","supertype":"Pokémon","hp":"50","types":["Colorless"],"stage":"Basic"},
    {"id":"base1-28","localId":"28","name":"Growlithe","category":"Pokémon","supertype":"Pokémon","hp":"50","types":["Fire"],"stage":"Basic"},
    {"id":"base1-29","localId":"29","name":"Haunter","category":"Pokémon","supertype":"Pokémon","hp":"60","types":["Psychic"],"stage":"Stage 1","evolvesFrom":"Gastly"},
    {"id":"base1-30","localId":"30","name":"Ivysaur","category":"Pokémon","supertype":"Pokémon","hp":"60","types":["Grass"],"stage":"Stage 1","evolvesFrom":"Bulbasaur"},
    {"id":"base1-31","localId":"31","name":"Jynx","category":"Pokémon","supertype":"Pokémon","hp":"50","types":["Psychic"],"stage":"Basic"},
    {"id":"base1-32","localId":"32","name":"Kadabra","category":"Pokémon","supertype":"Pokémon","hp":"60","types":["Psychic"],"stage":"Stage 1","evolvesFrom":"Abra"},
    {"id":"base1-33","localId":"33","name":"Kakuna","category":"Pokémon","supertype":"Pokémon","hp":"50","types":["Grass"],"stage":"Stage 1","evolvesFrom":"Weedle"},
    {"id":"base1-34","localId":"34","name":"Machoke","category":"Pokémon","supertype":"Pokémon","hp":"80","types":["Fighting"],"stage":"Stage 1","evolvesFrom":"Machop"},
    {"id":"base1-35","localId":"35","name":"Magikarp","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Water"],"stage":"Basic"},
    {"id":"base1-36","localId":"36","name":"Magmar","category":"Pokémon","supertype":"Pokémon","hp":"50","types":["Fire"],"stage":"Basic"},
    {"id":"base1-37","localId":"37","name":"Nidorino","category":"Pokémon","supertype":"Pokémon","hp":"60","types":["Grass"],"stage":"Stage 1","evolvesFrom":"Nidoran♂"},
    {"id":"base1-38","localId":"38","name":"Poliwhirl","category":"Pokémon","supertype":"Pokémon","hp":"60","types":["Water"],"stage":"Stage 1","evolvesFrom":"Poliwag"},
    {"id":"base1-39","localId":"39","name":"Porygon","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Colorless"],"stage":"Basic"},
    {"id":"base1-40","localId":"40","name":"Raticate","category":"Pokémon","supertype":"Pokémon","hp":"60","types":["Colorless"],"stage":"Stage 1","evolvesFrom":"Rattata"},
    {"id":"base1-41","localId":"41","name":"Seel","category":"Pokémon","supertype":"Pokémon","hp":"60","types":["Water"],"stage":"Basic"},
    {"id":"base1-42","localId":"42","name":"Wartortle","category":"Pokémon","supertype":"Pokémon","hp":"70","types":["Water"],"stage":"Stage 1","evolvesFrom":"Squirtle"},
    {"id":"base1-43","localId":"43","name":"Abra","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Psychic"],"stage":"Basic"},
    {"id":"base1-44","localId":"44","name":"Bulbasaur","category":"Pokémon","supertype":"Pokémon","hp":"40","types":["Grass"],"stage":"Basic"},
    {"id":"base1-45","localId":"45","name":"Caterpie","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Grass"],"stage":"Basic"},
    {"id":"base1-46","localId":"46","name":"Charmander","category":"Pokémon","supertype":"Pokémon","hp":"40","types":["Fire"],"stage":"Basic"},
    {"id":"base1-47","localId":"47","name":"Diglett","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Fighting"],"stage":"Basic"},
    {"id":"base1-48","localId":"48","name":"Doduo","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Colorless"],"stage":"Basic"},
    {"id":"base1-49","localId":"49","name":"Drowzee","category":"Pokémon","supertype":"Pokémon","hp":"50","types":["Psychic"],"stage":"Basic"},
    {"id":"base1-50","localId":"50","name":"Gastly","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Psychic"],"stage":"Basic"},
    {"id":"base1-51","localId":"51","name":"Koffing","category":"Pokémon","supertype":"Pokémon","hp":"50","types":["Grass"],"stage":"Basic"},
    {"id":"base1-52","localId":"52","name":"Machop","category":"Pokémon","supertype":"Pokémon","hp":"50","types":["Fighting"],"stage":"Basic"},
    {"id":"base1-53","localId":"53","name":"Magnemite","category":"Pokémon","supertype":"Pokémon","hp":"40","types":["Lightning"],"stage":"Basic"},
    {"id":"base1-54","localId":"54","name":"Metapod","category":"Pokémon","supertype":"Pokémon","hp":"50","types":["Grass"],"stage":"Stage 1","evolvesFrom":"Caterpie"},
    {"id":"base1-55","localId":"55","name":"Nidoran♂","category":"Pokémon","supertype":"Pokémon","hp":"40","types":["Grass"],"stage":"Basic"},
    {"id":"base1-56","localId":"56","name":"Onix","category":"Pokémon","supertype":"Pokémon","hp":"70","types":["Fighting"],"stage":"Basic"},
    {"id":"base1-57","localId":"57","name":"Pidgey","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Colorless"],"stage":"Basic"},
    {"id":"base1-58","localId":"58","name":"Pikachu","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Lightning"],"stage":"Basic"},
    {"id":"base1-59","localId":"59","name":"Poliwag","category":"Pokémon","supertype":"Pokémon","hp":"40","types":["Water"],"stage":"Basic"},
    {"id":"base1-60","localId":"60","name":"Ponyta","category":"Pokémon","supertype":"Pokémon","hp":"40","types":["Fire"],"stage":"Basic"},
    {"id":"base1-61","localId":"61","name":"Rattata","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Colorless"],"stage":"Basic"},
    {"id":"base1-62","localId":"62","name":"Sandshrew","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Fighting"],"stage":"Basic"},
    {"id":"base1-63","localId":"63","name":"Squirtle","category":"Pokémon","supertype":"Pokémon","hp":"40","types":["Water"],"stage":"Basic"},
    {"id":"base1-64","localId":"64","name":"Starmie","category":"Pokémon","supertype":"Pokémon","hp":"60","types":["Water"],"stage":"Stage 1","evolvesFrom":"Staryu"},
    {"id":"base1-65","localId":"65","name":"Staryu","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Water"],"stage":"Basic"},
    {"id":"base1-66","localId":"66","name":"Tangela","category":"Pokémon","supertype":"Pokémon","hp":"50","types":["Grass"],"stage":"Basic"},
    {"id":"base1-67","localId":"67","name":"Voltorb","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Lightning"],"stage":"Basic"},
    {"id":"base1-68","localId":"68","name":"Vulpix","category":"Pokémon","supertype":"Pokémon","hp":"40","types":["Fire"],"stage":"Basic"},
    {"id":"base1-69","localId":"69","name":"Weedle","category":"Pokémon","supertype":"Pokémon","hp":"30","types":["Grass"],"stage":"Basic"},
    {"id":"base1-70","localId":"70","name":"Clefairy Doll","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-71","localId":"71","name":"Computer Search","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-72","localId":"72","name":"Devolution Spray","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-73","localId":"73","name":"Impostor Professor Oak","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-74","localId":"74","name":"Item Finder","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-75","localId":"75","name":"Lass","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-76","localId":"76","name":"Pokemon Breeder","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-77","localId":"77","name":"Pokemon Trader","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-78","localId":"78","name":"Scoop Up","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-79","localId":"79","name":"Super Energy Removal","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-80","localId":"80","name":"Defender","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-81","localId":"81","name":"Energy Retrieval","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-82","localId":"82","name":"Full Heal","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-83","localId":"83","name":"Maintenance","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-84","localId":"84","name":"PlusPower","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-85","localId":"85","name":"Pokemon Center","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-86","localId":"86","name":"Pokemon Flute","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-87","localId":"87","name":"Pokedex","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-88","localId":"88","name":"Professor Oak","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-89","localId":"89","name":"Revive","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-90","localId":"90","name":"Super Potion","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-91","localId":"91","name":"Bill","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-92","localId":"92","name":"Energy Removal","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-93","localId":"93","name":"Gust of Wind","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-94","localId":"94","name":"Potion","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-95","localId":"95","name":"Switch","category":"Trainer","supertype":"Trainer"},
    {"id":"base1-96","localId":"96","name":"Double Colorless Energy","category":"Energy","supertype":"Energy"},
    {"id":"base1-97","localId":"97","name":"Fighting Energy","category":"Energy","supertype":"Energy"},
    {"id":"base1-98","localId":"98","name":"Fire Energy","category":"Energy","supertype":"Energy"},
    {"id":"base1-99","localId":"99","name":"Grass Energy","category":"Energy","supertype":"Energy"},
    {"id":"base1-100","localId":"100","name":"Lightning Energy","category":"Energy","supertype":"Energy"},
    {"id":"base1-101","localId":"101","name":"Psychic Energy","category":"Energy","supertype":"Energy"},
    {"id":"base1-102","localId":"102","name":"Water Energy","category":"Energy","supertype":"Energy"},
]


def save_sets():
    with open(f"{OUTPUT_DIR}/tcgdex_sets.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "cards", "releaseDate"])
        writer.writeheader()
        for s in SETS_DATA:
            writer.writerow(s)
    print(f"Saved {len(SETS_DATA)} sets to tcgdex_sets.csv")

    with open(f"{OUTPUT_DIR}/tcgdex_sets.json", "w") as f:
        json.dump(SETS_DATA, f, indent=2)
    print(f"Saved {len(SETS_DATA)} sets to tcgdex_sets.json")


def save_cards():
    with open(f"{OUTPUT_DIR}/tcgdex_base_set_cards.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "localId", "name", "category", "supertype", "hp", "types", "stage", "evolvesFrom"])
        writer.writeheader()
        for c in BASE_SET_CARDS:
            writer.writerow({
                "id": c.get("id", ""),
                "localId": c.get("localId", ""),
                "name": c.get("name", ""),
                "category": c.get("category", ""),
                "supertype": c.get("supertype", ""),
                "hp": c.get("hp", ""),
                "types": ",".join(c.get("types", [])) if isinstance(c.get("types"), list) else c.get("types", ""),
                "stage": c.get("stage", ""),
                "evolvesFrom": c.get("evolvesFrom", ""),
            })
    print(f"Saved {len(BASE_SET_CARDS)} Base Set cards to tcgdex_base_set_cards.csv")

    with open(f"{OUTPUT_DIR}/tcgdex_base_set_cards.json", "w") as f:
        json.dump(BASE_SET_CARDS, f, indent=2)
    print(f"Saved {len(BASE_SET_CARDS)} Base Set cards to tcgdex_base_set_cards.json")


if __name__ == "__main__":
    print("=" * 60)
    print("TCGdex Data Saver")
    print("Source: api.tcgdex.net/v2/en")
    print("=" * 60)
    save_sets()
    save_cards()

    total_cards = sum(s["cards"] for s in SETS_DATA)
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Sets: {len(SETS_DATA)}")
    print(f"Total cards across all sets: {total_cards}")
    print(f"Base Set cards saved: {len(BASE_SET_CARDS)}")

    print(f"\nFiles created:")
    print(f"  tcgdex_sets.csv           - {len(SETS_DATA)} sets")
    print(f"  tcgdex_sets.json          - {len(SETS_DATA)} sets (JSON)")
    print(f"  tcgdex_base_set_cards.csv - {len(BASE_SET_CARDS)} cards")
    print(f"  tcgdex_base_set_cards.json - {len(BASE_SET_CARDS)} cards (JSON)")

    print(f"\nNote: To get all cards for all sets, run the full scraper")
    print(f"with the webfetch tool or on a machine with SSL working.")

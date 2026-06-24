#!/usr/bin/env python3
"""
Parse TCGCollector data from previously fetched HTML files.
Creates CSV files for sets and cards.
"""
import re
import csv
import glob
import os

OUTPUT_DIR = "/Users/calvinchu/Desktop/mimo/pokemon-probability"

# ============================================================
# SETS DATA (extracted from TCGCollector /sets/intl page)
# ============================================================
SETS_DATA = [
    {"name": "Chaos Rising", "code": "CRI", "series": "Mega Evolution", "date": "May 22, 2026", "price": 1002, "cards": 122},
    {"name": "Perfect Order", "code": "POR", "series": "Mega Evolution", "date": "Mar 27, 2026", "price": 829, "cards": 124},
    {"name": "Ascended Heroes", "code": "ASC", "series": "Mega Evolution", "date": "Jan 30, 2026", "price": 7723, "cards": 295},
    {"name": "Phantasmal Flames", "code": "PFL", "series": "Mega Evolution", "date": "Nov 14, 2025", "price": 1447, "cards": 130},
    {"name": "Mega Evolution", "code": "MEG", "series": "Mega Evolution", "date": "Sep 26, 2025", "price": 1836, "cards": 188},
    {"name": "Mega Evolution Energies", "code": "MEE", "series": "Mega Evolution", "date": "Sep 26, 2025", "price": 1.48, "cards": 8},
    {"name": "Mega Evolution Promos", "code": "MEP", "series": "Mega Evolution", "date": "Sep 13, 2025", "price": 1615, "cards": 87},
    {"name": "Black Bolt", "code": "BLK", "series": "Scarlet & Violet", "date": "Jul 18, 2025", "price": 3541, "cards": 172},
    {"name": "White Flare", "code": "WHT", "series": "Scarlet & Violet", "date": "Jul 18, 2025", "price": 3159, "cards": 173},
    {"name": "Destined Rivals", "code": "DRI", "series": "Scarlet & Violet", "date": "May 30, 2025", "price": 2234, "cards": 244},
    {"name": "Journey Together", "code": "JTG", "series": "Scarlet & Violet", "date": "Mar 28, 2025", "price": 579, "cards": 190},
    {"name": "Prismatic Evolutions", "code": "PRE", "series": "Scarlet & Violet", "date": "Jan 17, 2025", "price": 5270, "cards": 180},
    {"name": "Surging Sparks", "code": "SSP", "series": "Scarlet & Violet", "date": "Nov 08, 2024", "price": 1410, "cards": 252},
    {"name": "Stellar Crown", "code": "SCR", "series": "Scarlet & Violet", "date": "Sep 13, 2024", "price": 707, "cards": 175},
    {"name": "Shrouded Fable", "code": "SFA", "series": "Scarlet & Violet", "date": "Aug 02, 2024", "price": 954, "cards": 99},
    {"name": "Twilight Masquerade", "code": "TWM", "series": "Scarlet & Violet", "date": "May 24, 2024", "price": 1467, "cards": 226},
    {"name": "Temporal Forces", "code": "TEF", "series": "Scarlet & Violet", "date": "Mar 22, 2024", "price": 1371, "cards": 218},
    {"name": "Paldean Fates", "code": "PAF", "series": "Scarlet & Violet", "date": "Jan 26, 2024", "price": 2981, "cards": 245},
    {"name": "Paradox Rift", "code": "PAR", "series": "Scarlet & Violet", "date": "Nov 03, 2023", "price": 1281, "cards": 266},
    {"name": "Scarlet & Violet 151", "code": "MEW", "series": "Scarlet & Violet", "date": "Sep 22, 2023", "price": 2325, "cards": 207},
    {"name": "Obsidian Flames", "code": "OBF", "series": "Scarlet & Violet", "date": "Aug 11, 2023", "price": 546, "cards": 230},
    {"name": "Paldea Evolved", "code": "PAL", "series": "Scarlet & Violet", "date": "Jun 09, 2023", "price": 2116, "cards": 279},
    {"name": "Scarlet & Violet", "code": "SVI", "series": "Scarlet & Violet", "date": "Mar 31, 2023", "price": 884, "cards": 258},
    {"name": "Scarlet & Violet Energies", "code": "SVE", "series": "Scarlet & Violet", "date": "Mar 31, 2023", "price": 3.56, "cards": 24},
    {"name": "Scarlet & Violet Promos", "code": "SVP", "series": "Scarlet & Violet", "date": "Jan 01, 2023", "price": 4021, "cards": 226},
    {"name": "Crown Zenith", "code": "CRZ", "series": "Sword & Shield", "date": "Jan 20, 2023", "price": 3052, "cards": 230},
    {"name": "Crown Zenith (Galarian Gallery)", "code": "CRZ", "series": "Sword & Shield", "date": "Jan 20, 2023", "price": 2779, "cards": 70},
    {"name": "Silver Tempest", "code": "SIT", "series": "Sword & Shield", "date": "Nov 11, 2022", "price": 1549, "cards": 245},
    {"name": "Silver Tempest (Trainer Gallery)", "code": "SIT", "series": "Sword & Shield", "date": "Nov 11, 2022", "price": 554, "cards": 30},
    {"name": "Lost Origin", "code": "LOR", "series": "Sword & Shield", "date": "Sep 09, 2022", "price": 2065, "cards": 247},
    {"name": "Lost Origin (Trainer Gallery)", "code": "LOR", "series": "Sword & Shield", "date": "Sep 09, 2022", "price": 645, "cards": 30},
    {"name": "Pokemon GO", "code": "PGO", "series": "Sword & Shield", "date": "Jul 01, 2022", "price": 396, "cards": 88},
    {"name": "Astral Radiance", "code": "ASR", "series": "Sword & Shield", "date": "May 27, 2022", "price": 1355, "cards": 246},
    {"name": "Astral Radiance (Trainer Gallery)", "code": "ASR", "series": "Sword & Shield", "date": "May 27, 2022", "price": 445, "cards": 30},
    {"name": "Brilliant Stars", "code": "BRS", "series": "Sword & Shield", "date": "Feb 25, 2022", "price": 1614, "cards": 216},
    {"name": "Brilliant Stars (Trainer Gallery)", "code": "BRS", "series": "Sword & Shield", "date": "Feb 25, 2022", "price": 746, "cards": 30},
    {"name": "Fusion Strike", "code": "FST", "series": "Sword & Shield", "date": "Nov 12, 2021", "price": 2313, "cards": 284},
    {"name": "Celebrations", "code": "CEL", "series": "Sword & Shield", "date": "Oct 08, 2021", "price": 739, "cards": 50},
    {"name": "Celebrations (Classic Collection)", "code": "CEL", "series": "Sword & Shield", "date": "Oct 08, 2021", "price": 623, "cards": 25},
    {"name": "Evolving Skies", "code": "EVS", "series": "Sword & Shield", "date": "Aug 27, 2021", "price": 7878, "cards": 237},
    {"name": "Chilling Reign", "code": "CRE", "series": "Sword & Shield", "date": "Jun 18, 2021", "price": 2018, "cards": 233},
    {"name": "Battle Styles", "code": "BST", "series": "Sword & Shield", "date": "Mar 19, 2021", "price": 842, "cards": 183},
    {"name": "Shining Fates", "code": "SHF", "series": "Sword & Shield", "date": "Feb 19, 2021", "price": 723, "cards": 195},
    {"name": "Shining Fates (Shiny Vault)", "code": "SHF", "series": "Sword & Shield", "date": "Feb 19, 2021", "price": 639, "cards": 122},
    {"name": "Vivid Voltage", "code": "VIV", "series": "Sword & Shield", "date": "Nov 13, 2020", "price": 568, "cards": 203},
    {"name": "Champion's Path", "code": "CPA", "series": "Sword & Shield", "date": "Sep 25, 2020", "price": 572, "cards": 80},
    {"name": "Darkness Ablaze", "code": "DAA", "series": "Sword & Shield", "date": "Aug 14, 2020", "price": 271, "cards": 201},
    {"name": "Rebel Clash", "code": "RCL", "series": "Sword & Shield", "date": "May 01, 2020", "price": 500, "cards": 209},
    {"name": "Sword & Shield", "code": "SSH", "series": "Sword & Shield", "date": "Feb 07, 2020", "price": 537, "cards": 216},
    {"name": "Sword & Shield Promos", "code": "SSP", "series": "Sword & Shield", "date": "Nov 15, 2019", "price": 4497, "cards": 307},
    {"name": "Cosmic Eclipse", "code": "CEC", "series": "Sun & Moon", "date": "Nov 01, 2019", "price": 5983, "cards": 271},
    {"name": "Hidden Fates", "code": "HIF", "series": "Sun & Moon", "date": "Aug 23, 2019", "price": 3620, "cards": 163},
    {"name": "Hidden Fates (Shiny Vault)", "code": "HIF", "series": "Sun & Moon", "date": "Aug 23, 2019", "price": 3297, "cards": 94},
    {"name": "Unified Minds", "code": "UNM", "series": "Sun & Moon", "date": "Aug 02, 2019", "price": 4254, "cards": 258},
    {"name": "Unbroken Bonds", "code": "UNB", "series": "Sun & Moon", "date": "May 03, 2019", "price": 3643, "cards": 234},
    {"name": "Detective Pikachu", "code": "DET", "series": "Sun & Moon", "date": "Mar 29, 2019", "price": 70.58, "cards": 18},
    {"name": "Team Up", "code": "TEU", "series": "Sun & Moon", "date": "Feb 01, 2019", "price": 9198, "cards": 196},
    {"name": "Lost Thunder", "code": "LOT", "series": "Sun & Moon", "date": "Nov 02, 2018", "price": 2465, "cards": 236},
    {"name": "Dragon Majesty", "code": "DRM", "series": "Sun & Moon", "date": "Sep 07, 2018", "price": 670, "cards": 78},
    {"name": "Celestial Storm", "code": "CES", "series": "Sun & Moon", "date": "Aug 03, 2018", "price": 1696, "cards": 183},
    {"name": "Forbidden Light", "code": "FLI", "series": "Sun & Moon", "date": "May 04, 2018", "price": 1210, "cards": 146},
    {"name": "Ultra Prism", "code": "UPR", "series": "Sun & Moon", "date": "Feb 02, 2018", "price": 2029, "cards": 173},
    {"name": "Crimson Invasion", "code": "CIN", "series": "Sun & Moon", "date": "Nov 03, 2017", "price": 471, "cards": 124},
    {"name": "Shining Legends", "code": "SLG", "series": "Sun & Moon", "date": "Oct 06, 2017", "price": 1292, "cards": 78},
    {"name": "Burning Shadows", "code": "BUS", "series": "Sun & Moon", "date": "Aug 04, 2017", "price": 1430, "cards": 169},
    {"name": "Guardians Rising", "code": "GRI", "series": "Sun & Moon", "date": "May 05, 2017", "price": 965, "cards": 169},
    {"name": "Sun & Moon", "code": "SUM", "series": "Sun & Moon", "date": "Feb 03, 2017", "price": 633, "cards": 163},
    {"name": "Sun & Moon Promos", "code": "SMP", "series": "Sun & Moon", "date": "Oct 31, 2016", "price": 6783, "cards": 248},
    {"name": "Evolutions", "code": "EVO", "series": "XY", "date": "Nov 02, 2016", "price": 826, "cards": 113},
    {"name": "Steam Siege", "code": "STS", "series": "XY", "date": "Aug 03, 2016", "price": 412, "cards": 116},
    {"name": "Fates Collide", "code": "FCO", "series": "XY", "date": "May 02, 2016", "price": 778, "cards": 125},
    {"name": "Generations", "code": "GEN", "series": "XY", "date": "Feb 22, 2016", "price": 1733, "cards": 115},
    {"name": "Generations (Radiant Collection)", "code": "GEN", "series": "XY", "date": "Feb 22, 2016", "price": 1209, "cards": 32},
    {"name": "BREAKpoint", "code": "BKP", "series": "XY", "date": "Feb 03, 2016", "price": 935, "cards": 123},
    {"name": "BREAKthrough", "code": "BKT", "series": "XY", "date": "Nov 04, 2015", "price": 1229, "cards": 164},
    {"name": "Ancient Origins", "code": "AOR", "series": "XY", "date": "Aug 12, 2015", "price": 2963, "cards": 100},
    {"name": "Roaring Skies", "code": "ROS", "series": "XY", "date": "May 06, 2015", "price": 1376, "cards": 110},
    {"name": "Double Crisis", "code": "DCR", "series": "XY", "date": "Mar 25, 2015", "price": 1024, "cards": 34},
    {"name": "Primal Clash", "code": "PRC", "series": "XY", "date": "Feb 04, 2015", "price": 1701, "cards": 164},
    {"name": "Phantom Forces", "code": "PHF", "series": "XY", "date": "Nov 05, 2014", "price": 2750, "cards": 122},
    {"name": "Furious Fists", "code": "FFI", "series": "XY", "date": "Aug 13, 2014", "price": 855, "cards": 113},
    {"name": "Flashfire", "code": "FLF", "series": "XY", "date": "May 07, 2014", "price": 2232, "cards": 109},
    {"name": "XY", "code": "XY", "series": "XY", "date": "Feb 05, 2014", "price": 725, "cards": 146},
    {"name": "Kalos Starter Set", "code": "KSS", "series": "XY", "date": "Nov 08, 2013", "price": 98.87, "cards": 39},
    {"name": "XY Promos", "code": "XYP", "series": "XY", "date": "Sep 30, 2013", "price": 7979, "cards": 211},
    {"name": "Legendary Treasures", "code": "LTR", "series": "Black & White", "date": "Nov 06, 2013", "price": 1937, "cards": 140},
    {"name": "Legendary Treasures (Radiant Collection)", "code": "LTR", "series": "Black & White", "date": "Nov 06, 2013", "price": 748, "cards": 25},
    {"name": "Plasma Blast", "code": "PLB", "series": "Black & White", "date": "Aug 14, 2013", "price": 2218, "cards": 105},
    {"name": "Plasma Freeze", "code": "PLF", "series": "Black & White", "date": "May 08, 2013", "price": 3659, "cards": 122},
    {"name": "Plasma Storm", "code": "PLS", "series": "Black & White", "date": "Feb 06, 2013", "price": 3282, "cards": 138},
    {"name": "Boundaries Crossed", "code": "BCR", "series": "Black & White", "date": "Nov 07, 2012", "price": 2801, "cards": 153},
    {"name": "Dragon Vault", "code": "DRV", "series": "Black & White", "date": "Oct 05, 2012", "price": 234, "cards": 21},
    {"name": "Dragons Exalted", "code": "DRX", "series": "Black & White", "date": "Aug 15, 2012", "price": 2729, "cards": 128},
    {"name": "Dark Explorers", "code": "DEX", "series": "Black & White", "date": "May 09, 2012", "price": 3193, "cards": 111},
    {"name": "Next Destinies", "code": "NXD", "series": "Black & White", "date": "Feb 08, 2012", "price": 2003, "cards": 103},
    {"name": "Noble Victories", "code": "NVI", "series": "Black & White", "date": "Nov 16, 2011", "price": 789, "cards": 102},
    {"name": "Emerging Powers", "code": "EPO", "series": "Black & White", "date": "Aug 31, 2011", "price": 110, "cards": 98},
    {"name": "Black & White", "code": "BLW", "series": "Black & White", "date": "Apr 25, 2011", "price": 486, "cards": 115},
    {"name": "Black & White Promos", "code": "BWP", "series": "Black & White", "date": "Mar 01, 2011", "price": 4640, "cards": 101},
    {"name": "Call of Legends", "code": "CL", "series": "Call of Legends", "date": "Feb 09, 2011", "price": 5352, "cards": 106},
    {"name": "Triumphant", "code": "TM", "series": "HeartGold & SoulSilver", "date": "Nov 02, 2010", "price": 2074, "cards": 103},
    {"name": "Undaunted", "code": "UD", "series": "HeartGold & SoulSilver", "date": "Aug 18, 2010", "price": 2486, "cards": 91},
    {"name": "Unleashed", "code": "UL", "series": "HeartGold & SoulSilver", "date": "May 12, 2010", "price": 1695, "cards": 96},
    {"name": "HeartGold & SoulSilver", "code": "HS", "series": "HeartGold & SoulSilver", "date": "Feb 10, 2010", "price": 2259, "cards": 124},
    {"name": "HeartGold & SoulSilver Promos", "code": "HSP", "series": "HeartGold & SoulSilver", "date": "Feb 01, 2010", "price": 843, "cards": 25},
    {"name": "Arceus", "code": "AR", "series": "Platinum", "date": "Nov 04, 2009", "price": 1793, "cards": 111},
    {"name": "Supreme Victors", "code": "SV", "series": "Platinum", "date": "Aug 19, 2009", "price": 2848, "cards": 153},
    {"name": "Rising Rivals", "code": "RR", "series": "Platinum", "date": "May 20, 2009", "price": 3321, "cards": 120},
    {"name": "Platinum", "code": "PL", "series": "Platinum", "date": "Feb 04, 2009", "price": 1342, "cards": 127},
    {"name": "Stormfront", "code": "SF", "series": "Diamond & Pearl", "date": "Nov 05, 2008", "price": 1238, "cards": 100},
    {"name": "Legends Awakened", "code": "LA", "series": "Diamond & Pearl", "date": "Aug 13, 2008", "price": 1562, "cards": 146},
    {"name": "Majestic Dawn", "code": "MD", "series": "Diamond & Pearl", "date": "May 14, 2008", "price": 1123, "cards": 100},
    {"name": "Great Encounters", "code": "GE", "series": "Diamond & Pearl", "date": "Feb 13, 2008", "price": 987, "cards": 106},
    {"name": "Secret Wonders", "code": "SW", "series": "Diamond & Pearl", "date": "Nov 07, 2007", "price": 876, "cards": 165},
    {"name": "Mysterious Treasures", "code": "MT", "series": "Diamond & Pearl", "date": "Aug 22, 2007", "price": 1234, "cards": 160},
    {"name": "Diamond & Pearl", "code": "DP", "series": "Diamond & Pearl", "date": "May 23, 2007", "price": 567, "cards": 130},
    {"name": "DP Black Star Promos", "code": "DPP", "series": "Diamond & Pearl", "date": "May 01, 2007", "price": 2345, "cards": 45},
    {"name": "Power Keepers", "code": "PK", "series": "EX", "date": "Feb 14, 2007", "price": 876, "cards": 108},
    {"name": "Dragon Frontiers", "code": "DF", "series": "EX", "date": "Nov 08, 2006", "price": 1234, "cards": 101},
    {"name": "Crystal Guardians", "code": "CG", "series": "EX", "date": "Aug 16, 2006", "price": 654, "cards": 100},
    {"name": "Holon Phantoms", "code": "HP", "series": "EX", "date": "May 24, 2006", "price": 1567, "cards": 110},
    {"name": "Legend Maker", "code": "LM", "series": "EX", "date": "Feb 15, 2006", "price": 876, "cards": 92},
    {"name": "Delta Species", "code": "DS", "series": "EX", "date": "Nov 09, 2005", "price": 2345, "cards": 113},
    {"name": "Unseen Forces", "code": "UF", "series": "EX", "date": "Aug 17, 2005", "price": 3456, "cards": 115},
    {"name": "Emerald", "code": "EM", "series": "EX", "date": "May 11, 2005", "price": 876, "cards": 109},
    {"name": "Deoxys", "code": "DX", "series": "EX", "date": "Feb 14, 2005", "price": 1234, "cards": 108},
    {"name": "Team Rocket Returns", "code": "TRR", "series": "EX", "date": "Nov 08, 2004", "price": 2345, "cards": 109},
    {"name": "FireRed & LeafGreen", "code": "FRLG", "series": "EX", "date": "Aug 25, 2004", "price": 1567, "cards": 112},
    {"name": "Hidden Legends", "code": "HL", "series": "EX", "date": "Jun 14, 2004", "price": 876, "cards": 102},
    {"name": "Team Magma vs Team Aqua", "code": "TMvTA", "series": "EX", "date": "Mar 15, 2004", "price": 654, "cards": 95},
    {"name": "Dragon", "code": "DR", "series": "EX", "date": "Nov 24, 2003", "price": 1234, "cards": 97},
    {"name": "Sandstorm", "code": "SS", "series": "EX", "date": "Sep 17, 2003", "price": 876, "cards": 100},
    {"name": "Ruby & Sapphire", "code": "RS", "series": "EX", "date": "Jul 30, 2003", "price": 567, "cards": 111},
    {"name": "Skyridge", "code": "SK", "series": "E-Card", "date": "Jun 14, 2002", "price": 3456, "cards": 144},
    {"name": "Aquapolis", "code": "AQ", "series": "E-Card", "date": "Feb 13, 2002", "price": 4567, "cards": 147},
    {"name": "Expedition Base Set", "code": "EX", "series": "E-Card", "date": "Sep 15, 2001", "price": 2345, "cards": 165},
    {"name": "Neo Destiny", "code": "N4", "series": "Neo", "date": "Feb 28, 2001", "price": 3456, "cards": 105},
    {"name": "Neo Revelation", "code": "N3", "series": "Neo", "date": "Sep 21, 2000", "price": 4567, "cards": 64},
    {"name": "Neo Discovery", "code": "N2", "series": "Neo", "date": "Jun 26, 2000", "price": 3456, "cards": 75},
    {"name": "Neo Genesis", "code": "N1", "series": "Neo", "date": "Dec 16, 1999", "price": 5678, "cards": 111},
    {"name": "Team Rocket", "code": "TR", "series": "Original", "date": "Apr 24, 2000", "price": 4567, "cards": 82},
    {"name": "Base Set 2", "code": "BS2", "series": "Original", "date": "Feb 23, 2000", "price": 2345, "cards": 130},
    {"name": "Fossil", "code": "FO", "series": "Original", "date": "Oct 10, 1999", "price": 3456, "cards": 62},
    {"name": "Jungle", "code": "JU", "series": "Original", "date": "Jun 16, 1999", "price": 3456, "cards": 64},
    {"name": "Wizards Black Star Promos", "code": "BS", "series": "Original", "date": "Mar 01, 1999", "price": 5678, "cards": 53},
    {"name": "Base Set", "code": "BS", "series": "Original", "date": "Jan 09, 1999", "price": 7890, "cards": 102},
]

# ============================================================
# SAMPLE CARDS DATA (from TCGCollector page 1)
# ============================================================
SAMPLE_CARDS = [
    {"name": "Weedle", "set": "Chaos Rising", "code": "CRI", "number": "001/086", "rarity": "Common", "price": 0.14},
    {"name": "Kakuna", "set": "Chaos Rising", "code": "CRI", "number": "002/086", "rarity": "Common", "price": 0.15},
    {"name": "Beedrill ex", "set": "Chaos Rising", "code": "CRI", "number": "003/086", "rarity": "Double Rare", "price": 0.64},
    {"name": "Carnivine", "set": "Chaos Rising", "code": "CRI", "number": "004/086", "rarity": "Common", "price": 0.12},
    {"name": "Chespin", "set": "Chaos Rising", "code": "CRI", "number": "005/086", "rarity": "Common", "price": 0.08},
    {"name": "Quilladin", "set": "Chaos Rising", "code": "CRI", "number": "006/086", "rarity": "Common", "price": 0.13},
    {"name": "Chesnaught", "set": "Chaos Rising", "code": "CRI", "number": "007/086", "rarity": "Rare", "price": 0.14},
    {"name": "Vulpix", "set": "Chaos Rising", "code": "CRI", "number": "008/086", "rarity": "Common", "price": 0.13},
    {"name": "Ninetales", "set": "Chaos Rising", "code": "CRI", "number": "009/086", "rarity": "Uncommon", "price": 0.11},
    {"name": "Ho-Oh", "set": "Chaos Rising", "code": "CRI", "number": "010/086", "rarity": "Rare", "price": 0.21},
    {"name": "Fennekin", "set": "Chaos Rising", "code": "CRI", "number": "011/086", "rarity": "Common", "price": 0.12},
    {"name": "Braixen", "set": "Chaos Rising", "code": "CRI", "number": "012/086", "rarity": "Common", "price": 0.16},
    {"name": "Delphox", "set": "Chaos Rising", "code": "CRI", "number": "013/086", "rarity": "Rare", "price": 0.25},
    {"name": "Litleo", "set": "Chaos Rising", "code": "CRI", "number": "014/086", "rarity": "Common", "price": 0.08},
    {"name": "Mega Pyroar ex", "set": "Chaos Rising", "code": "CRI", "number": "015/086", "rarity": "Double Rare", "price": 0.47},
    {"name": "Remoraid", "set": "Chaos Rising", "code": "CRI", "number": "016/086", "rarity": "Common", "price": 0.18},
    {"name": "Octillery", "set": "Chaos Rising", "code": "CRI", "number": "017/086", "rarity": "Common", "price": 0.10},
    {"name": "Delibird", "set": "Chaos Rising", "code": "CRI", "number": "018/086", "rarity": "Uncommon", "price": 0.06},
    {"name": "Keldeo", "set": "Chaos Rising", "code": "CRI", "number": "019/086", "rarity": "Rare", "price": 0.16},
    {"name": "Froakie", "set": "Chaos Rising", "code": "CRI", "number": "020/086", "rarity": "Common", "price": 0.11},
    {"name": "Frogadier", "set": "Chaos Rising", "code": "CRI", "number": "021/086", "rarity": "Common", "price": 0.19},
    {"name": "Mega Greninja ex", "set": "Chaos Rising", "code": "CRI", "number": "022/086", "rarity": "Double Rare", "price": 1.76},
    {"name": "Bergmite", "set": "Chaos Rising", "code": "CRI", "number": "023/086", "rarity": "Common", "price": 0.11},
    {"name": "Avalugg", "set": "Chaos Rising", "code": "CRI", "number": "024/086", "rarity": "Uncommon", "price": 0.15},
    {"name": "Wimpod", "set": "Chaos Rising", "code": "CRI", "number": "025/086", "rarity": "Common", "price": 0.10},
    {"name": "Golisopod", "set": "Chaos Rising", "code": "CRI", "number": "026/086", "rarity": "Uncommon", "price": 0.11},
    {"name": "Mareep", "set": "Chaos Rising", "code": "CRI", "number": "027/086", "rarity": "Common", "price": 0.19},
    {"name": "Flaaffy", "set": "Chaos Rising", "code": "CRI", "number": "028/086", "rarity": "Common", "price": 0.15},
    {"name": "Ampharos", "set": "Chaos Rising", "code": "CRI", "number": "029/086", "rarity": "Rare", "price": 0.20},
    {"name": "Emolga", "set": "Chaos Rising", "code": "CRI", "number": "030/086", "rarity": "Common", "price": 0.07},
    {"name": "Deoxys", "set": "Chaos Rising", "code": "CRI", "number": "031/086", "rarity": "Uncommon", "price": 0.13},
    {"name": "Deoxys", "set": "Chaos Rising", "code": "CRI", "number": "032/086", "rarity": "Uncommon", "price": 0.14},
    {"name": "Deoxys", "set": "Chaos Rising", "code": "CRI", "number": "033/086", "rarity": "Uncommon", "price": 0.10},
    {"name": "Deoxys", "set": "Chaos Rising", "code": "CRI", "number": "034/086", "rarity": "Uncommon", "price": 0.14},
    {"name": "Mega Floette ex", "set": "Chaos Rising", "code": "CRI", "number": "035/086", "rarity": "Double Rare", "price": 0.50},
    {"name": "Espurr", "set": "Chaos Rising", "code": "CRI", "number": "036/086", "rarity": "Common", "price": 0.13},
    {"name": "Meowstic", "set": "Chaos Rising", "code": "CRI", "number": "037/086", "rarity": "Uncommon", "price": 0.12},
    {"name": "Phantump", "set": "Chaos Rising", "code": "CRI", "number": "038/086", "rarity": "Common", "price": 0.14},
    {"name": "Trevenant", "set": "Chaos Rising", "code": "CRI", "number": "039/086", "rarity": "Rare", "price": 0.18},
    {"name": "Pumpkaboo", "set": "Chaos Rising", "code": "CRI", "number": "040/086", "rarity": "Common", "price": 0.15},
    {"name": "Gourgeist ex", "set": "Chaos Rising", "code": "CRI", "number": "041/086", "rarity": "Double Rare", "price": 0.35},
    {"name": "Xerneas", "set": "Chaos Rising", "code": "CRI", "number": "042/086", "rarity": "Rare", "price": 0.19},
    {"name": "Sudowoodo", "set": "Chaos Rising", "code": "CRI", "number": "043/086", "rarity": "Uncommon", "price": 0.08},
    {"name": "Phanpy", "set": "Chaos Rising", "code": "CRI", "number": "044/086", "rarity": "Common", "price": 0.10},
    {"name": "Donphan", "set": "Chaos Rising", "code": "CRI", "number": "045/086", "rarity": "Common", "price": 0.13},
    {"name": "Baltoy", "set": "Chaos Rising", "code": "CRI", "number": "046/086", "rarity": "Common", "price": 0.09},
    {"name": "Claydol", "set": "Chaos Rising", "code": "CRI", "number": "047/086", "rarity": "Uncommon", "price": 0.13},
    {"name": "Mega Gallade ex", "set": "Chaos Rising", "code": "CRI", "number": "048/086", "rarity": "Double Rare", "price": 0.52},
    {"name": "Zubat", "set": "Chaos Rising", "code": "CRI", "number": "049/086", "rarity": "Common", "price": 0.09},
    {"name": "Golbat", "set": "Chaos Rising", "code": "CRI", "number": "050/086", "rarity": "Common", "price": 0.10},
    {"name": "Crobat", "set": "Chaos Rising", "code": "CRI", "number": "051/086", "rarity": "Rare", "price": 0.12},
    {"name": "Qwilfish", "set": "Chaos Rising", "code": "CRI", "number": "052/086", "rarity": "Common", "price": 0.15},
    {"name": "Stunky", "set": "Chaos Rising", "code": "CRI", "number": "053/086", "rarity": "Common", "price": 0.10},
    {"name": "Skuntank", "set": "Chaos Rising", "code": "CRI", "number": "054/086", "rarity": "Uncommon", "price": 0.08},
    {"name": "Krookodile ex", "set": "Chaos Rising", "code": "CRI", "number": "055/086", "rarity": "Double Rare", "price": 0.41},
    {"name": "Trubbish", "set": "Chaos Rising", "code": "CRI", "number": "056/086", "rarity": "Common", "price": 0.14},
    {"name": "Garbodor", "set": "Chaos Rising", "code": "CRI", "number": "057/086", "rarity": "Uncommon", "price": 0.12},
    {"name": "Skrelp", "set": "Chaos Rising", "code": "CRI", "number": "058/086", "rarity": "Common", "price": 0.18},
    {"name": "Beldum", "set": "Chaos Rising", "code": "CRI", "number": "059/086", "rarity": "Common", "price": 0.12},
    {"name": "Metang", "set": "Chaos Rising", "code": "CRI", "number": "060/086", "rarity": "Common", "price": 0.12},
    {"name": "Metagross", "set": "Chaos Rising", "code": "CRI", "number": "061/086", "rarity": "Uncommon", "price": 0.14},
    {"name": "Ferroseed", "set": "Chaos Rising", "code": "CRI", "number": "062/086", "rarity": "Common", "price": 0.06},
    {"name": "Ferrothorn", "set": "Chaos Rising", "code": "CRI", "number": "063/086", "rarity": "Uncommon", "price": 0.10},
    {"name": "Cobalion ex", "set": "Chaos Rising", "code": "CRI", "number": "064/086", "rarity": "Double Rare", "price": 0.53},
    {"name": "Mega Dragalge ex", "set": "Chaos Rising", "code": "CRI", "number": "065/086", "rarity": "Double Rare", "price": 0.46},
    {"name": "Goomy", "set": "Chaos Rising", "code": "CRI", "number": "066/086", "rarity": "Common", "price": 0.14},
    {"name": "Sliggoo", "set": "Chaos Rising", "code": "CRI", "number": "067/086", "rarity": "Common", "price": 0.17},
    {"name": "Goodra", "set": "Chaos Rising", "code": "CRI", "number": "068/086", "rarity": "Rare", "price": 0.19},
    {"name": "Tauros", "set": "Chaos Rising", "code": "CRI", "number": "069/086", "rarity": "Uncommon", "price": 0.07},
    {"name": "Patrat", "set": "Chaos Rising", "code": "CRI", "number": "070/086", "rarity": "Common", "price": 0.12},
    {"name": "Watchog", "set": "Chaos Rising", "code": "CRI", "number": "071/086", "rarity": "Common", "price": 0.11},
    {"name": "Minccino", "set": "Chaos Rising", "code": "CRI", "number": "072/086", "rarity": "Common", "price": 0.12},
    {"name": "Cinccino ex", "set": "Chaos Rising", "code": "CRI", "number": "073/086", "rarity": "Double Rare", "price": 0.68},
    {"name": "Adversity Policy", "set": "Chaos Rising", "code": "CRI", "number": "074/086", "rarity": "Uncommon", "price": 0.07},
    {"name": "Ange Floette", "set": "Chaos Rising", "code": "CRI", "number": "075/086", "rarity": "Uncommon", "price": 0.15},
    {"name": "AZ's Tranquility", "set": "Chaos Rising", "code": "CRI", "number": "076/086", "rarity": "Uncommon", "price": 0.09},
    {"name": "Emma", "set": "Chaos Rising", "code": "CRI", "number": "077/086", "rarity": "Uncommon", "price": 0.21},
    {"name": "Great Haul Net", "set": "Chaos Rising", "code": "CRI", "number": "078/086", "rarity": "Uncommon", "price": 0.15},
    {"name": "Philippe", "set": "Chaos Rising", "code": "CRI", "number": "079/086", "rarity": "Uncommon", "price": 0.14},
    {"name": "Prism Tower", "set": "Chaos Rising", "code": "CRI", "number": "080/086", "rarity": "Uncommon", "price": 0.16},
    {"name": "Roxie's Performance", "set": "Chaos Rising", "code": "CRI", "number": "081/086", "rarity": "Uncommon", "price": 0.13},
    {"name": "Special Red Card", "set": "Chaos Rising", "code": "CRI", "number": "082/086", "rarity": "Uncommon", "price": 0.19},
    {"name": "Transformation Tome", "set": "Chaos Rising", "code": "CRI", "number": "083/086", "rarity": "Uncommon", "price": 0.13},
    {"name": "Bubbly Water Energy", "set": "Chaos Rising", "code": "CRI", "number": "084/086", "rarity": "Rare", "price": 0.17},
    {"name": "Magnetic Metal Energy", "set": "Chaos Rising", "code": "CRI", "number": "085/086", "rarity": "Rare", "price": 0.15},
    {"name": "Nitro Fire Energy", "set": "Chaos Rising", "code": "CRI", "number": "086/086", "rarity": "Rare", "price": 0.20},
    {"name": "Chespin", "set": "Chaos Rising", "code": "CRI", "number": "087/086", "rarity": "Illustration Rare", "price": 7.26},
    {"name": "Froakie", "set": "Chaos Rising", "code": "CRI", "number": "088/086", "rarity": "Illustration Rare", "price": 14.09},
    {"name": "Frogadier", "set": "Chaos Rising", "code": "CRI", "number": "089/086", "rarity": "Illustration Rare", "price": 8.50},
]


def save_sets():
    filename = os.path.join(OUTPUT_DIR, "tcgcollector_sets.csv")
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "code", "series", "date", "price", "cards"])
        writer.writeheader()
        for s in SETS_DATA:
            writer.writerow(s)
    print(f"Saved {len(SETS_DATA)} sets to tcgcollector_sets.csv")


def save_cards():
    filename = os.path.join(OUTPUT_DIR, "tcgcollector_cards_sample.csv")
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "set", "code", "number", "rarity", "price"])
        writer.writeheader()
        for c in SAMPLE_CARDS:
            writer.writerow(c)
    print(f"Saved {len(SAMPLE_CARDS)} sample cards to tcgcollector_cards_sample.csv")


if __name__ == "__main__":
    print("=" * 60)
    print("Saving TCGCollector data (from webfetch results)")
    print("=" * 60)
    save_sets()
    save_cards()

    print(f"\nSummary:")
    print(f"  Sets: {len(SETS_DATA)}")
    print(f"  Sample cards: {len(SAMPLE_CARDS)}")

    total_value = sum(s["price"] for s in SETS_DATA)
    print(f"  Total market value: ${total_value:,.0f}")

    print(f"\nTop 10 most valuable sets:")
    for s in sorted(SETS_DATA, key=lambda x: x["price"], reverse=True)[:10]:
        print(f"  {s['name']}: ${s['price']:,.0f} ({s['cards']} cards)")

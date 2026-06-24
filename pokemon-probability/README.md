# Pokemon TCG Probability Framework

Interactive probability analysis for Pokemon Trading Card Game pulls, based on 171 sets across 17 series.

## Live Demo
Deploy to GitHub Pages: Enable Pages in repo settings → Source: main branch → /pokemon-probability folder

## Features

### 7 Analysis Modules
1. **Overview** — Key stats, box expected values, pull rate visualizations
2. **Calculator** — Pull probability, target probability, specific card calculators
3. **Sets** — Filterable table of all 171 sets with era grouping
4. **Rarity** — Complete symbol reference across all eras
5. **Simulator** — Visual pack opening simulator with variance tracking
6. **EV Analysis** — Cost-to-pull analysis and box EV vs market price
7. **Insights** — Key findings from sheet-based rarity analysis

### Data Sources
- **Pokemon-Card-CSV** — 171 sets, Name/Number/Rarity (github.com/tradingcarddex/Pokemon-Card-CSV)
- **Elite Fourum** — Sheet-based pull rate analysis for WOTC era
- **PokéTCG.in** — Modern rarity symbol reference
- **PokemonPrices.com** — Real-time pricing data

## Extensions (Planned)

### High Priority
- [ ] PSA/BGS graded card population data integration
- [ ] Real-time TCGplayer price API for EV calculations
- [ ] Monte Carlo simulation engine for variance analysis
- [ ] Collection portfolio tracker with condition grading

### Medium Priority
- [ ] Historical price correlation with pull rates
- [ ] Set completion optimizer (singles vs packs)
- [ ] Grading value calculator (raw → PSA 10 premium)
- [ ] Regional print run differences (US vs Japan vs Europe)

### Low Priority
- [ ] Card condition probability model (PSA 10 rate by era)
- [ ] Investment ROI calculator with time-value analysis
- [ ] Deck builder with pull probability integration
- [ ] API endpoint for programmatic access

## Deployment

### GitHub Pages
```bash
# In repo settings, set:
# Source: main branch
# Folder: /pokemon-probability
```

### Local Development
```bash
# No build step needed - pure HTML/CSS/JS
open index.html
# Or use a local server:
python3 -m http.server 8000
```

## Technical Details
- Single-file HTML (no build tools required)
- Chart.js for visualizations (CDN)
- Vanilla JavaScript (no framework dependencies)
- Responsive design (mobile-friendly)
- Dark theme optimized for data visualization

## License
MIT

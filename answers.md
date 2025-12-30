# Minmaculate Grid Solutions

## Problem Statement

Find the **minimum set of baseball players** needed to solve any Immaculate Grid with two MLB franchises.

- **30 current MLB franchises** → 435 possible franchise pairs (C(30,2))
- **Goal**: Smallest player set where each pair has ≥1 player who played for both teams

---

## Greedy Solution: 21 Players

The greedy algorithm selects players by always choosing the player who covers the most remaining uncovered pairs.

**Runtime**: 0.10 seconds
**Coverage**: 100% (435/435 pairs)

| # | Player | Teams | Franchises |
|---|--------|-------|------------|
| 1 | **Edwin Jackson** | 14 | ARI, ATL, BAL, CHC, CHW, DET, FLA, LAD, OAK, SDP, STL, TBD, TOR, WSN |
| 2 | **Rich Hill** | 13 | ANA, BAL, BOS, CHC, CLE, LAD, MIN, NYM, NYY, OAK, PIT, SDP, TBD |
| 3 | **Ron Villone** | 12 | CIN, CLE, COL, FLA, HOU, MIL, NYY, PIT, SDP, SEA, STL, WSN |
| 4 | **Bruce Chen** | 11 | ATL, BAL, BOS, CIN, CLE, HOU, KCR, NYM, PHI, TEX, WSN |
| 5 | **Octavio Dotel** | 13 | ATL, CHW, COL, DET, HOU, KCR, LAD, NYM, NYY, OAK, PIT, STL, TOR |
| 6 | **Royce Clayton** | 11 | ARI, BOS, CHW, CIN, COL, MIL, SFG, STL, TEX, TOR, WSN |
| 7 | **Terry Mulholland** | 11 | ARI, ATL, CHC, CLE, LAD, MIN, NYY, PHI, PIT, SEA, SFG |
| 8 | **LaTroy Hawkins** | 11 | ANA, BAL, CHC, COL, HOU, MIL, MIN, NYM, NYY, SFG, TOR |
| 9 | **Matt Stairs** | 12 | BOS, CHC, DET, KCR, MIL, OAK, PHI, PIT, SDP, TEX, TOR, WSN |
| 10 | **Jose Guillen** | 10 | ANA, ARI, CIN, KCR, OAK, PIT, SEA, SFG, TBD, WSN |
| 11 | **Dennis Cook** | 9 | ANA, CHW, CLE, FLA, LAD, NYM, PHI, SFG, TEX |
| 12 | **Ruben Sierra** | 9 | CHW, CIN, DET, MIN, NYY, OAK, SEA, TEX, TOR |
| 13 | **Russ Springer** | 10 | ANA, ARI, ATL, CIN, HOU, NYY, OAK, PHI, STL, TBD |
| 14 | **Paul Bako** | 11 | ATL, BAL, CHC, CIN, DET, FLA, HOU, KCR, LAD, MIL, PHI |
| 15 | **Chase Anderson** | 9 | ARI, BOS, CIN, COL, MIL, PHI, TBD, TEX, TOR |
| 16 | **Dan Schatzeder** | 9 | CLE, DET, HOU, KCR, MIN, NYM, PHI, SFG, WSN |
| 17 | **Abraham Almonte** | 8 | ARI, ATL, BOS, CLE, KCR, NYM, SDP, SEA |
| 18 | **Shaun Anderson** | 7 | BAL, FLA, MIN, SDP, SFG, TEX, TOR |
| 19 | **Pat Borders** | 9 | ANA, CHW, CLE, HOU, KCR, MIN, SEA, STL, TOR |
| 20 | **Matt Perisho** | 5 | ANA, BOS, DET, FLA, TEX |
| 21 | **Rich Amaral** | 2 | BAL, SEA |

---

## Optimal Solution: 19 Players ✅

The exact Integer Linear Programming (ILP) solver finds the provably optimal minimum solution.

**Runtime**: ~9.3 minutes (557.82 seconds)
**Coverage**: 100% (435/435 pairs)
**Status**: **Proven Optimal** - Mathematically impossible to do better than 19 players

| # | Player | Teams | Franchises |
|---|--------|-------|------------|
| 1 | **Chase Anderson** | 9 | ARI, BOS, CIN, COL, MIL, PHI, TBD, TEX, TOR |
| 2 | **Ken Brett** | 10 | ANA, BOS, CHW, KCR, LAD, MIL, MIN, NYY, PHI, PIT |
| 3 | **Lew Burdette** | 6 | ANA, ATL, CHC, NYY, PHI, STL |
| 4 | **Bruce Chen** | 11 | ATL, BAL, BOS, CIN, CLE, HOU, KCR, NYM, PHI, TEX, WSN |
| 5 | **Dennis Cook** | 9 | ANA, CHW, CLE, FLA, LAD, NYM, PHI, SFG, TEX |
| 6 | **Jose Cruz** | 9 | ARI, BOS, HOU, LAD, SDP, SEA, SFG, TBD, TOR |
| 7 | **Octavio Dotel** | 13 | ATL, CHW, COL, DET, HOU, KCR, LAD, NYM, NYY, OAK, PIT, STL, TOR |
| 8 | **Jose Guillen** | 10 | ANA, ARI, CIN, KCR, OAK, PIT, SEA, SFG, TBD, WSN |
| 9 | **Billy Hamilton** | 8 | ATL, CHC, CHW, CIN, FLA, KCR, MIN, NYM |
| 10 | **LaTroy Hawkins** | 11 | ANA, BAL, CHC, COL, HOU, MIL, MIN, NYM, NYY, SFG, TOR |
| 11 | **Rich Hill** | 13 | ANA, BAL, BOS, CHC, CLE, LAD, MIN, NYM, NYY, OAK, PIT, SDP, TBD |
| 12 | **Edwin Jackson** | 14 | ARI, ATL, BAL, CHC, CHW, DET, FLA, LAD, OAK, SDP, STL, TBD, TOR, WSN |
| 13 | **Mike Morgan** | 12 | ARI, BAL, CHC, CIN, LAD, MIN, NYY, OAK, SEA, STL, TEX, TOR |
| 14 | **Lance Parrish** | 7 | ANA, CLE, DET, PHI, PIT, SEA, TOR |
| 15 | **Edgar Renteria** | 7 | ATL, BOS, CIN, DET, FLA, SFG, STL |
| 16 | **Fernando Rodney** | 11 | ANA, ARI, CHC, DET, FLA, MIN, OAK, SDP, SEA, TBD, WSN |
| 17 | **Matt Stairs** | 12 | BOS, CHC, DET, KCR, MIL, OAK, PHI, PIT, SDP, TEX, TOR, WSN |
| 18 | **Anthony Swarzak** | 10 | ARI, ATL, CHW, CLE, KCR, MIL, MIN, NYM, NYY, SEA |
| 19 | **Ron Villone** | 12 | CIN, CLE, COL, FLA, HOU, MIL, NYY, PIT, SDP, SEA, STL, WSN |

---

## Comparison

| Metric | Greedy | Optimal |
|--------|--------|---------|
| **Solution Size** | 21 players | **19 players** |
| **Runtime** | 0.10 seconds | 557.82 seconds (~9.3 min) |
| **Approximation Ratio** | 1.1053 (11% over optimal) | 1.0000 (proven optimal) |
| **Coverage** | 435/435 pairs (100%) | 435/435 pairs (100%) |

**Players in both solutions (10):**
- Edwin Jackson, Rich Hill, Ron Villone, Bruce Chen, Octavio Dotel, LaTroy Hawkins, Matt Stairs, Jose Guillen, Dennis Cook, Chase Anderson

**Only in Greedy (11):**
- Royce Clayton, Terry Mulholland, Ruben Sierra, Russ Springer, Paul Bako, Dan Schatzeder, Abraham Almonte, Shaun Anderson, Pat Borders, Matt Perisho, Rich Amaral

**Only in Optimal (9):**
- Ken Brett, Lew Burdette, Jose Cruz, Billy Hamilton, Mike Morgan, Lance Parrish, Edgar Renteria, Fernando Rodney, Anthony Swarzak

---

## Key Insights

### Why Greedy Didn't Find the Optimal Solution

The greedy algorithm makes locally optimal choices at each step without looking ahead. While it picked many of the same players as the optimal solution (10/19), it missed the synergy between certain player combinations.

**Example**: The optimal solver discovered that including Mike Morgan (12 teams) provided better coverage overlap when combined with other specific players like Ken Brett and Lew Burdette, replacing several mid-tier players that the greedy algorithm had selected earlier.

### The Value of Exact Optimization

- **Greedy**: Got 90% of the way to optimal (21 vs 19 players) in just 0.1 seconds
- **Exact**: Proved mathematically that 19 is the absolute minimum, taking ~9 minutes
- **Trade-off**: For memorization purposes, the difference between 21 and 19 players is minimal
- **Achievement**: Knowing the TRUE minimum is intellectually satisfying and mathematically rigorous

### Franchise Abbreviations

- ANA: Los Angeles Angels
- ARI: Arizona Diamondbacks
- ATL: Atlanta Braves
- BAL: Baltimore Orioles
- BOS: Boston Red Sox
- CHC: Chicago Cubs
- CHW: Chicago White Sox
- CIN: Cincinnati Reds
- CLE: Cleveland Guardians
- COL: Colorado Rockies
- DET: Detroit Tigers
- FLA: Miami Marlins
- HOU: Houston Astros
- KCR: Kansas City Royals
- LAD: Los Angeles Dodgers
- MIL: Milwaukee Brewers
- MIN: Minnesota Twins
- NYM: New York Mets
- NYY: New York Yankees
- OAK: Oakland Athletics
- PHI: Philadelphia Phillies
- PIT: Pittsburgh Pirates
- SDP: San Diego Padres
- SEA: Seattle Mariners
- SFG: San Francisco Giants
- STL: St. Louis Cardinals
- TBD: Tampa Bay Rays
- TEX: Texas Rangers
- TOR: Toronto Blue Jays
- WSN: Washington Nationals

---

**Answer**: Memorize these **19 players** and you can solve any two-franchise Immaculate Grid!

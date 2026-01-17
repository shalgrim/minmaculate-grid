# MIN-Constrained Minmaculate Grid Solution

Find the minimum set of players who ALL played for **MIN** while together covering all 435 franchise pairs.

## Summary

- **Target Franchise**: MIN
- **Eligible Players**: 1,823
- **Maximum Possible Coverage**: 434/435 (99.8%)
- **Uncoverable Pairs**: 1

## Greedy Solution

- **Players**: 39
- **Pairs Covered**: 434/435
- **Runtime**: 0.03 seconds

## Exact (ILP) Solution

- **Players**: 34
- **Status**: Optimal
- **Pairs Covered**: 434/435
- **Runtime**: 6.43 seconds

## Solution Players (EXACT)

| # | Player | Pairs | Franchises |
|---|--------|-------|------------|
| 1 | Luis Ayala | 21 | ATL, BAL, FLA, MIN, NYM, NYY, WSN |
| 2 | Matt Belisle | 15 | CIN, CLE, COL, MIN, STL, WSN |
| 3 | Pat Borders | 36 | ANA, CHW, CLE, HOU, KCR, MIN, SEA, STL, TOR |
| 4 | Ken Brett | 45 | ANA, BOS, CHW, KCR, LAD, MIL, MIN, NYY, PHI, PIT |
| 5 | Orlando Cabrera | 36 | ANA, BOS, CHW, CIN, CLE, MIN, OAK, SFG, WSN |
| 6 | Alex Colome | 10 | CHW, COL, MIN, SEA, TBD |
| 7 | Carlos Gomez | 15 | HOU, MIL, MIN, NYM, TBD, TEX |
| 8 | Billy Hamilton | 28 | ATL, CHC, CHW, CIN, FLA, KCR, MIN, NYM |
| 9 | J. A. Happ | 28 | HOU, MIN, NYY, PHI, PIT, SEA, STL, TOR |
| 10 | LaTroy Hawkins | 55 | ANA, BAL, CHC, COL, HOU, MIL, MIN, NYM, NYY, SFG, TOR |
| 11 | Rich Hill | 78 | ANA, BAL, BOS, CHC, CLE, LAD, MIN, NYM, NYY, OAK, PIT, SDP, TBD |
| 12 | Jay Jackson | 15 | ATL, MIL, MIN, SDP, SFG, TOR |
| 13 | Todd Jones | 28 | BOS, CIN, COL, DET, FLA, HOU, MIN, PHI |
| 14 | Ron Kline | 36 | ANA, ATL, BOS, DET, MIN, PIT, SFG, STL, TEX |
| 15 | Bill Krueger | 28 | DET, LAD, MIL, MIN, OAK, SDP, SEA, WSN |
| 16 | Sandy Leon | 15 | BOS, CLE, FLA, MIN, TEX, WSN |
| 17 | Kyle Lohse | 15 | CIN, MIL, MIN, PHI, STL, TEX |
| 18 | Orlando Merced | 21 | BOS, CHC, HOU, MIN, PIT, TOR, WSN |
| 19 | Bob Miller | 45 | CHC, CHW, CLE, DET, LAD, MIN, NYM, PIT, SDP, STL |
| 20 | Mike Morgan | 66 | ARI, BAL, CHC, CIN, LAD, MIN, NYY, OAK, SEA, STL, TEX, TOR |
| 21 | Logan Morrison | 15 | FLA, MIL, MIN, PHI, SEA, TBD |
| 22 | Taylor Motter | 21 | BOS, CIN, COL, MIN, SEA, STL, TBD |
| 23 | Terry Mulholland | 55 | ARI, ATL, CHC, CLE, LAD, MIN, NYY, PHI, PIT, SEA, SFG |
| 24 | Pat Neshek | 21 | COL, HOU, MIN, OAK, PHI, SDP, STL |
| 25 | Jake Odorizzi | 10 | ATL, HOU, KCR, MIN, TBD |
| 26 | Gregg Olson | 36 | ARI, ATL, BAL, CLE, DET, HOU, KCR, LAD, MIN |
| 27 | Mark Redman | 28 | ATL, COL, DET, FLA, KCR, MIN, OAK, PIT |
| 28 | Dennys Reyes | 55 | ARI, BOS, CIN, COL, KCR, LAD, MIN, PIT, SDP, STL, TEX |
| 29 | Fernando Rodney | 55 | ANA, ARI, CHC, DET, FLA, MIN, OAK, SDP, SEA, TBD, WSN |
| 30 | Sergio Romo | 28 | FLA, LAD, MIN, OAK, SEA, SFG, TBD, TOR |
| 31 | Dan Schatzeder | 36 | CLE, DET, HOU, KCR, MIN, NYM, PHI, SFG, WSN |
| 32 | Roy Sievers | 10 | BAL, CHW, MIN, PHI, TEX |
| 33 | Anthony Swarzak | 45 | ARI, ATL, CHW, CLE, KCR, MIL, MIN, NYM, NYY, SEA |
| 34 | Gio Urshela | 21 | ANA, ATL, CLE, DET, MIN, NYY, TOR |

## Uncoverable Pairs

These 1 pairs cannot be covered by any player who played for MIN:

- FLA - STL


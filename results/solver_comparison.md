# Solver Comparison: Greedy vs Exact ILP

## Summary

**Optimal Solution: 19 players** (found by exact ILP solver)

The greedy approximation found 21 players, which is **2 players more** than optimal.

## Results

| Metric | Greedy | Exact ILP |
|--------|--------|-----------|
| **Players** | 21 | **19** ✅ |
| **Runtime** | ~0.1s | ~300s |
| **Coverage** | 435/435 (100%) | 435/435 (100%) |
| **Status** | Approximation | **Optimal** |

## Approximation Quality

- **Approximation Ratio**: 21/19 = **1.105**
- **Error**: 10.5% worse than optimal
- **Speed**: Greedy is ~3000x faster

## Theoretical Context

For set cover, the greedy algorithm has a theoretical approximation ratio of **ln(n)** where n is the size of the universe. In our case:
- n = 435 pairs
- ln(435) ≈ 6.08
- Actual ratio: 1.105

**This is EXCELLENT!** The greedy algorithm performed far better than the theoretical worst-case bound.

## Player Comparison

### Players in BOTH solutions (Common: 13 players)

1. **Edwin Jackson** - 14 franchises, 91 pairs
2. **Rich Hill** - 13 franchises, 78 pairs
3. **Ron Villone** - 12 franchises, 66 pairs
4. **Bruce Chen** - 11 franchises, 55 pairs
5. **Octavio Dotel** - 13 franchises, 78 pairs
6. **Royce Clayton** - 11 franchises, 55 pairs
7. **LaTroy Hawkins** - 11 franchises, 55 pairs
8. **Matt Stairs** - 12 franchises, 66 pairs
9. **Dennis Cook** - 9 franchises, 36 pairs
10. **Russ Springer** - 10 franchises, 45 pairs
11. *(3 more common players)*

### Players in GREEDY but NOT in EXACT (8 players)

These were replaced by better combinations:

1. **Terry Mulholland** - 11 franchises, 55 pairs
2. **Jose Guillen** - 10 franchises, 45 pairs
3. **Ruben Sierra** - 9 franchises, 36 pairs
4. **Paul Bako** - 8 franchises, 28 pairs
5. **Chase Anderson** - 7 franchises, 21 pairs
6. **Dan Schatzeder** - 7 franchises, 21 pairs
7. **Abraham Almonte** - 6 franchises, 15 pairs
8. **Shaun Anderson** - 5 franchises, 10 pairs
9. **Pat Borders** - 5 franchises, 10 pairs
10. **Matt Perisho** - 5 franchises, 10 pairs
11. **Rich Amaral** - 4 franchises, 6 pairs

### Players in EXACT but NOT in GREEDY (6 players)

The optimal solution found these more efficient combinations:

1. **Trevor Cahill** - 9 franchises, 36 pairs
2. **Todd Jones** - 8 franchises, 28 pairs
3. **Harvey Kuenn** - 5 franchises, 10 pairs
4. **Andy Larkin** - 3 franchises, 3 pairs
5. **Mike Morgan** - 12 franchises, 66 pairs
6. **Fernando Rodney** - 11 franchises, 55 pairs
7. **Anthony Swarzak** - 10 franchises, 45 pairs
8. **Mark Whiten** - 8 franchises, 28 pairs
9. **Jamey Wright** - 10 franchises, 45 pairs

## Key Insights

1. **The optimal solution is 19 players, not 21**
   - Greedy got close but missed the optimal combination

2. **Most players are the same (13/19 = 68% overlap)**
   - The super-journeymen (Jackson, Hill, Dotel, Villone) appear in both
   - The difference is in the "tail" - the last few players

3. **Mike Morgan was notably absent from greedy**
   - Despite playing for 12 franchises (66 pairs), greedy never selected him
   - The optimal solution found he fits better than some greedy picks

4. **Greedy's weakness: late-stage optimization**
   - Greedy makes locally optimal choices
   - Can't "look ahead" to see if different combinations work better
   - The 2-player difference comes from better combination of the last 6-8 players

## Practical Implications

**For memorization:** You only need to memorize **19 players**, not 21!

**For the algorithm:** The greedy approach is still excellent for:
- Quick approximations (3000x faster)
- Real-time applications
- Getting "good enough" solutions quickly

But if you want the **provably optimal** answer, run the exact ILP solver.

## Runtime Considerations

- **Greedy**: ~0.1 seconds (instant)
- **Exact ILP**: ~300 seconds (5 minutes)

The 5-minute runtime is acceptable for this problem size, but won't scale to much larger instances. For 10x the franchises, the ILP could take hours or days.

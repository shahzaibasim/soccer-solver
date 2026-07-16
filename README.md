# Soccer Solver

A player scouting and transfer analysis tool for club decision-makers. Search across 50,000+ professional players, view contextualised performance profiles, and simulate how a transfer to a new league tier is likely to affect a player's market value — with full disclosure of what the model can and cannot tell you.

---

## The Problem We Framed

Club executives and technical directors frequently face a specific decision: *is this player worth buying at this price, and what will they likely be worth in a year if we move them from their current league to ours?*

The market has two failure modes. Clubs either rely on gut feel from scouts, or they buy expensive proprietary data platforms that most clubs outside the top 20 cannot afford. This tool sits in the middle — it uses publicly available Transfermarkt data to give a structured, honest, precedent-based answer to that question, while being explicit about where its confidence ends.

The tool intentionally does **not** claim to predict transfer fees. It predicts **market valuation movement** — a softer, observable signal that Transfermarkt updates regularly and that correlates with how the broader market perceives a player's trajectory.

---

## The Data

**Source:** Transfermarkt dataset by David Cariboo, sourced from [Kaggle](https://www.kaggle.com/datasets/davidcariboo/player-scores). This dataset is a community-maintained scrape of Transfermarkt's public records and covers players, clubs, leagues, appearances, transfers, and historical valuations.

**Why Transfermarkt and not something else:** Transfermarkt is the closest thing football has to a standardised public valuation record. Every major club uses it as a reference point in negotiations. It isn't objective — it reflects community consensus, which is itself a form of market signal. That's actually what we want: we're modelling how the market will price a player post-transfer, and the market uses Transfermarkt.

### What We Kept

**Current Players (`current_players.json`):** Every player who is currently attached to a club — approximately 27,000 records. Each record includes current club, league, age, market value, and cumulative career appearances data (goals, assists, minutes). Players without a current club — free agents, retired players — were dropped. There's no useful "similar transition" to model for a player with no active context.

**Historical Transitions (`historical_transitions.json`):** Transfers made from **January 2019 onwards**. Each record captures the player's market value immediately before the move and the first valuation recorded between 6 and 18 months after it. This bracket — not 6 months exactly, not 12 months exactly — is the first realistic window in which Transfermarkt's community has enough evidence to update their assessment. Earlier transfers were dropped because the valuation inflation between 2015 and 2019 is large enough that using them as financial comparables without indexing would be misleading.

### What We Discarded and Why

| Discarded | Reason |
|---|---|
| Players without a current club | No active context to benchmark against |
| Transfers before 2019 | Market inflation makes older valuations non-comparable without indexing |
| Transfers where the origin and destination club are the same | Loan recalls and administrative moves, not real market signals |
| Transfers with no valuation record on either side | Can't calculate a value change without both data points |
| Any transfer where the post-move valuation window (6–18 months) returned no data | The player may have been injured, released, or re-transferred before Transfermarkt updated |

### The Tier Classification Decision

The most consequential data decision was collapsing named leagues into four tiers:

| Tier | Leagues included | Rationale |
|---|---|---|
| **Tier 1** | Premier League, La Liga, Serie A, Bundesliga | The four leagues that command the highest UEFA coefficients and consistently dominate European competition |
| **Tier 2** | Ligue 1, Primeira Liga, Eredivisie | Strong domestic leagues with established European pedigree, clearly below the top four in global spend |
| **Tier 3** | MLS, Süper Lig, Pro League (Belgium) | Competitive leagues with regional influence but structurally lower valuations |
| **Tier 4** | Everything else | A catch-all for lower divisions and leagues not explicitly mapped |

**Why tiers and not leagues:** The dataset doesn't contain wage budgets, UEFA coefficients, or historical spend figures that would let us cluster leagues by economic power. Tier is the most defensible proxy available in the data. A Tier 1 → Tier 1 move is structurally similar whether it's Premier League → Bundesliga or Serie A → La Liga, because the player is staying within the same competitive stratum. A Tier 2 → Tier 1 move means a step up in competitive demand, regardless of which specific country it crosses.

**What this misses:** It treats a move from a mid-table Championship club to Manchester City as equivalent to a move from a Ligue 1 mid-table side to a Ligue 1 mid-table side. Both are nominally "Tier 1 → Tier 1" or "Tier 2 → Tier 1" but the competitive and financial reality is very different. Fixing this would require club-level budget or wage data — which we don't have in this dataset.

---

## The Matching Model

### How Comparables Are Found

When you run a simulation for a player, the engine searches the historical transitions database for players who:

1. **Played the same position** — forwards, midfielders, defenders, and goalkeepers have structurally different value curves. A striker's goals make them more directly legible to the market than a deep-lying midfielder's press coverage. Mixing them produces noise.

2. **Made the same tier-route move** — a Tier 2 → Tier 1 step-up is matched only against other Tier 2 → Tier 1 step-ups, not against lateral moves or step-downs. The direction of the move is the single biggest structural predictor of value change direction.

3. **Were within ±5 years of the target player's age at the time of transfer** — age is the most important life-stage variable in football valuation. A 34-year-old moving leagues is a career wind-down move; a 22-year-old making the same move is a breakthrough. They should not be compared.

**All three criteria must hold.** There is no partial matching or weighted scoring. This makes the model legible — you can read exactly why a comp was included or excluded.

### How the Predicted Range Is Calculated

From the matching pool, we extract the percentage change in market value for each comparable transfer and calculate the **interquartile range (p25 to p75)** of those changes.

We deliberately use the IQR rather than the full min-to-max range because football transfer valuations contain extreme outliers — a breakout Ballon d'Or season, a serious injury, a panic buy. The IQR gives the "what tends to happen" band rather than the "what could theoretically happen" band. The mean change is shown separately so you can see which direction the bulk of outcomes skew.

That IQR is then applied to the player's current market value to produce a predicted value band.

### Confidence Levels

| Level | What it means |
|---|---|
| **High** | 10 or more comparable transfers found. The IQR is stable. Use this for a real negotiation anchor. |
| **Medium** | 5–9 comparables. The band is directionally reliable but would shift with 2–3 more data points. |
| **Low** | Fewer than 5 comparables. The range is indicative only — a signal, not a forecast. |
| **No precedent** | Zero comparables. The tool explicitly refuses to show a number. Fabricating a range from zero data points would be worse than saying nothing. |

---

## Limitations — What Would Need to Change Before Using This With Real Money

**1. Market inflation is not accounted for.** A €20M player in 2019 and a €20M player in 2024 are not the same. The broader football market has inflated significantly in that period. To trust this model in a real negotiation, you would need to index all historical valuations to a common base year — or weight more recent comps more heavily than older ones.

**2. We don't know whether the player actually played.** The valuation change for a comparable transfer could reflect an injury layoff, a position change, a loan, or a complete lack of game time rather than a genuine market reassessment of the player's quality in their new environment. Playing-time data post-transfer is not in the dataset.

**3. Age alone doesn't capture career trajectory.** Two 27-year-olds are not equivalent if one is three seasons into their peak and one is beginning to decline. A model that accounts for this would need to track year-on-year valuation trend before the move, not just the age at the time of it.

**4. The tier classification is coarse.** Treating all Tier 1 clubs as equivalent ignores the difference between signing for a Champions League contender and signing for a relegation battler in the same division. This matters — Champions League exposure significantly inflates valuations regardless of individual performance.

**5. The time window is data-driven, not deliberate.** We look at the first valuation update recorded between 6 and 18 months post-transfer. That's the window where Transfermarkt data actually exists in sufficient quantity. It is not a clean "12-month post-transfer assessment." You cannot directly compare the percentage changes between two players if one's was measured at 7 months and another's at 16 months.

**6. Small-league profiles have very few precedents.** If you're evaluating a young goalkeeper from the Norwegian league for a Tier 2 move, you may have zero historical comps. The tool says so and refuses to fabricate a number. It does not silently return a range with a false confidence label.

---

## Running the App Locally

### Prerequisites

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

### Start the App

```bash
docker-compose up
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs

### Running Tests

```bash
cd backend
bash run_tests.sh
```

38 tests covering the search service, profile service, and transition engine — including edge cases for zero-sample and single-sample scenarios.

### Regenerating the Data (Optional)

The processed JSON files are already included in the repository. If you need to rebuild them from the raw Transfermarkt dataset, see [`backend/scripts/README.md`](backend/scripts/README.md).
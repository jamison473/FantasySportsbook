from flask import Flask, jsonify

# Team stats and projections
TEAM_STATS = {
    "Baudelaire Zingaro": {"wins": 6, "losses": 8, "pf": 1654.88, "projection": 117.27},
    "The New Guy": {"wins": 10, "losses": 4, "pf": 1594.86, "projection": 119.75},
    "Lords of the Underworld": {"wins": 7, "losses": 7, "pf": 1515.94, "projection": 117.79},
    "Njoku's on You": {"wins": 11, "losses": 3, "pf": 1743.58, "projection": 124.60},
    "Darth": {"wins": 7, "losses": 7, "pf": 1534.88, "projection": 116.41},
    "Burrowing the League": {"wins": 9, "losses": 5, "pf": 1590.96, "projection": 100.75},
    "Pawn Shop": {"wins": 6, "losses": 8, "pf": 1423.38, "projection": 97.90},
    "Dr. Ooster": {"wins": 6, "losses": 8, "pf": 1474.36, "projection": 105.18},
    "The Den of Dragons": {"wins": 2, "losses": 12, "pf": 1329.56, "projection": 82.17},
    "Prime Daboo": {"wins": 6, "losses": 8, "pf": 1563.22, "projection": 103.59},
}

# Market sentiment
MARKET_SENTIMENT = {
    "Baudelaire Zingaro": 1.05,  # Public favors Zingaro (boost by 5%)
    "The New Guy": 0.95,         # Public doubts New Guy (reduce by 5%)
    "Lords of the Underworld": 0.90,  # Public doubts Lords (reduce by 10%)
    "Njoku's on You": 1.10,          # Public favors Njoku's (boost by 10%)
    "Darth": 1.00,               # Neutral sentiment
    "Burrowing the League": 0.90,  # Public doubts Burrowing (reduce by 10%)
    "Pawn Shop": 1.10,           # Public favors Pawn Shop (boost by 10%)
    "Dr. Ooster": 0.95,          # Public doubts Dr. Ooster (reduce by 5%)
    "The Den of Dragons": 1.00,  # Neutral sentiment
    "Prime Daboo": 1.00,         # Neutral sentiment
}

# Flask app setup
app = Flask(__name__)

def calculate_weighted_projection(team_name):
    """Calculate a projection using records, PF, and market sentiment."""
    stats = TEAM_STATS[team_name]
    wins = stats["wins"]
    losses = stats["losses"]
    pf = stats["pf"]
    raw_projection = stats["projection"]

    # Calculate win percentage
    total_games = wins + losses
    win_percentage = wins / total_games if total_games > 0 else 0

    # Normalize PF
    max_pf = max(team["pf"] for team in TEAM_STATS.values())
    normalized_pf = pf / max_pf

    # Weighted projection formula
    max_projection = max(team["projection"] for team in TEAM_STATS.values())
    base_projection = (
        (raw_projection * 0.5)
        + (normalized_pf * 0.4 * max_projection)
        + (win_percentage * 0.1 * max_projection)
    )

    # Apply market sentiment
    adjusted_projection = base_projection * MARKET_SENTIMENT.get(team_name, 1.00)
    return round(adjusted_projection, 2)

def calculate_moneyline(proj_a, proj_b):
    """Calculate moneylines based on projections."""
    if proj_a == proj_b:
        return 0, 0  # EVEN odds

    # Calculate probabilities
    probability_a = proj_a / (proj_a + proj_b)
    probability_b = proj_b / (proj_a + proj_b)

    # Moneyline formula
    if probability_a > probability_b:
        moneyline_a = -round(10 * round((100 * (probability_a / (1 - probability_a))) / 10))
        moneyline_b = round(10 * round((100 * ((1 - probability_b) / probability_b)) / 10))
    else:
        moneyline_a = round(10 * round((100 * ((1 - probability_a) / probability_a)) / 10))
        moneyline_b = -round(10 * round((100 * (probability_b / (1 - probability_b))) / 10))

    # Format odds with + for underdogs
    if moneyline_a > 0:
        moneyline_a = f"+{moneyline_a}"
    if moneyline_b > 0:
        moneyline_b = f"+{moneyline_b}"

    return moneyline_a, moneyline_b

@app.route('/odds')
def odds():
    # Matchups
    matchups = [
        ("Baudelaire Zingaro", "The New Guy"),
        ("Lords of the Underworld", "Njoku's on You"),
        ("Darth", "Burrowing the League"),
        ("Pawn Shop", "Dr. Ooster"),
        ("The Den of Dragons", "Prime Daboo"),
    ]

    odds_data = []
    for team_a, team_b in matchups:
        proj_a = calculate_weighted_projection(team_a)
        proj_b = calculate_weighted_projection(team_b)

        spread = round((proj_a - proj_b) / 2, 1)
        over_under = round(proj_a + proj_b, 1)
        moneyline_a, moneyline_b = calculate_moneyline(proj_a, proj_b)

        odds_data.append({
            "matchup": f"{team_a} vs {team_b}",
            "spread": f"{team_a} {spread} / {team_b} {-spread}",
            "over_under": f"Total: {over_under}",
            "moneyline": f"{team_a}: {moneyline_a} / {team_b}: {moneyline_b}",
        })

    return jsonify(odds_data)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Render provides the PORT variable
    app.run(host="0.0.0.0", port=port)        # Listen on all interfaces

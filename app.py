from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("players.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/players")
def players():

    conn = get_db()

    players = conn.execute("""
        SELECT
            players.*,
            countries.CountryName,
            clubs.ClubName,
            positions.PositionName
        FROM players
        LEFT JOIN countries
            ON players.CountryID = countries.ID
        LEFT JOIN clubs
            ON players.ClubID = clubs.ID
        LEFT JOIN positions
            ON players.PositionID = positions.ID
    """).fetchall()

    conn.close()

    return render_template("players.html", players=players)


@app.route("/countries")
def countries():
    conn = get_db()
    countries = conn.execute("SELECT * FROM countries").fetchall()
    conn.close()

    return render_template("countries.html", countries=countries)

@app.route("/clubs")
def clubs():
    conn = get_db()
    clubs = conn.execute("SELECT * FROM clubs").fetchall()
    conn.close()

    return render_template("clubs.html", clubs=clubs)

@app.route("/clubs/add", methods=["GET", "POST"])
def add_club():

    if request.method == "POST":

        club_name = request.form["club_name"]

        conn = sqlite3.connect("players.db")

        conn.execute(
            "INSERT INTO clubs (ClubName) VALUES (?)",
            (club_name,)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("clubs"))

    return render_template("club_form.html")

@app.route("/clubs/edit/<int:club_id>", methods=["GET", "POST"])
def edit_club(club_id):

    conn = sqlite3.connect("players.db")
    conn.row_factory = sqlite3.Row

    club = conn.execute(
        "SELECT * FROM clubs WHERE ID = ?",
        (club_id,)
    ).fetchone()

    if request.method == "POST":

        club_name = request.form["club_name"]

        conn.execute(
            "UPDATE clubs SET ClubName = ? WHERE ID = ?",
            (club_name, club_id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("clubs"))

    conn.close()

    return render_template(
        "club_form.html",
        club=club
    )


@app.route("/clubs/delete/<int:club_id>", methods=["POST"])
def delete_club(club_id):

    conn = sqlite3.connect("players.db")

    conn.execute(
        "DELETE FROM clubs WHERE ID = ?",
        (club_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("clubs"))




@app.route("/countries/add", methods=["GET", "POST"])
def add_country():

    if request.method == "POST":

        country_name = request.form["country_name"]

        conn = sqlite3.connect("players.db")

        conn.execute(
            "INSERT INTO countries (CountryName) VALUES (?)",
            (country_name,)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("countries"))

    return render_template("country_form.html")

@app.route("/countries/delete/<int:country_id>", methods=["POST"])
def delete_country(country_id):

    conn = sqlite3.connect("players.db")

    conn.execute(
        "DELETE FROM countries WHERE ID = ?",
        (country_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("countries"))


@app.route("/countries/edit/<int:country_id>", methods=["GET", "POST"])
def edit_country(country_id):

    conn = sqlite3.connect("players.db")
    conn.row_factory = sqlite3.Row

    country = conn.execute(
        "SELECT * FROM countries WHERE ID = ?",
        (country_id,)
    ).fetchone()

    if request.method == "POST":

        country_name = request.form["country_name"]

        conn.execute(
            "UPDATE countries SET CountryName = ? WHERE ID = ?",
            (country_name, country_id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("countries"))

    conn.close()

    return render_template(
        "country_form.html",
        country=country
    )

# ADD A PLAYER
@app.route("/players/add", methods=["GET", "POST"])
def add_player():

    conn = get_db()

    if request.method == "POST":

        conn.execute("""
            INSERT INTO players
            (playerName, playerImage, CountryID, ClubID, PositionID,
             Age, MarketValue, Goals, MatchesPlayed, InternationalPlayer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["playerName"],
            request.form["playerImage"],
            request.form["CountryID"],
            request.form["ClubID"],
            request.form["PositionID"],
            request.form["Age"],
            request.form["MarketValue"],
            request.form["Goals"],
            request.form["MatchesPlayed"],
            request.form["InternationalPlayer"]
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("players"))

    countries = conn.execute(
        "SELECT * FROM countries ORDER BY CountryName"
    ).fetchall()

    clubs = conn.execute(
        "SELECT * FROM clubs ORDER BY ClubName"
    ).fetchall()

    positions = conn.execute(
        "SELECT * FROM positions ORDER BY PositionName"
    ).fetchall()

    conn.close()

    return render_template(
        "player_form.html",
        player=None,
        countries=countries,
        clubs=clubs,
        positions=positions
    )


# EDIT A PLAYER
@app.route("/players/edit/<int:player_id>",
           methods=["GET", "POST"])
def edit_player(player_id):

    conn = get_db()

    player = conn.execute(
        "SELECT * FROM players WHERE playerID = ?",
        (player_id,)
    ).fetchone()

    if player is None:
        conn.close()
        return "Player not found", 404

    if request.method == "POST":

        conn.execute("""
            UPDATE players
            SET playerName = ?,
                playerImage = ?,
                CountryID = ?,
                ClubID = ?,
                PositionID = ?,
                Age = ?,
                MarketValue = ?,
                Goals = ?,
                MatchesPlayed = ?,
                InternationalPlayer = ?
            WHERE playerID = ?
        """, (
            request.form["playerName"],
            request.form["playerImage"],
            request.form["CountryID"],
            request.form["ClubID"],
            request.form["PositionID"],
            request.form["Age"],
            request.form["MarketValue"],
            request.form["Goals"],
            request.form["MatchesPlayed"],
            request.form["InternationalPlayer"],
            player_id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("players"))

    countries = conn.execute(
        "SELECT * FROM countries ORDER BY CountryName"
    ).fetchall()

    clubs = conn.execute(
        "SELECT * FROM clubs ORDER BY ClubName"
    ).fetchall()

    positions = conn.execute(
        "SELECT * FROM positions ORDER BY PositionName"
    ).fetchall()

    conn.close()

    return render_template(
        "player_form.html",
        player=player,
        countries=countries,
        clubs=clubs,
        positions=positions
    )


# DELETE A PLAYER
@app.route("/players/delete/<int:player_id>", methods=["POST"])
def delete_player(player_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM players WHERE playerID = ?",
        (player_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("players"))

# DISPLAY ALL POSITIONS
@app.route("/positions")
def positions():

    conn = get_db()

    positions = conn.execute(
        "SELECT * FROM positions"
    ).fetchall()

    conn.close()

    return render_template(
        "positions.html",
        positions=positions
    )


# ADD A POSITION
@app.route("/positions/add", methods=["GET", "POST"])
def add_position():

    if request.method == "POST":

        position_name = request.form["position_name"]

        conn = get_db()

        conn.execute(
            "INSERT INTO positions (PositionName) VALUES (?)",
            (position_name,)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("positions"))

    return render_template("position_form.html", position=None)


# EDIT A POSITION
@app.route("/positions/edit/<int:position_id>",
           methods=["GET", "POST"])
def edit_position(position_id):

    conn = get_db()

    position = conn.execute(
        "SELECT * FROM positions WHERE ID = ?",
        (position_id,)
    ).fetchone()

    if position is None:
        conn.close()
        return "Position not found", 404

    if request.method == "POST":

        position_name = request.form["position_name"]

        conn.execute(
            "UPDATE positions SET PositionName = ? WHERE ID = ?",
            (position_name, position_id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("positions"))

    conn.close()

    return render_template(
        "position_form.html",
        position=position
    )


# DELETE A POSITION
@app.route("/positions/delete/<int:position_id>",
           methods=["POST"])
def delete_position(position_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM positions WHERE ID = ?",
        (position_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("positions"))



if __name__ == "__main__":
    app.run(debug=True)



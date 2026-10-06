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
    players = conn.execute("SELECT * FROM players").fetchall()
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

if __name__ == "__main__":
    app.run(debug=True)



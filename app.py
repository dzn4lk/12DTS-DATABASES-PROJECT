from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "football-database-secret-key-2026"
)

ADMIN_EMAIL = "admin@footballdb.co.nz"
ADMIN_PASSWORD = "FootballAdmin123!"


def get_db():
    conn = sqlite3.connect("players.db")
    conn.row_factory = sqlite3.Row
    return conn


def setup_users():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Email TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL,
            Role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    admin = conn.execute(
        "SELECT ID FROM users WHERE Email = ?", (ADMIN_EMAIL,)
    ).fetchone()

    if admin is None:
        conn.execute(
            "INSERT INTO users (Email, Password, Role) VALUES (?, ?, ?)",
            (ADMIN_EMAIL, generate_password_hash(ADMIN_PASSWORD), "admin")
        )

    conn.commit()
    conn.close()


setup_users()


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)
    return wrapper


def admin_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("You do not have permission to access that page.")
            return redirect(url_for("players"))
        return route_function(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    return render_template("home.html")


# VIEW AND FILTER PLAYERS
@app.route("/players")
@login_required
def players():
    conn = get_db()

    country_id = request.args.get("country_id", "")
    club_id = request.args.get("club_id", "")
    position_id = request.args.get("position_id", "")
    age_group = request.args.get("age_group", "")
    value_group = request.args.get("value_group", "")
    international = request.args.get("international", "")
    search_name = request.args.get("search_name", "").strip()

    query = """
        SELECT players.*, countries.CountryName, clubs.ClubName,
               positions.PositionName
        FROM players
        LEFT JOIN countries ON players.CountryID = countries.ID
        LEFT JOIN clubs ON players.ClubID = clubs.ID
        LEFT JOIN positions ON players.PositionID = positions.ID
        WHERE 1 = 1
    """
    parameters = []

    if country_id:
        query += " AND players.CountryID = ?"
        parameters.append(country_id)

    if club_id:
        query += " AND players.ClubID = ?"
        parameters.append(club_id)

    if position_id:
        query += " AND players.PositionID = ?"
        parameters.append(position_id)

    if age_group == "under20":
        query += " AND players.Age < 20"
    elif age_group == "20to24":
        query += " AND players.Age BETWEEN 20 AND 24"
    elif age_group == "25to29":
        query += " AND players.Age BETWEEN 25 AND 29"
    elif age_group == "30plus":
        query += " AND players.Age >= 30"

    if value_group == "under10":
        query += " AND players.MarketValue < 10"
    elif value_group == "10to50":
        query += " AND players.MarketValue BETWEEN 10 AND 50"
    elif value_group == "over50":
        query += " AND players.MarketValue > 50"

    if international in ("0", "1"):
        query += " AND players.InternationalPlayer = ?"
        parameters.append(international)

    if search_name:
        query += " AND players.playerName LIKE ?"
        parameters.append("%" + search_name + "%")

    query += " ORDER BY players.playerName"

    player_rows = conn.execute(query, parameters).fetchall()
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
        "players.html",
        players=player_rows,
        countries=countries,
        clubs=clubs,
        positions=positions,
        selected_country=country_id,
        selected_club=club_id,
        selected_position=position_id,
        selected_age=age_group,
        selected_value=value_group,
        selected_international=international,
        search_name=search_name
    )


# COUNTRIES
@app.route("/countries")
@admin_required
def countries():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM countries ORDER BY CountryName"
    ).fetchall()
    conn.close()
    return render_template("countries.html", countries=rows)


@app.route("/countries/add", methods=["GET", "POST"])
@admin_required
def add_country():
    if request.method == "POST":
        name = request.form.get("country_name", "").strip()

        if name:
            conn = get_db()
            conn.execute(
                "INSERT INTO countries (CountryName) VALUES (?)", (name,)
            )
            conn.commit()
            conn.close()
            flash("Country added.")
            return redirect(url_for("countries"))

        flash("Enter a country name.")

    return render_template("country_form.html", country=None)


@app.route("/countries/edit/<int:country_id>", methods=["GET", "POST"])
@admin_required
def edit_country(country_id):
    conn = get_db()
    country = conn.execute(
        "SELECT * FROM countries WHERE ID = ?", (country_id,)
    ).fetchone()

    if country is None:
        conn.close()
        return "Country not found", 404

    if request.method == "POST":
        name = request.form.get("country_name", "").strip()

        if name:
            conn.execute(
                "UPDATE countries SET CountryName = ? WHERE ID = ?",
                (name, country_id)
            )
            conn.commit()
            conn.close()
            flash("Country updated.")
            return redirect(url_for("countries"))

        flash("Enter a country name.")

    conn.close()
    return render_template("country_form.html", country=country)


@app.route("/countries/delete/<int:country_id>", methods=["POST"])
@admin_required
def delete_country(country_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM countries WHERE ID = ?", (country_id,))
        conn.commit()
        flash("Country deleted.")
    except sqlite3.IntegrityError:
        flash("This country is linked to players and cannot be deleted.")
    finally:
        conn.close()
    return redirect(url_for("countries"))


# CLUBS
@app.route("/clubs")
@admin_required
def clubs():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM clubs ORDER BY ClubName"
    ).fetchall()
    conn.close()
    return render_template("clubs.html", clubs=rows)


@app.route("/clubs/add", methods=["GET", "POST"])
@admin_required
def add_club():
    if request.method == "POST":
        name = request.form.get("club_name", "").strip()

        if name:
            conn = get_db()
            conn.execute("INSERT INTO clubs (ClubName) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            flash("Club added.")
            return redirect(url_for("clubs"))

        flash("Enter a club name.")

    return render_template("club_form.html", club=None)


@app.route("/clubs/edit/<int:club_id>", methods=["GET", "POST"])
@admin_required
def edit_club(club_id):
    conn = get_db()
    club = conn.execute(
        "SELECT * FROM clubs WHERE ID = ?", (club_id,)
    ).fetchone()

    if club is None:
        conn.close()
        return "Club not found", 404

    if request.method == "POST":
        name = request.form.get("club_name", "").strip()

        if name:
            conn.execute(
                "UPDATE clubs SET ClubName = ? WHERE ID = ?", (name, club_id)
            )
            conn.commit()
            conn.close()
            flash("Club updated.")
            return redirect(url_for("clubs"))

        flash("Enter a club name.")

    conn.close()
    return render_template("club_form.html", club=club)


@app.route("/clubs/delete/<int:club_id>", methods=["POST"])
@admin_required
def delete_club(club_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM clubs WHERE ID = ?", (club_id,))
        conn.commit()
        flash("Club deleted.")
    except sqlite3.IntegrityError:
        flash("This club is linked to players and cannot be deleted.")
    finally:
        conn.close()
    return redirect(url_for("clubs"))


# ADD PLAYER
@app.route("/players/add", methods=["GET", "POST"])
@admin_required
def add_player():
    conn = get_db()

    if request.method == "POST":
        fields = (
            request.form.get("playerName", "").strip(),
            request.form.get("playerImage", "").strip(),
            request.form.get("CountryID") or None,
            request.form.get("ClubID") or None,
            request.form.get("PositionID") or None,
            request.form.get("Age") or None,
            request.form.get("MarketValue") or None,
            request.form.get("Goals") or None,
            request.form.get("MatchesPlayed") or None,
            request.form.get("InternationalPlayer", "0")
        )

        if fields[0]:
            conn.execute("""
                INSERT INTO players
                (playerName, playerImage, CountryID, ClubID, PositionID,
                 Age, MarketValue, Goals, MatchesPlayed, InternationalPlayer)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, fields)
            conn.commit()
            conn.close()
            flash("Player added.")
            return redirect(url_for("players"))

        flash("Enter the player's name.")

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
        "player_form.html", player=None,
        countries=countries, clubs=clubs, positions=positions
    )


# EDIT PLAYER
@app.route("/players/edit/<int:player_id>", methods=["GET", "POST"])
@admin_required
def edit_player(player_id):
    conn = get_db()
    player = conn.execute(
        "SELECT * FROM players WHERE playerID = ?", (player_id,)
    ).fetchone()

    if player is None:
        conn.close()
        return "Player not found", 404

    if request.method == "POST":
        fields = (
            request.form.get("playerName", "").strip(),
            request.form.get("playerImage", "").strip(),
            request.form.get("CountryID") or None,
            request.form.get("ClubID") or None,
            request.form.get("PositionID") or None,
            request.form.get("Age") or None,
            request.form.get("MarketValue") or None,
            request.form.get("Goals") or None,
            request.form.get("MatchesPlayed") or None,
            request.form.get("InternationalPlayer", "0"),
            player_id
        )

        if fields[0]:
            conn.execute("""
                UPDATE players
                SET playerName = ?, playerImage = ?, CountryID = ?,
                    ClubID = ?, PositionID = ?, Age = ?, MarketValue = ?,
                    Goals = ?, MatchesPlayed = ?, InternationalPlayer = ?
                WHERE playerID = ?
            """, fields)
            conn.commit()
            conn.close()
            flash("Player updated.")
            return redirect(url_for("players"))

        flash("Enter the player's name.")

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
        "player_form.html", player=player,
        countries=countries, clubs=clubs, positions=positions
    )


# DELETE PLAYER
@app.route("/players/delete/<int:player_id>", methods=["POST"])
@admin_required
def delete_player(player_id):
    conn = get_db()
    conn.execute("DELETE FROM players WHERE playerID = ?", (player_id,))
    conn.commit()
    conn.close()
    flash("Player deleted.")
    return redirect(url_for("players"))


# POSITIONS
@app.route("/positions")
@admin_required
def positions():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM positions ORDER BY PositionName"
    ).fetchall()
    conn.close()
    return render_template("positions.html", positions=rows)


@app.route("/positions/add", methods=["GET", "POST"])
@admin_required
def add_position():
    if request.method == "POST":
        name = request.form.get("position_name", "").strip()

        if name:
            conn = get_db()
            conn.execute(
                "INSERT INTO positions (PositionName) VALUES (?)", (name,)
            )
            conn.commit()
            conn.close()
            flash("Position added.")
            return redirect(url_for("positions"))

        flash("Enter a position name.")

    return render_template("position_form.html", position=None)


@app.route("/positions/edit/<int:position_id>", methods=["GET", "POST"])
@admin_required
def edit_position(position_id):
    conn = get_db()
    position = conn.execute(
        "SELECT * FROM positions WHERE ID = ?", (position_id,)
    ).fetchone()

    if position is None:
        conn.close()
        return "Position not found", 404

    if request.method == "POST":
        name = request.form.get("position_name", "").strip()

        if name:
            conn.execute(
                "UPDATE positions SET PositionName = ? WHERE ID = ?",
                (name, position_id)
            )
            conn.commit()
            conn.close()
            flash("Position updated.")
            return redirect(url_for("positions"))

        flash("Enter a position name.")

    conn.close()
    return render_template("position_form.html", position=position)


@app.route("/positions/delete/<int:position_id>", methods=["POST"])
@admin_required
def delete_position(position_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM positions WHERE ID = ?", (position_id,))
        conn.commit()
        flash("Position deleted.")
    except sqlite3.IntegrityError:
        flash("This position is linked to players and cannot be deleted.")
    finally:
        conn.close()
    return redirect(url_for("positions"))


# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Enter an email and password.")
            return render_template("signup.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.")
            return render_template("signup.html")

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (Email, Password, Role) VALUES (?, ?, ?)",
                (email, generate_password_hash(password), "user")
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("That email already has an account.")
            return render_template("signup.html")

        conn.close()
        flash("Account created. Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE Email = ?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["Password"], password):
            session.clear()
            session["user_id"] = user["ID"]
            session["email"] = user["Email"]
            session["role"] = user["Role"]
            flash("You are now logged in.")
            return redirect(url_for("home"))

        flash("Incorrect email or password.")

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template
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

if __name__ == "__main__":
    app.run(debug=True)

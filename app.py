# - - - - - - - - - - - - - - - - - - - - -
# Hovedsakelig så bruker jeg NextLibrary
# Dette er en spesiallaget bibliotek for å lage webapplikasjoner (av meg)
# Den er automatisert og gjør det enklere å lage webapplikasjoner
# Den bruker templates og blokker for å gjøre det enklere å lage webapplikasjoner
# - - - - - - - - - - - - - - - - - - - - -



# - - - - - - - - - - - - - - - - - - - - -
# Importerer nødvendige biblioteker
# Flask er et rammeverk for å lage webapplikasjoner
# request er en del av Flask og lar oss hente ut data fra forespørselen
# jsonify lar oss returnere JSON-data
# render_template lar oss returnere HTML-filer
# sqlite3 lar oss jobbe med SQLite-databaser
# - - - - - - - - - - - - - - - - - - - - -

from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# - - - - - - - - - - - - - - - - - - - - -
# Denne funksjonen initialiserer databasen
# Vi bruker SQLite fordi det er enkelt å sette opp
# Vi bruker with fordi vi vil at databasen skal lukkes automatisk
# Hvis tabellen ikke eksisterer, lager vi den
# - - - - - - - - - - - - - - - - - - - - -

def init_db():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS login
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''') # -> Lager en tabell med kolonnene id, username og password
        con.commit()  # -> Commiter endringene

# Hyperkobling til index.html
@app.route('/')
def index():
    return render_template('index.html')

# Hyperkobling til students.html
@app.route('/students', methods=['POST', 'GET'])
def redirect():
    return render_template('students.html')



# - - - - - - - - - - - - - - - - - - - - -
# Denne funksjonen henter ut alle studentene fra databasen og returnerer dem som en liste
# Grunnen til at con.row_factory = sqlite3.Row er for å kunne hente ut kolonnenavnene
# Dette gjør det enklere å jobbe med dataene i HTML-filen
# en annen måte vi kan gjøre dette på er å bruke pandas
# -> pd.read_sql_query("SELECT * FROM students", con)
# men dette er enklere for nå
# - - - - - - - - - - - - - - - - - - - - -

@app.route('/display', methods=['POST', 'GET'])
def display():
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row  # Dette gjør at vi kan hente ut kolonnenavnene
        cur = con.cursor()
        cur.execute("SELECT username, password FROM login") # -> Henter ut brukernavn og passord fra databasen
        records = cur.fetchall() # -> Henter ut alle radene som samsvarer med spørringen
        

        for record in records:
            print(f"Username: {record['username']}, Password: {record['password']}") # -> Printer ut brukernavn og passord
        
    return render_template('display.html', records=records)


# - - - - - - - - - - - - - - - - - - - - -
# Denne funksjonen legger til en student i databasen
# Vi bruker POST fordi vi sender data til serveren
# Vi bruker GET fordi vi sender data tilbake til klienten
# Først henter vi ut dataene fra request.form
# Deretter prøver vi å legge til studenten i databasen
# Vi sjekker om studenten allerede eksisterer
# Hvis studenten eksisterer får vi en IntegrityError
# Hvis det er en annen feil får vi en annen type feil
# - - - - - - - - - - - - - - - - - - - - -

@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        msg = ""
        try:
            username = request.form['username']
            password = request.form['password']

            with sqlite3.connect('database.db') as con:
                # se om brukernavnet allerede eksisterer
                cur = con.cursor()
                cur.execute("SELECT * FROM login WHERE username = ?", (username,)) # -> Henter ut brukernavnet fra databasen
                records = cur.fetchall()
                if records:
                    msg = "Username already exists"  # -> Hvis brukernavnet allerede eksisterer
                else:
                    cur.execute("INSERT INTO login (username, password) VALUES (?, ?)", (username, password)) # -> Legger til brukernavnet i databasen
                    con.commit() # -> Commiter endringene
                    msg = "Record successfully added" # -> Hvis brukernavnet ikke eksisterer
        except sqlite3.IntegrityError:
            msg = "Username already exists" # -> Hvis brukernavnet allerede eksisterer
        except Exception as e:
            msg = f"Error in insert operation: {str(e)}" # -> Hvis det oppstår en annen feil
        finally:
            return render_template('result.html', msg=msg)
    return render_template('result2.html')


# - - - - - - - - - - - - - - - - - - - - -
# Denne funksjonen logger inn en bruker
# Vi bruker POST fordi vi sender data til serveren
# Vi bruker GET fordi vi sender data tilbake til klienten
# Først henter vi ut dataene fra request.form
# Deretter prøver vi å logge inn brukeren
# Vi sjekker om brukeren eksisterer i databasen
# hvis brukeren ikke eksisterer, får vi en feil
# hvis brukeren eksisterer, får vi en suksessmelding
# - - - - - - - - - - - - - - - - - - - - -

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        msg = ""
        try:
            username = request.form['username']
            password = request.form['password']
            with sqlite3.connect('database.db') as con:
                cur = con.cursor() # -> con.cursor() er en metode som returnerer en cursor-objekt
                cur.execute("SELECT * FROM login WHERE username = ? AND password = ?", (username, password)) 

                # -> execute er en metode som kjører en SQL-spørring

                records = cur.fetchall() 
                # -> fetchall er en metode som henter alle radene som samsvarer med spørringen

                if records:
                    msg = "Login successful" # -> Hvis brukeren finnes i databasen
                else:
                    msg = "Login failed" # -> Hvis brukeren ikke finnes i databasen

        except Exception as e: # -> Hvis det oppstår en feil

            msg = f"Error in login: {str(e)}" # -> Skriv ut feilmeldingen

        finally: # -> God praksis å ha en finally-blokk
            return render_template('result.html', msg=msg) # -> Returner resultatet
    return render_template('login.html') # -> Hvis det ikke er en POST-metode, returner login.html

if __name__ == '__main__':
    init_db() # -> Denne funksjonen kjører kun én gang - når serveren starter - for å initialisere databasen
    app.run(debug=True)
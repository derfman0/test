import tkinter as tk

# ---------- Funktionen ----------

def taste_gedrueckt(zeichen):
    """Fügt das gedrückte Zeichen an die Anzeige an."""
    aktueller_text = anzeige.get()
    anzeige.delete(0, tk.END)
    anzeige.insert(0, aktueller_text + zeichen)


def loeschen():
    """Leert die Anzeige komplett."""
    anzeige.delete(0, tk.END)


def rueckgaengig():
    """Löscht das letzte Zeichen."""
    aktueller_text = anzeige.get()
    anzeige.delete(0, tk.END)
    anzeige.insert(0, aktueller_text[:-1])


def berechnen():
    """Wertet den eingegebenen Ausdruck aus."""
    ausdruck = anzeige.get()
    try:
        # Komma durch Punkt ersetzen, falls jemand mit Komma rechnet
        ausdruck = ausdruck.replace(",", ".")
        ergebnis = eval(ausdruck)
        anzeige.delete(0, tk.END)
        anzeige.insert(0, str(ergebnis))
    except ZeroDivisionError:
        anzeige.delete(0, tk.END)
        anzeige.insert(0, "Fehler: /0")
    except Exception:
        anzeige.delete(0, tk.END)
        anzeige.insert(0, "Fehler")


# ---------- Fenster einrichten ----------

fenster = tk.Tk()
fenster.title("Taschenrechner")
fenster.resizable(False, False)
fenster.configure(bg="#2b2b2b")

# ---------- Anzeige ----------

anzeige = tk.Entry(
    fenster,
    font=("Arial", 24),
    justify="right",
    bd=0,
    bg="#1e1e1e",
    fg="white",
    insertbackground="white",
)
anzeige.grid(row=0, column=0, columnspan=4, ipady=20, sticky="we", padx=10, pady=10)

# ---------- Tasten-Layout ----------

tasten = [
    ("C", 1, 0), ("⌫", 1, 1), ("%", 1, 2), ("/", 1, 3),
    ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("*", 2, 3),
    ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("-", 3, 3),
    ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("+", 4, 3),
    ("0", 5, 0), (",", 5, 1), ("=", 5, 2, 2),  # "=" nimmt 2 Spalten ein
]

farbe_zahl = "#3c3c3c"
farbe_operator = "#ff9500"
farbe_funktion = "#a5a5a5"

for taste in tasten:
    text = taste[0]
    zeile = taste[1]
    spalte = taste[2]
    spannweite = taste[3] if len(taste) > 3 else 1

    if text == "C":
        befehl = loeschen
        farbe = farbe_funktion
    elif text == "⌫":
        befehl = rueckgaengig
        farbe = farbe_funktion
    elif text == "=":
        befehl = berechnen
        farbe = farbe_operator
    elif text in ("+", "-", "*", "/", "%"):
        befehl = lambda z=text: taste_gedrueckt(z)
        farbe = farbe_operator
    else:
        befehl = lambda z=text: taste_gedrueckt(z)
        farbe = farbe_zahl

    button = tk.Button(
        fenster,
        text=text,
        font=("Arial", 18),
        bg=farbe,
        fg="white",
        bd=0,
        activebackground="#555555",
        activeforeground="white",
        command=befehl,
    )
    button.grid(
        row=zeile,
        column=spalte,
        columnspan=spannweite,
        sticky="we",
        padx=5,
        pady=5,
        ipady=10,
    )

# Spalten gleichmäßig verteilen
for i in range(4):
    fenster.grid_columnconfigure(i, weight=1)

# ---------- Tastatur-Unterstützung ----------

def taste_gedrueckt_event(event):
    zeichen = event.char
    if zeichen in "0123456789+-*/.,%":
        taste_gedrueckt(zeichen)
    elif event.keysym == "Return":
        berechnen()
    elif event.keysym == "BackSpace":
        rueckgaengig()
    elif event.keysym == "Escape":
        loeschen()

fenster.bind("<Key>", taste_gedrueckt_event)

# ---------- Hauptschleife ----------

fenster.mainloop()

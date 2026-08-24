import streamlit as st
import ast
import operator
import re

# ============================================================
# SEITE
# ============================================================

st.set_page_config(
    page_title="Taschenrechner",
    page_icon="🧮",
    layout="centered",
)

# ============================================================
# SICHERE BERECHNUNG
# ============================================================

OPERATOREN = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def sicher_auswerten(knoten):
    """Berechnet nur erlaubte mathematische AST-Ausdrücke."""

    if isinstance(knoten, ast.Constant):
        if isinstance(knoten.value, (int, float)):
            return knoten.value
        raise ValueError("Ungültige Zahl")

    if isinstance(knoten, ast.BinOp):
        op_typ = type(knoten.op)

        if op_typ not in OPERATOREN:
            raise ValueError("Operator nicht erlaubt")

        links = sicher_auswerten(knoten.left)
        rechts = sicher_auswerten(knoten.right)

        return OPERATOREN[op_typ](links, rechts)

    if isinstance(knoten, ast.UnaryOp):
        op_typ = type(knoten.op)

        if op_typ not in OPERATOREN:
            raise ValueError("Operator nicht erlaubt")

        return OPERATOREN[op_typ](
            sicher_auswerten(knoten.operand)
        )

    raise ValueError("Ungültiger Ausdruck")


def berechne_ausdruck(text):
    """Wandelt den Ausdruck um und berechnet ihn."""

    text = text.replace(",", ".")
    text = text.replace("×", "*")
    text = text.replace("÷", "/")

    # Prozent behandeln
    text = re.sub(
        r"(\d+(?:\.\d+)?)%",
        r"(\1/100)",
        text
    )

    # Nur erlaubte Zeichen
    if not re.fullmatch(
        r"[0-9\.\+\-\*/\(\)\s]+",
        text
    ):
        raise ValueError("Ungültige Zeichen")

    baum = ast.parse(text, mode="eval")

    return sicher_auswerten(baum.body)


# ============================================================
# SESSION STATE
# ============================================================

if "eingabe" not in st.session_state:
    st.session_state.eingabe = ""


def taste(zeichen):
    """Fügt eine Taste zur Anzeige hinzu."""

    # Fehleranzeige löschen, wenn neue Eingabe beginnt
    if st.session_state.eingabe.startswith("Fehler"):
        st.session_state.eingabe = ""

    st.session_state.eingabe += zeichen


def loeschen():
    """Komplett löschen."""

    st.session_state.eingabe = ""


def rueckgaengig():
    """Letztes Zeichen löschen."""

    if st.session_state.eingabe.startswith("Fehler"):
        st.session_state.eingabe = ""
    else:
        st.session_state.eingabe = st.session_state.eingabe[:-1]


def berechnen():
    """Ausdruck berechnen."""

    if not st.session_state.eingabe:
        return

    try:
        ergebnis = berechne_ausdruck(
            st.session_state.eingabe
        )

        # 5.0 wird zu 5
        if isinstance(ergebnis, float) and ergebnis.is_integer():
            ergebnis = int(ergebnis)

        st.session_state.eingabe = str(ergebnis)

    except ZeroDivisionError:
        st.session_state.eingabe = "Fehler: Division durch 0"

    except Exception:
        st.session_state.eingabe = "Fehler"


# ============================================================
# DESIGN
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       HAUPTSEITE
    -------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at top,
                #242424 0%,
                #121212 45%,
                #0b0b0b 100%
            );

        color: white;
    }

    /* Hauptcontainer etwas schmaler */
    .block-container {
        max-width: 500px;
        padding-top: 35px;
        padding-bottom: 40px;
    }


    /* --------------------------------------------------------
       TITEL
    -------------------------------------------------------- */

    .calculator-title {
        text-align: center;
        color: #ffffff;
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -1px;
    }

    .calculator-subtitle {
        text-align: center;
        color: #888888;
        font-size: 14px;
        margin-bottom: 25px;
    }


    /* --------------------------------------------------------
       ANZEIGE
    -------------------------------------------------------- */

    div[data-testid="stTextInput"] {
        margin-bottom: 18px;
    }

    div[data-testid="stTextInput"] input {
        width: 100% !important;

        background-color: #1b1b1b !important;

        color: #ffffff !important;

        border: 1px solid #333333 !important;

        border-radius: 18px !important;

        height: 90px !important;

        padding: 10px 20px !important;

        font-size: 42px !important;

        font-weight: 600 !important;

        text-align: right !important;

        box-shadow:
            inset 0 2px 10px rgba(0,0,0,0.35),
            0 8px 25px rgba(0,0,0,0.25);

        transition: all 0.2s ease;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #ff9500 !important;

        box-shadow:
            0 0 0 2px rgba(255,149,0,0.15),
            inset 0 2px 10px rgba(0,0,0,0.35);
    }


    /* --------------------------------------------------------
       NORMALE TASTEN
    -------------------------------------------------------- */

    div[data-testid="stButton"] button {
        width: 100%;

        height: 76px;

        border-radius: 18px;

        border: 1px solid #383838;

        background: linear-gradient(
            145deg,
            #303030,
            #252525
        );

        color: #ffffff !important;

        font-size: 29px !important;

        font-weight: 700 !important;

        box-shadow:
            0 5px 12px rgba(0,0,0,0.30),
            inset 0 1px 0 rgba(255,255,255,0.04);

        transition:
            transform 0.08s ease,
            background 0.15s ease,
            box-shadow 0.15s ease;

        margin-bottom: 10px;
    }


    /* Hover */

    div[data-testid="stButton"] button:hover {
        background: linear-gradient(
            145deg,
            #3b3b3b,
            #303030
        );

        color: #ffffff !important;

        border-color: #4a4a4a;

        transform: translateY(-2px);

        box-shadow:
            0 8px 18px rgba(0,0,0,0.40);
    }


    /* Beim Klicken */

    div[data-testid="stButton"] button:active {
        transform: scale(0.96);
    }


    /* --------------------------------------------------------
       OPERATOR-TASTEN
    -------------------------------------------------------- */

    .operator button {
        background: linear-gradient(
            145deg,
            #ff9f0a,
            #e67e00
        ) !important;

        color: white !important;

        border: none !important;
    }

    .operator button:hover {
        background: linear-gradient(
            145deg,
            #ffb340,
            #f28b00
        ) !important;
    }


    /* --------------------------------------------------------
       C - LÖSCHTASTE
    -------------------------------------------------------- */

    .clear-button button {
        background: linear-gradient(
            145deg,
            #ff453a,
            #c62828
        ) !important;

        color: white !important;

        border: none !important;
    }

    .clear-button button:hover {
        background: linear-gradient(
            145deg,
            #ff6258,
            #e53935
        ) !important;
    }


    /* --------------------------------------------------------
       RÜCKGÄNGIG
    -------------------------------------------------------- */

    .back-button button {
        background: linear-gradient(
            145deg,
            #454545,
            #333333
        ) !important;
    }


    /* --------------------------------------------------------
       GLEICH
    -------------------------------------------------------- */

    .equals-button button {
        height: 78px !important;

        border-radius: 18px !important;

        background: linear-gradient(
            145deg,
            #ff9f0a,
            #e67e00
        ) !important;

        color: white !important;

        border: none !important;

        font-size: 34px !important;

        font-weight: 800 !important;

        box-shadow:
            0 6px 18px rgba(255,149,0,0.25);
    }

    .equals-button button:hover {
        background: linear-gradient(
            145deg,
            #ffb340,
            #f28b00
        ) !important;

        box-shadow:
            0 8px 24px rgba(255,149,0,0.35);
    }


    /* --------------------------------------------------------
       ABSTÄNDE
    -------------------------------------------------------- */

    div[data-testid="column"] {
        padding-left: 4px;
        padding-right: 4px;
    }


    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .footer {
        text-align: center;

        color: #555555;

        font-size: 12px;

        margin-top: 22px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# OBERFLÄCHE
# ============================================================

st.markdown(
    '<div class="calculator-title">🧮 Taschenrechner</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="calculator-subtitle">'
    'Einfach · Schnell · Sicher'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# ANZEIGE
# ============================================================

st.text_input(
    "Anzeige",
    key="eingabe",
    label_visibility="collapsed",
    placeholder="0",
)


# ============================================================
# TASTATUR
# ============================================================

reihen = [
    ["C", "⌫", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "−"],
    ["1", "2", "3", "+"],
    ["(", "0", ")", ","],
]


for r_index, reihe in enumerate(reihen):

    spalten = st.columns(4)

    for s_index, text in enumerate(reihe):

        with spalten[s_index]:

            # C
            if text == "C":

                st.markdown(
                    '<div class="clear-button">',
                    unsafe_allow_html=True
                )

                st.button(
                    "C",
                    on_click=loeschen,
                    key=f"clear_{r_index}_{s_index}",
                    use_container_width=True,
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            # Rückgängig
            elif text == "⌫":

                st.markdown(
                    '<div class="back-button">',
                    unsafe_allow_html=True
                )

                st.button(
                    "⌫",
                    on_click=rueckgaengig,
                    key=f"back_{r_index}_{s_index}",
                    use_container_width=True,
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            # Operatoren
            elif text in ["÷", "×", "−", "+", "%"]:

                st.markdown(
                    '<div class="operator">',
                    unsafe_allow_html=True
                )

                st.button(
                    text,
                    on_click=taste,
                    args=(text,),
                    key=f"operator_{r_index}_{s_index}",
                    use_container_width=True,
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            # Normale Tasten
            else:

                st.button(
                    text,
                    on_click=taste,
                    args=(text,),
                    key=f"number_{r_index}_{s_index}",
                    use_container_width=True,
                )


# ============================================================
# GLEICH
# ============================================================

st.markdown(
    '<div class="equals-button">',
    unsafe_allow_html=True
)

st.button(
    "=",
    on_click=berechnen,
    key="equals",
    use_container_width=True,
)

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">Python + Streamlit 🐍</div>',
    unsafe_allow_html=True
)

import streamlit as st
import ast
import operator
import re

st.set_page_config(page_title="Taschenrechner", page_icon="🧮", layout="centered")

# ---------- Sichere Berechnung (ohne eval) ----------

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
    if isinstance(knoten, ast.Constant):
        return knoten.value
    if isinstance(knoten, ast.BinOp):
        op_typ = type(knoten.op)
        if op_typ not in OPERATOREN:
            raise ValueError("Operator nicht erlaubt")
        return OPERATOREN[op_typ](sicher_auswerten(knoten.left), sicher_auswerten(knoten.right))
    if isinstance(knoten, ast.UnaryOp):
        op_typ = type(knoten.op)
        if op_typ not in OPERATOREN:
            raise ValueError("Operator nicht erlaubt")
        return OPERATOREN[op_typ](sicher_auswerten(knoten.operand))
    raise ValueError("Ungültiger Ausdruck")


def berechne_ausdruck(text):
    text = text.replace(",", ".").replace("%", "/100")
    if not re.fullmatch(r"[0-9\.\+\-\*/\(\)\s]+", text):
        raise ValueError("Ungültige Zeichen")
    baum = ast.parse(text, mode="eval")
    return sicher_auswerten(baum.body)


# ---------- Session State ----------

if "ausdruck" not in st.session_state:
    st.session_state.ausdruck = ""


def taste(zeichen):
    st.session_state.ausdruck += zeichen


def loeschen():
    st.session_state.ausdruck = ""


def rueckgaengig():
    st.session_state.ausdruck = st.session_state.ausdruck[:-1]


def berechnen():
    if not st.session_state.ausdruck:
        return
    try:
        ergebnis = berechne_ausdruck(st.session_state.ausdruck)
        if isinstance(ergebnis, float) and ergebnis.is_integer():
            ergebnis = int(ergebnis)
        st.session_state.ausdruck = str(ergebnis)
    except ZeroDivisionError:
        st.session_state.ausdruck = "Fehler: /0"
    except Exception:
        st.session_state.ausdruck = "Fehler"


# ---------- Dunkles Design ----------

st.markdown(
    """
    <style>
    /* Ganzer Hintergrund */
    .stApp {
        background-color: #121212;
    }

    /* Anzeige-Feld */
    div[data-testid="stTextInput"] input {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
        font-size: 30px !important;
        text-align: right !important;
        border-radius: 10px !important;
        border: 1px solid #333 !important;
        height: 55px !important;
    }

    /* Alle normalen Tasten (Zahlen + Operatoren): dunkelgrau, weiße Schrift */
    div[data-testid="stButton"] button {
        width: 100%;
        height: 55px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        background-color: #2c2c2c;
        color: #ffffff !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #3a3a3a;
        color: #ffffff !important;
        border: none;
    }

    /* "=" Taste (type=primary): orange hervorgehoben */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #ff9500;
        color: #ffffff !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #ffab33;
    }

    /* Löschtaste "C": rot, über eindeutigen Key angesprochen */
    .st-key-btn_loeschen button {
        background-color: #e53935 !important;
        color: #ffffff !important;
    }
    .st-key-btn_loeschen button:hover {
        background-color: #ff5c5c !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Oberfläche ----------

st.markdown("<h1 style='text-align:center; color:white;'>🧮 Taschenrechner</h1>", unsafe_allow_html=True)

st.text_input(
    "Anzeige",
    value=st.session_state.ausdruck if st.session_state.ausdruck else "0",
    disabled=True,
    label_visibility="collapsed",
)

reihen = [
    ["C", "⌫", "%", "/"],
    ["7", "8", "9", "*"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["(", "0", ")", ","],
]

for r_index, reihe in enumerate(reihen):
    spalten = st.columns(4)
    for s_index, text in enumerate(reihe):
        if text == "C":
            spalten[s_index].button(text, on_click=loeschen, key="btn_loeschen")
        elif text == "⌫":
            spalten[s_index].button(text, on_click=rueckgaengig, key=f"btn_{r_index}_{s_index}")
        else:
            spalten[s_index].button(text, on_click=taste, args=(text,), key=f"btn_{r_index}_{s_index}")

st.button("=", on_click=berechnen, use_container_width=True, type="primary", key="btn_gleich")

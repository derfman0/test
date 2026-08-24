import streamlit as st
import re
import ast
import operator

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
        links = sicher_auswerten(knoten.left)
        rechts = sicher_auswerten(knoten.right)
        return OPERATOREN[op_typ](links, rechts)
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
if "verlauf" not in st.session_state:
    st.session_state.verlauf = []
if "fehler" not in st.session_state:
    st.session_state.fehler = False


def taste_gedrueckt(zeichen):
    if st.session_state.fehler:
        st.session_state.ausdruck = ""
        st.session_state.fehler = False
    st.session_state.ausdruck += zeichen


def loeschen():
    st.session_state.ausdruck = ""
    st.session_state.fehler = False


def rueckgaengig():
    st.session_state.ausdruck = st.session_state.ausdruck[:-1]
    st.session_state.fehler = False


def berechnen():
    ausdruck = st.session_state.ausdruck
    if not ausdruck:
        return
    try:
        ergebnis = berechne_ausdruck(ausdruck)
        if isinstance(ergebnis, float) and ergebnis.is_integer():
            ergebnis = int(ergebnis)
        st.session_state.verlauf.insert(0, f"{ausdruck} = {ergebnis}")
        st.session_state.verlauf = st.session_state.verlauf[:8]
        st.session_state.ausdruck = str(ergebnis)
        st.session_state.fehler = False
    except ZeroDivisionError:
        st.session_state.ausdruck = "Fehler: Division durch 0"
        st.session_state.fehler = True
    except Exception:
        st.session_state.ausdruck = "Fehler: ungültiger Ausdruck"
        st.session_state.fehler = True


# ---------- Eigenes CSS ----------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #121212;
    }
    div[data-testid="stTextInput"] input {
        background-color: #1e1e1e;
        color: #ffffff;
        font-size: 32px;
        text-align: right;
        border-radius: 10px;
        border: 1px solid #333;
        height: 60px;
    }
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
        border: none;
        background-color: #2c2c2c;
        color: white;
        transition: 0.15s;
    }
    div.stButton > button:hover {
        background-color: #3a3a3a;
        color: white;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Titel ----------

st.markdown("<h1 style='text-align:center; color:white;'>🧮 Taschenrechner</h1>", unsafe_allow_html=True)

# ---------- Anzeige ----------

st.text_input(
    "Anzeige",
    value=st.session_state.ausdruck if st.session_state.ausdruck else "0",
    key="anzeige_feld",
    disabled=True,
    label_visibility="collapsed",
)

# ---------- Tasten-Layout ----------

tasten = [
    ["C", "⌫", "%", "/"],
    ["7", "8", "9", "*"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["(", "0", ")", ","],
]

for reihe in tasten:
    spalten = st.columns(4)
    for spalte, text in zip(spalten, reihe):
        with spalte:
            if text == "C":
                st.button(text, on_click=loeschen, key=f"btn_{text}")
            elif text == "⌫":
                st.button(text, on_click=rueckgaengig, key=f"btn_{text}")
            else:
                st.button(text, on_click=taste_gedrueckt, args=(text,), key=f"btn_{text}")

# "=" als eigene, breite Taste
st.button("=", on_click=berechnen, use_container_width=True, type="primary", key="btn_gleich")

# ---------- Verlauf ----------

with st.expander("📜 Verlauf", expanded=False):
    if st.session_state.verlauf:
        for eintrag in st.session_state.verlauf:
            st.markdown(f"<div style='color:#ccc;'>{eintrag}</div>", unsafe_allow_html=True)
        if st.button("Verlauf löschen"):
            st.session_state.verlauf = []
            st.rerun()
    else:
        st.markdown("<div style='color:#777;'>Noch keine Berechnungen</div>", unsafe_allow_html=True)

import streamlit as st
import ast
import operator
import re

# ============================================================
# KONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Calculator",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# SICHERE MATHEMATISCHE BERECHNUNG
# ============================================================

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_eval(node):
    """Sichere Auswertung eines mathematischen Ausdrucks."""

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Ungültiger Wert")

    if isinstance(node, ast.BinOp):
        operator_type = type(node.op)

        if operator_type not in OPERATORS:
            raise ValueError("Operator nicht erlaubt")

        left = safe_eval(node.left)
        right = safe_eval(node.right)

        return OPERATORS[operator_type](left, right)

    if isinstance(node, ast.UnaryOp):
        operator_type = type(node.op)

        if operator_type not in OPERATORS:
            raise ValueError("Operator nicht erlaubt")

        return OPERATORS[operator_type](
            safe_eval(node.operand)
        )

    raise ValueError("Ungültiger Ausdruck")


def calculate(expression):
    """Berechnet einen mathematischen Ausdruck."""

    expression = expression.replace(",", ".")
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("−", "-")

    # Prozent
    expression = re.sub(
        r"(\d+(?:\.\d+)?)%",
        r"(\1/100)",
        expression,
    )

    # Nur erlaubte Zeichen
    if not re.fullmatch(
        r"[0-9\.\+\-\*/\(\)\s]+",
        expression,
    ):
        raise ValueError("Ungültige Eingabe")

    tree = ast.parse(expression, mode="eval")

    return safe_eval(tree.body)


# ============================================================
# SESSION STATE
# ============================================================

if "display" not in st.session_state:
    st.session_state.display = ""

if "history" not in st.session_state:
    st.session_state.history = []


# ============================================================
# FUNKTIONEN
# ============================================================

def add_to_display(value):
    """Taste hinzufügen."""

    if st.session_state.display.startswith("Fehler"):
        st.session_state.display = ""

    st.session_state.display += value


def clear_display():
    """Alles löschen."""

    st.session_state.display = ""


def backspace():
    """Letztes Zeichen entfernen."""

    if st.session_state.display.startswith("Fehler"):
        st.session_state.display = ""
    else:
        st.session_state.display = st.session_state.display[:-1]


def calculate_result():
    """Ergebnis berechnen."""

    expression = st.session_state.display

    if not expression:
        return

    try:
        result = calculate(expression)

        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 10)

        st.session_state.history.append(
            f"{expression} = {result}"
        )

        # Nur die letzten 5 Berechnungen behalten
        st.session_state.history = (
            st.session_state.history[-5:]
        )

        st.session_state.display = str(result)

    except ZeroDivisionError:
        st.session_state.display = "Fehler"

    except Exception:
        st.session_state.display = "Fehler"


# ============================================================
# DESIGN
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GESAMTE APP
       ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 50% -10%,
                #303030 0%,
                #171717 35%,
                #0b0b0b 75%
            );

        min-height: 100vh;
    }

    .block-container {
        max-width: 520px;
        padding-top: 35px;
        padding-bottom: 40px;
    }

    /* Streamlit Header verstecken */
    header {
        visibility: hidden;
    }

    /* ========================================================
       TITEL
       ======================================================== */

    .title {
        text-align: center;

        font-size: 36px;

        font-weight: 800;

        color: #ffffff;

        letter-spacing: -1.5px;

        margin-bottom: 4px;
    }

    .subtitle {
        text-align: center;

        color: #777777;

        font-size: 14px;

        margin-bottom: 25px;
    }

    /* ========================================================
       CALCULATOR CARD
       ======================================================== */

    .calculator-card {
        background: rgba(27, 27, 27, 0.92);

        border: 1px solid rgba(255,255,255,0.06);

        border-radius: 28px;

        padding: 22px;

        box-shadow:
            0 25px 70px rgba(0,0,0,0.45),
            inset 0 1px 0 rgba(255,255,255,0.03);
    }

    /* ========================================================
       DISPLAY
       ======================================================== */

    div[data-testid="stTextInput"] {
        margin-bottom: 18px;
    }

    div[data-testid="stTextInput"] input {
        box-sizing: border-box !important;

        width: 100% !important;

        height: 105px !important;

        background: #111111 !important;

        color: #ffffff !important;

        border: 1px solid #292929 !important;

        border-radius: 20px !important;

        padding: 15px 20px !important;

        font-size: 42px !important;

        font-weight: 600 !important;

        text-align: right !important;

        outline: none !important;

        box-shadow:
            inset 0 4px 15px rgba(0,0,0,0.45);
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #ff9500 !important;

        box-shadow:
            0 0 0 2px rgba(255,149,0,0.10),
            inset 0 4px 15px rgba(0,0,0,0.45) !important;
    }

    /* ========================================================
       BUTTONS
       ======================================================== */

    div[data-testid="column"] {
        padding-left: 4px;
        padding-right: 4px;
    }

    div[data-testid="stButton"] button {
        width: 100%;

        height: 72px;

        border-radius: 18px;

        background:
            linear-gradient(
                145deg,
                #363636,
                #282828
            );

        color: #ffffff !important;

        border: 1px solid #414141;

        font-size: 27px !important;

        font-weight: 700 !important;

        box-shadow:
            0 5px 12px rgba(0,0,0,0.25),
            inset 0 1px 0 rgba(255,255,255,0.04);

        transition:
            all 0.12s ease;

        margin-bottom: 9px;
    }

    div[data-testid="stButton"] button:hover {
        background:
            linear-gradient(
                145deg,
                #444444,
                #333333
            );

        border-color: #555555;

        transform: translateY(-2px);

        box-shadow:
            0 8px 18px rgba(0,0,0,0.35);
    }

    div[data-testid="stButton"] button:active {
        transform: scale(0.95);
    }

    /* ========================================================
       ROTE C TASTE
       ======================================================== */

    div.st-key-clear_button button {
        background:
            linear-gradient(
                145deg,
                #ff5148,
                #d62f2f
            ) !important;

        border: none !important;

        color: #ffffff !important;

        box-shadow:
            0 6px 18px rgba(255,69,58,0.22);
    }

    div.st-key-clear_button button:hover {
        background:
            linear-gradient(
                145deg,
                #ff6b63,
                #e53935
            ) !important;

        box-shadow:
            0 9px 24px rgba(255,69,58,0.35);
    }

    /* ========================================================
       OPERATOR BUTTONS
       ======================================================== */

    div.st-key-op_div button,
    div.st-key-op_mul button,
    div.st-key-op_sub button,
    div.st-key-op_add button,
    div.st-key-op_percent button {

        background:
            linear-gradient(
                145deg,
                #ff9f0a,
                #e67e00
            ) !important;

        border: none !important;

        color: #ffffff !important;

        box-shadow:
            0 6px 16px rgba(255,149,0,0.18);
    }

    div.st-key-op_div button:hover,
    div.st-key-op_mul button:hover,
    div.st-key-op_sub button:hover,
    div.st-key-op_add button:hover,
    div.st-key-op_percent button:hover {

        background:
            linear-gradient(
                145deg,
                #ffb340,
                #f28b00
            ) !important;
    }

    /* ========================================================
       GLEICH BUTTON
       ======================================================== */

    div.st-key-equals_button button {

        height: 76px !important;

        background:
            linear-gradient(
                145deg,
                #ff9f0a,
                #e67e00
            ) !important;

        color: #ffffff !important;

        border: none !important;

        font-size: 34px !important;

        font-weight: 800 !important;

        box-shadow:
            0 8px 25px rgba(255,149,0,0.25);
    }

    div.st-key-equals_button button:hover {

        background:
            linear-gradient(
                145deg,
                #ffb340,
                #f28b00
            ) !important;

        box-shadow:
            0 10px 30px rgba(255,149,0,0.35);
    }

    /* ========================================================
       HISTORY
       ======================================================== */

    .history-title {
        color: #777777;

        font-size: 12px;

        text-transform: uppercase;

        letter-spacing: 1px;

        margin-top: 15px;

        margin-bottom: 8px;
    }

    .history-item {
        background: #151515;

        color: #888888;

        border-radius: 12px;

        padding: 8px 12px;

        margin-bottom: 5px;

        font-size: 13px;

        text-align: right;
    }

    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        text-align: center;

        color: #4d4d4d;

        font-size: 12px;

        margin-top: 18px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TITEL
# ============================================================

st.markdown(
    '<div class="title">🧮 Calculator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Simple · Fast · Powerful</div>',
    unsafe_allow_html=True
)


# ============================================================
# CALCULATOR CARD START
# ============================================================

st.markdown(
    '<div class="calculator-card">',
    unsafe_allow_html=True
)


# ============================================================
# DISPLAY
# ============================================================

st.text_input(
    "display",
    key="display",
    placeholder="0",
    label_visibility="collapsed",
)


# ============================================================
# TASTATUR
# ============================================================

# Reihe 1
cols = st.columns(4)

with cols[0]:
    st.button(
        "C",
        key="clear_button",
        on_click=clear_display,
        use_container_width=True,
    )

with cols[1]:
    st.button(
        "⌫",
        key="back_button",
        on_click=backspace,
        use_container_width=True,
    )

with cols[2]:
    st.button(
        "%",
        key="op_percent",
        on_click=add_to_display,
        args=("%",),
        use_container_width=True,
    )

with cols[3]:
    st.button(
        "÷",
        key="op_div",
        on_click=add_to_display,
        args=("÷",),
        use_container_width=True,
    )


# Reihe 2
cols = st.columns(4)

for i, number in enumerate(["7", "8", "9"]):
    with cols[i]:
        st.button(
            number,
            key=f"num_{number}",
            on_click=add_to_display,
            args=(number,),
            use_container_width=True,
        )

with cols[3]:
    st.button(
        "×",
        key="op_mul",
        on_click=add_to_display,
        args=("×",),
        use_container_width=True,
    )


# Reihe 3
cols = st.columns(4)

for i, number in enumerate(["4", "5", "6"]):
    with cols[i]:
        st.button(
            number,
            key=f"num_{number}",
            on_click=add_to_display,
            args=(number,),
            use_container_width=True,
        )

with cols[3]:
    st.button(
        "−",
        key="op_sub",
        on_click=add_to_display,
        args=("−",),
        use_container_width=True,
    )


# Reihe 4
cols = st.columns(4)

for i, number in enumerate(["1", "2", "3"]):
    with cols[i]:
        st.button(
            number,
            key=f"num_{number}",
            on_click=add_to_display,
            args=(number,),
            use_container_width=True,
        )

with cols[3]:
    st.button(
        "+",
        key="op_add",
        on_click=add_to_display,
        args=("+",),
        use_container_width=True,
    )


# Reihe 5
cols = st.columns(4)

with cols[0]:
    st.button(
        "(",
        key="left_parenthesis",
        on_click=add_to_display,
        args=("(",),
        use_container_width=True,
    )

with cols[1]:
    st.button(
        "0",
        key="num_0",
        on_click=add_to_display,
        args=("0",),
        use_container_width=True,
    )

with cols[2]:
    st.button(
        ")",
        key="right_parenthesis",
        on_click=add_to_display,
        args=(")",),
        use_container_width=True,
    )

with cols[3]:
    st.button(
        ",",
        key="decimal",
        on_click=add_to_display,
        args=(",",),
        use_container_width=True,
    )


# ============================================================
# GLEICH
# ============================================================

st.button(
    "=",
    key="equals_button",
    on_click=calculate_result,
    use_container_width=True,
)


# ============================================================
# HISTORY
# ============================================================

if st.session_state.history:

    st.markdown(
        '<div class="history-title">Letzte Berechnungen</div>',
        unsafe_allow_html=True,
    )

    for item in reversed(st.session_state.history):

        st.markdown(
            f'<div class="history-item">{item}</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# CARD ENDE
# ============================================================

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">Built with Python & Streamlit 🐍</div>',
    unsafe_allow_html=True
)

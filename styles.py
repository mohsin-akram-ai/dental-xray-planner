# Page style: dark X-ray scan theme
STYLE = """
<style>
#MainMenu, footer {
    visibility: hidden;
}
.stApp {
    background:
        linear-gradient(rgba(0, 229, 255, 0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 229, 255, 0.06) 1px, transparent 1px),
        radial-gradient(circle at 20% 15%, rgba(0, 188, 212, 0.28), transparent 40%),
        radial-gradient(circle at 80% 75%, rgba(33, 150, 243, 0.22), transparent 45%),
        linear-gradient(160deg, #020b14 0%, #06202e 50%, #031018 100%);
    background-size: 40px 40px, 40px 40px, auto, auto, auto;
    background-attachment: fixed;
}
[data-testid="stHeader"] {
    background: transparent;
}
.stApp, .stApp p, .stApp label, .stApp span, .stApp h2, .stApp h3,
[data-testid="stWidgetLabel"] p,
[data-testid="stCaptionContainer"] {
    color: #e0f7fa !important;
}

/* Header banner */
.banner {
    background: linear-gradient(90deg, rgba(0, 121, 107, 0.9), rgba(38, 166, 154, 0.9));
    border: 1px solid rgba(0, 229, 255, 0.5);
    box-shadow: 0 0 25px rgba(0, 229, 255, 0.25);
    padding: 26px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 14px;
}
.banner h1 {
    margin: 0;
    font-size: 2rem;
    color: white !important;
}
.banner p {
    margin: 6px 0 0 0;
    color: #e0f2f1 !important;
}
.badges {
    text-align: center;
    margin-bottom: 22px;
}
.badge {
    display: inline-block;
    margin: 3px;
    padding: 4px 12px;
    border-radius: 999px;
    border: 1px solid rgba(0, 229, 255, 0.5);
    background: rgba(2, 20, 30, 0.7);
    color: #b2ebf2 !important;
    font-size: 0.78rem;
}

/* Step titles */
.step-title {
    margin: 26px 0 8px 0;
    padding-left: 12px;
    border-left: 4px solid #00e5ff;
    font-size: 1.1rem;
    font-weight: 600;
    color: #e0f7fa !important;
}

/* Upload box */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(2, 20, 30, 0.75);
    border: 2px dashed rgba(0, 229, 255, 0.6);
    border-radius: 14px;
    transition: all 0.25s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(4, 40, 56, 0.85);
    border-color: #00e5ff;
    box-shadow: 0 0 18px rgba(0, 229, 255, 0.45);
}
[data-testid="stFileUploaderDropzone"] * {
    color: #e0f7fa !important;
}
[data-testid="stFileUploaderFile"] {
    background: rgba(2, 20, 30, 0.6);
    border-radius: 10px;
}

/* Buttons */
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stBaseButton-secondary"],
.stButton button {
    background: linear-gradient(90deg, #00796b, #26a69a) !important;
    border: 1px solid rgba(0, 229, 255, 0.6) !important;
    border-radius: 10px !important;
    color: white !important;
    transition: all 0.25s ease;
}
[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stBaseButton-secondary"]:hover,
.stButton button:hover {
    background: linear-gradient(90deg, #26a69a, #4dd0e1) !important;
    box-shadow: 0 0 16px rgba(0, 229, 255, 0.6);
}
[data-testid="stFileUploaderDropzone"] button *,
[data-testid="stBaseButton-secondary"] *,
.stButton button * {
    color: white !important;
}

/* Dropdown list */
[data-baseweb="select"] > div {
    background: rgba(2, 20, 30, 0.75);
    border: 1px solid rgba(0, 229, 255, 0.6);
}
[data-baseweb="popover"] ul {
    background: #06202e;
}
[data-baseweb="popover"] li {
    color: #e0f7fa !important;
}
[data-baseweb="popover"] li:hover {
    background: rgba(0, 188, 212, 0.35) !important;
}

/* Result report card */
.report {
    background: rgba(2, 20, 30, 0.8);
    border: 1px solid rgba(0, 229, 255, 0.5);
    box-shadow: 0 0 22px rgba(0, 229, 255, 0.2);
    border-radius: 16px;
    padding: 22px;
    margin-top: 14px;
}
.report .label {
    color: #80deea !important;
    font-size: 0.8rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 0;
}
.report .value {
    color: #ffffff !important;
    font-size: 1.4rem;
    font-weight: 700;
    margin: 2px 0 14px 0;
}
.report .text {
    color: #e0f7fa !important;
    font-size: 1rem;
    line-height: 1.5;
    margin: 2px 0 16px 0;
}
.urgency {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.9rem;
}
.urgency-high {
    background: rgba(255, 82, 82, 0.18);
    border: 1px solid #ff5252;
    color: #ff8a80 !important;
}
.urgency-medium {
    background: rgba(255, 179, 0, 0.18);
    border: 1px solid #ffb300;
    color: #ffd54f !important;
}
.urgency-low {
    background: rgba(0, 230, 118, 0.18);
    border: 1px solid #00e676;
    color: #69f0ae !important;
}

/* Disclaimer */
.disclaimer {
    margin-top: 30px;
    padding: 14px 18px;
    border-radius: 12px;
    border: 1px solid rgba(0, 229, 255, 0.35);
    background: rgba(2, 20, 30, 0.7);
    color: #b2ebf2 !important;
    font-size: 0.85rem;
    text-align: center;
}
</style>
"""

# Header banner shown at the top of the page
HEADER = """
<div class="banner">
    <h1>🦷 Dental X-Ray Planner</h1>
    <p>AI-assisted dental screening and treatment suggestions</p>
</div>
<div class="badges">
    <span class="badge">X-ray analysis</span>
    <span class="badge">Intra-oral photo analysis</span>
    <span class="badge">Treatment suggestions</span>
</div>
"""
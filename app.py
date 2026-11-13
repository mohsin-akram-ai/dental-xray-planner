import streamlit as st
from PIL import Image

from detector import detect
from rules import get_plan
from styles import HEADER, STYLE

# This must be the first Streamlit command in the file
st.set_page_config(page_title="Dental X-Ray Planner", page_icon="🦷", layout="centered")

# Results below this confidence get a warning (0.5 means 50 percent).
LOW_CONFIDENCE = 0.5

# Used to show the most urgent findings first (0 comes first).
URGENCY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def group_detections(detections):
    """Group the detections by name.

    Example: [("caries", 0.7), ("caries", 0.5)] becomes
    {"caries": {"count": 2, "best": 0.7}}
    """
    groups = {}
    for name, score in detections:
        if name not in groups:
            groups[name] = {"count": 0, "best": 0.0}
        groups[name]["count"] += 1
        if score > groups[name]["best"]:
            groups[name]["best"] = score
    return groups


def make_card(name, count, best):
    """Build the HTML report card for one condition."""
    plan = get_plan(name)
    urgency_class = "urgency-" + plan["urgency"].lower()

    if count == 1:
        found_text = "Found 1 time"
    else:
        found_text = "Found " + str(count) + " times"

    return (
        '<div class="report">'
        '<p class="label">Detected condition</p>'
        '<p class="value">' + name.title() + "</p>"
        '<p class="text">' + found_text + ". Highest confidence: "
        + str(round(best * 100, 1)) + " %</p>"
        '<p class="label">Suggested treatment</p>'
        '<p class="text">' + plan["treatment"] + "</p>"
        '<span class="urgency ' + urgency_class + '">Urgency: ' + plan["urgency"] + "</span>"
        "</div>"
    )


# ------------------------------------------------------------------
# Page setup
# ------------------------------------------------------------------
st.markdown(STYLE, unsafe_allow_html=True)
st.markdown(HEADER, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Step 1: choose input type
# ------------------------------------------------------------------
st.markdown('<div class="step-title">Step 1: Choose input type</div>', unsafe_allow_html=True)
input_type = st.radio("Input type", ["X-ray", "Photo"], horizontal=True, label_visibility="collapsed")

if input_type == "X-ray":
    upload_label = "Upload a dental X-ray image"
else:
    upload_label = "Upload an intra-oral photo"

# ------------------------------------------------------------------
# Step 2: upload image
# ------------------------------------------------------------------
st.markdown('<div class="step-title">Step 2: Upload image</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(upload_label, type=["jpg", "jpeg", "png"])

# ------------------------------------------------------------------
# Step 3: result
# ------------------------------------------------------------------
st.markdown('<div class="step-title">Step 3: Result</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    # Run the right model (Model A for X-ray, Model B for photo)
    with st.spinner("Analyzing image..."):
        detections, annotated = detect(image, input_type)

    # Show the image with the detection boxes drawn on it
    st.image(annotated, caption="Detection result", channels="BGR", width="stretch")

    groups = group_detections(detections)

    if len(groups) == 0:
        st.warning("No clear finding. Please try a clearer image or see a dentist.")
    else:
        # Find the highest confidence among all findings
        top_confidence = 0.0
        for name in groups:
            if groups[name]["best"] > top_confidence:
                top_confidence = groups[name]["best"]

        st.caption(
            "Total findings: " + str(len(detections))
            + " | Different conditions: " + str(len(groups))
        )

        if top_confidence < LOW_CONFIDENCE:
            st.warning("Low confidence result. Please do not rely on it and ask a dentist.")

        # Sort: High urgency first, then by highest confidence
        rows = []
        for name in groups:
            plan = get_plan(name)
            order = URGENCY_ORDER[plan["urgency"]]
            rows.append((order, -groups[name]["best"], name))
        rows.sort()

        # Show one card for each condition
        for order, negative_best, name in rows:
            card = make_card(name, groups[name]["count"], groups[name]["best"])
            st.markdown(card, unsafe_allow_html=True)
else:
    st.write("Upload an image to see the result here.")

st.markdown(
    '<div class="disclaimer">This tool is for decision support only. '
    "The final diagnosis must be made by a licensed dentist.</div>",
    unsafe_allow_html=True,
)
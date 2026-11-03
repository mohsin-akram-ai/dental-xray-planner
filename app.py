import streamlit as st
from PIL import Image

from detector import detect
from styles import HEADER, STYLE

# This must be the first Streamlit command in the file
st.set_page_config(page_title="Dental X-Ray Planner", page_icon="🦷", layout="centered")

# Results below this confidence get a warning (0.5 means 50 percent).
LOW_CONFIDENCE = 0.5

# ------------------------------------------------------------------
# Treatment logic engine (rule based)
# ------------------------------------------------------------------
RULES = {
    "caries": {
        "treatment": "Filling or Root Canal Treatment (RCT) may be needed. The dentist will decide after examining the tooth.",
        "urgency": "Medium",
    },
    "periapical lesion": {
        "treatment": "Possible infection at the root tip. See a dentist soon. Root Canal Treatment (RCT) or other treatment may be needed.",
        "urgency": "High",
    },
    "impacted tooth": {
        "treatment": "A dentist or oral surgeon should check whether the tooth needs to be removed.",
        "urgency": "Medium",
    },
    "calculus": {
        "treatment": "Scaling and cleaning recommended.",
        "urgency": "Low",
    },
    "gingivitis": {
        "treatment": "Scaling, regular brushing and flossing, and an antiseptic mouthwash as advised by a dentist.",
        "urgency": "Low",
    },
    "mouth ulcer": {
        "treatment": "Keep an eye on it. If it lasts more than two weeks, see a dentist.",
        "urgency": "Low",
    },
    "discoloration": {
        "treatment": "Polishing or whitening may help. Ask a dentist which option is suitable.",
        "urgency": "Low",
    },
    "hypodontia": {
        "treatment": "Discuss orthodontic or prosthetic options with a dentist.",
        "urgency": "Medium",
    },
}

DEFAULT_RULE = {
    "treatment": "Please see a dentist for a proper examination.",
    "urgency": "Medium",
}


def get_plan(condition):
    return RULES.get(condition, DEFAULT_RULE)


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

    # Pick the detection with the highest confidence
    detected = "no clear finding"
    confidence = 0.0
    for name, score in detections:
        if score > confidence:
            detected = name
            confidence = score

    st.caption("Confidence: " + str(round(confidence * 100, 1)) + " %")

    # Warn the user when the result is weak or missing
    if detected == "no clear finding":
        st.warning("No clear finding. Please try a clearer image or see a dentist.")
    elif confidence < LOW_CONFIDENCE:
        st.warning("Low confidence result. Please do not rely on it and ask a dentist.")

    plan = get_plan(detected)
    urgency_class = "urgency-" + plan["urgency"].lower()

    report = (
        '<div class="report">'
        '<p class="label">Detected condition</p>'
        '<p class="value">' + detected.title() + "</p>"
        '<p class="label">Suggested treatment</p>'
        '<p class="text">' + plan["treatment"] + "</p>"
        '<span class="urgency ' + urgency_class + '">Urgency: ' + plan["urgency"] + "</span>"
        "</div>"
    )
    st.markdown(report, unsafe_allow_html=True)
else:
    st.write("Upload an image to see the result here.")

st.markdown(
    '<div class="disclaimer">This tool is for decision support only. '
    "The final diagnosis must be made by a licensed dentist.</div>",
    unsafe_allow_html=True,
)
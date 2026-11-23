import io
from datetime import date
from xml.sax.saxutils import escape

import numpy as np
import streamlit as st
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as PdfImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from detector import detect
from rules import get_plan, get_reliability
from styles import HEADER, STYLE

# This must be the first Streamlit command in the file
st.set_page_config(page_title="Dental X-Ray Planner", page_icon="🦷", layout="centered")

# Results below this confidence get a warning (0.5 means 50 percent).
LOW_CONFIDENCE = 0.5

# Used to show the most urgent findings first (0 comes first).
URGENCY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

# Text color for each reliability level.
RELIABILITY_COLORS = {
    "Good": "#2ecc71",
    "Fair": "#f1c40f",
    "Low": "#e74c3c",
    "Not tested": "#95a5a6",
}


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

    reliability = get_reliability(name)
    reliability_color = RELIABILITY_COLORS.get(reliability["level"], "#95a5a6")

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
        '<p class="text" style="margin-top: 14px;">'
        '<span style="color: ' + reliability_color + '; font-weight: 700;">'
        "Model reliability: " + reliability["level"] + "</span><br>"
        + reliability["note"] + "</p>"
        "</div>"
    )


def clean_text(text):
    """Make text safe for the PDF.

    The PDF font only knows basic Latin letters, so other characters
    become a question mark. The escape() call protects special
    characters such as < and &.
    """
    text = str(text).encode("latin-1", "replace").decode("latin-1")
    return escape(text)


def build_pdf(patient_name, patient_age, input_type, annotated_bgr, groups, ordered_names, min_conf):
    """Build the PDF report and return it as bytes.

    Nothing is saved on disk or in a database. The name and age are
    only printed on this report.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Dental Report",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#0f2a43")
    )
    heading_style = ParagraphStyle(
        "ReportHeading", parent=styles["Heading2"], textColor=colors.HexColor("#1aa6a6")
    )
    body_style = styles["BodyText"]
    cell_style = ParagraphStyle("Cell", parent=styles["BodyText"], fontSize=9, leading=12)
    head_style = ParagraphStyle(
        "HeadCell", parent=cell_style, textColor=colors.white, fontName="Helvetica-Bold"
    )

    story = []
    story.append(Paragraph("Dental X-Ray Planner Report", title_style))

    # Patient details: name first, then age, as requested
    if patient_name.strip():
        name_text = clean_text(patient_name.strip())
    else:
        name_text = "Not given"

    if patient_age is None:
        age_text = "Not given"
    else:
        age_text = str(int(patient_age))

    story.append(Paragraph("<b>Patient name:</b> " + name_text, body_style))
    story.append(Paragraph("<b>Age:</b> " + age_text, body_style))
    story.append(Paragraph("<b>Date:</b> " + date.today().strftime("%d %B %Y"), body_style))
    story.append(Paragraph("<b>Input type:</b> " + clean_text(input_type), body_style))
    story.append(
        Paragraph("<b>Minimum confidence used:</b> " + str(round(min_conf * 100)) + " %", body_style)
    )
    story.append(Spacer(1, 0.4 * cm))

    # The annotated image (the detector gives it in BGR order, the PDF needs RGB)
    story.append(Paragraph("Detection result", heading_style))
    rgb = np.ascontiguousarray(annotated_bgr[:, :, ::-1])
    pil_image = Image.fromarray(rgb)
    image_buffer = io.BytesIO()
    pil_image.save(image_buffer, format="JPEG", quality=90)
    image_buffer.seek(0)

    # Shrink the image so it fits on the page without changing its shape
    max_width = 17 * cm
    max_height = 9 * cm
    width, height = pil_image.size
    scale = min(max_width / width, max_height / height)
    story.append(PdfImage(image_buffer, width=width * scale, height=height * scale))
    story.append(Spacer(1, 0.4 * cm))

    # Findings table, most urgent first
    story.append(Paragraph("Findings and suggested treatment", heading_style))
    rows = [
        [
            Paragraph("Condition", head_style),
            Paragraph("Found / Best confidence", head_style),
            Paragraph("Suggested treatment", head_style),
            Paragraph("Urgency", head_style),
            Paragraph("Model reliability", head_style),
        ]
    ]
    for name in ordered_names:
        plan = get_plan(name)
        reliability = get_reliability(name)
        found = str(groups[name]["count"]) + " time(s), " + str(round(groups[name]["best"] * 100, 1)) + " %"
        rows.append(
            [
                Paragraph(clean_text(name.title()), cell_style),
                Paragraph(clean_text(found), cell_style),
                Paragraph(clean_text(plan["treatment"]), cell_style),
                Paragraph(clean_text(plan["urgency"]), cell_style),
                Paragraph(clean_text(reliability["level"]), cell_style),
            ]
        )

    table = Table(rows, colWidths=[3.2 * cm, 3.2 * cm, 5.8 * cm, 2.1 * cm, 2.7 * cm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2a43")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c4cf")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f7")]),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.6 * cm))

    story.append(
        Paragraph(
            "<i>This report is for decision support only. It is a suggestion and not a "
            "diagnosis or a prescription. Please consult a qualified dentist.</i>",
            body_style,
        )
    )

    doc.build(story)
    return buffer.getvalue()


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

# The user chooses how sure the model must be before a finding is shown.
min_conf = st.slider(
    "Minimum confidence",
    min_value=0.10,
    max_value=0.90,
    value=0.25,
    step=0.05,
    help="Lower value shows more findings (some may be wrong). Higher value shows fewer findings (some may be missed).",
)

# ------------------------------------------------------------------
# Step 3: patient details (only printed on the PDF, never saved)
# ------------------------------------------------------------------
st.markdown(
    '<div class="step-title">Step 3: Patient details (optional, printed on the PDF only)</div>',
    unsafe_allow_html=True,
)
name_column, age_column = st.columns(2)
with name_column:
    patient_name = st.text_input("Patient name", placeholder="Type the name in English letters")
with age_column:
    patient_age = st.number_input(
        "Age", min_value=0, max_value=120, value=None, step=1, placeholder="Age in years"
    )

# ------------------------------------------------------------------
# Step 4: result
# ------------------------------------------------------------------
st.markdown('<div class="step-title">Step 4: Result</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    # Streamlit runs this whole file again every time a box changes.
    # So we run the model only when the image, input type or confidence changes.
    file_key = (uploaded_file.name, uploaded_file.size, input_type, min_conf)
    if st.session_state.get("file_key") != file_key:
        with st.spinner("Analyzing image..."):
            new_detections, new_annotated = detect(image, input_type, min_conf)
        st.session_state["file_key"] = file_key
        st.session_state["detections"] = new_detections
        st.session_state["annotated"] = new_annotated

    detections = st.session_state["detections"]
    annotated = st.session_state["annotated"]

    # Show the image with the detection boxes drawn on it
    st.image(annotated, caption="Detection result", channels="BGR", width="stretch")

    groups = group_detections(detections)

    if len(groups) == 0:
        st.warning("No clear finding. Try a lower minimum confidence, a clearer image, or see a dentist.")
    else:
        # Find the highest confidence among all findings
        top_confidence = 0.0
        for name in groups:
            if groups[name]["best"] > top_confidence:
                top_confidence = groups[name]["best"]

        st.caption(
            "Minimum confidence: " + str(round(min_conf * 100)) + " %"
            + " | Total findings: " + str(len(detections))
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

        # Build the PDF report and offer it for download
        ordered_names = [row[2] for row in rows]
        pdf_bytes = build_pdf(
            patient_name, patient_age, input_type, annotated, groups, ordered_names, min_conf
        )
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name="dental_report.pdf",
            mime="application/pdf",
        )
else:
    st.write("Upload an image to see the result here.")

st.markdown(
    '<div class="disclaimer">This tool is for decision support only. '
    "The final diagnosis must be made by a licensed dentist.</div>",
    unsafe_allow_html=True,
)
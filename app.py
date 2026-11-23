import io
import re
from datetime import datetime
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

# Short advice for each overall priority level.
PRIORITY_ADVICE = {
    "High": "Please book a dental consultation as soon as possible.",
    "Medium": "Please book a dental check-up in the near future.",
    "Low": "A routine dental check-up is advised.",
}

# Which model is used for each input type (shown in the PDF).
MODEL_NAMES = {
    "X-ray": "Model A (YOLOv8 X-ray detector)",
    "Photo": "Model B (YOLOv8 photo detector)",
}

# Text color for each reliability level.
RELIABILITY_COLORS = {
    "Good": "#2ecc71",
    "Fair": "#f1c40f",
    "Low": "#e74c3c",
    "Not tested": "#95a5a6",
}

# Background color of the urgency cell in the PDF table.
PDF_URGENCY_COLORS = {
    "High": "#f8d7da",
    "Medium": "#fff3cd",
    "Low": "#d4edda",
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


def highest_urgency(names):
    """Return the most urgent level among the given condition names."""
    best = "Low"
    for name in names:
        level = get_plan(name)["urgency"]
        if URGENCY_ORDER[level] < URGENCY_ORDER[best]:
            best = level
    return best


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


def make_summary_card(total_findings, condition_count, top_urgency):
    """Build the HTML summary card shown above the condition cards."""
    urgency_class = "urgency-" + top_urgency.lower()
    return (
        '<div class="report">'
        '<p class="label">Scan summary</p>'
        '<p class="text">Total findings: ' + str(total_findings)
        + " | Different conditions: " + str(condition_count) + "</p>"
        '<span class="urgency ' + urgency_class + '">Overall priority: ' + top_urgency + "</span>"
        '<p class="text" style="margin-top: 14px;">' + PRIORITY_ADVICE[top_urgency] + "</p>"
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


def make_file_name(patient_name, created):
    """Build the download file name, for example dental_report_Ali_Khan_2026-11-23.pdf"""
    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", patient_name.strip()).strip("_")
    date_text = created.strftime("%Y-%m-%d")
    if safe_name:
        return "dental_report_" + safe_name + "_" + date_text + ".pdf"
    return "dental_report_" + date_text + ".pdf"


def draw_footer(canvas, doc):
    """Draw the footer line and the page number at the bottom of every page."""
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#b8c4cf"))
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.0 * cm, "Generated by Dental X-Ray Planner | Decision support only")
    canvas.drawRightString(A4[0] - 2 * cm, 1.0 * cm, "Page " + str(doc.page))
    canvas.restoreState()


def build_pdf(patient_name, patient_age, input_type, annotated_bgr, groups, ordered_names, min_conf, created):
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
        topMargin=1.5 * cm,
        bottomMargin=2.2 * cm,
        title="Dental Report",
    )

    navy = colors.HexColor("#0f2a43")
    teal = colors.HexColor("#1aa6a6")
    light = colors.HexColor("#eef3f7")
    line_color = colors.HexColor("#b8c4cf")

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10, leading=14)
    small_style = ParagraphStyle("Small", parent=body_style, fontSize=8.5, leading=11, textColor=colors.grey)
    heading_style = ParagraphStyle(
        "ReportHeading", parent=styles["Heading2"], textColor=teal, fontSize=13, spaceBefore=10, spaceAfter=4
    )
    banner_title = ParagraphStyle(
        "BannerTitle", parent=styles["Title"], fontSize=20, leading=24, textColor=colors.white, alignment=0
    )
    banner_sub = ParagraphStyle(
        "BannerSub", parent=body_style, textColor=colors.HexColor("#bfe9e9"), fontSize=10
    )
    cell_style = ParagraphStyle("Cell", parent=body_style, fontSize=9, leading=12)
    label_style = ParagraphStyle("Label", parent=cell_style, fontName="Helvetica-Bold", textColor=navy)
    head_style = ParagraphStyle("HeadCell", parent=cell_style, textColor=colors.white, fontName="Helvetica-Bold")

    story = []

    # Banner at the top
    banner = Table(
        [
            [Paragraph("Dental X-Ray Planner", banner_title)],
            [Paragraph("AI-assisted Dental Screening Report", banner_sub)],
        ],
        colWidths=[17 * cm],
    )
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), navy),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (0, 0), 12),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
            ]
        )
    )
    story.append(banner)
    story.append(Spacer(1, 0.4 * cm))

    # Patient details: name first, then age, then date and time
    if patient_name.strip():
        name_text = clean_text(patient_name.strip())
    else:
        name_text = "Not given"

    if patient_age is None:
        age_text = "Not given"
    else:
        age_text = str(int(patient_age))

    report_id = "DR-" + created.strftime("%Y%m%d-%H%M%S")
    info_rows = [
        [Paragraph("Patient name", label_style), Paragraph(name_text, cell_style),
         Paragraph("Report ID", label_style), Paragraph(report_id, cell_style)],
        [Paragraph("Age", label_style), Paragraph(age_text, cell_style),
         Paragraph("Date", label_style), Paragraph(created.strftime("%d %B %Y"), cell_style)],
        [Paragraph("Input type", label_style), Paragraph(clean_text(input_type), cell_style),
         Paragraph("Time", label_style), Paragraph(created.strftime("%I:%M %p"), cell_style)],
        [Paragraph("Model used", label_style), Paragraph(clean_text(MODEL_NAMES.get(input_type, input_type)), cell_style),
         Paragraph("Minimum confidence", label_style), Paragraph(str(round(min_conf * 100)) + " %", cell_style)],
    ]
    info_table = Table(info_rows, colWidths=[3.0 * cm, 5.5 * cm, 3.6 * cm, 4.9 * cm])
    info_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, line_color),
                ("BACKGROUND", (0, 0), (0, -1), light),
                ("BACKGROUND", (2, 0), (2, -1), light),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(info_table)

    # Summary
    top_urgency = highest_urgency(ordered_names)
    total_findings = 0
    for name in ordered_names:
        total_findings += groups[name]["count"]

    story.append(Paragraph("Summary", heading_style))
    story.append(
        Paragraph(
            "<b>Total findings:</b> " + str(total_findings)
            + " in " + str(len(ordered_names)) + " condition(s). "
            + "<b>Overall priority:</b> " + top_urgency + ". "
            + clean_text(PRIORITY_ADVICE[top_urgency]),
            body_style,
        )
    )

    # The annotated image (the detector gives it in BGR order, the PDF needs RGB)
    story.append(Paragraph("Detection result", heading_style))
    rgb = np.ascontiguousarray(annotated_bgr[:, :, ::-1])
    pil_image = Image.fromarray(rgb)
    image_buffer = io.BytesIO()
    pil_image.save(image_buffer, format="JPEG", quality=90)
    image_buffer.seek(0)

    # Shrink the image so it fits on the page without changing its shape
    max_width = 17 * cm
    max_height = 8.5 * cm
    width, height = pil_image.size
    scale = min(max_width / width, max_height / height)
    story.append(PdfImage(image_buffer, width=width * scale, height=height * scale))

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
    urgency_styles = []
    for index, name in enumerate(ordered_names, start=1):
        plan = get_plan(name)
        reliability = get_reliability(name)
        found = str(groups[name]["count"]) + " time(s), " + str(round(groups[name]["best"] * 100, 1)) + " %"
        rows.append(
            [
                Paragraph("<b>" + clean_text(name.title()) + "</b>", cell_style),
                Paragraph(clean_text(found), cell_style),
                Paragraph(clean_text(plan["treatment"]), cell_style),
                Paragraph("<b>" + clean_text(plan["urgency"]) + "</b>", cell_style),
                Paragraph(clean_text(reliability["level"]), cell_style),
            ]
        )
        cell_color = PDF_URGENCY_COLORS.get(plan["urgency"], "#ffffff")
        urgency_styles.append(("BACKGROUND", (3, index), (3, index), colors.HexColor(cell_color)))

    table = Table(rows, colWidths=[3.2 * cm, 3.2 * cm, 5.8 * cm, 2.1 * cm, 2.7 * cm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("GRID", (0, 0), (-1, -1), 0.4, line_color),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
            + urgency_styles
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.2 * cm))
    story.append(
        Paragraph(
            "Model reliability shows how well the model did on test images for that condition. "
            "A Low level means the result needs extra care.",
            small_style,
        )
    )

    # Recommended next steps
    story.append(Paragraph("Recommended next steps", heading_style))
    story.append(Paragraph("1. Show this report to a licensed dentist.", body_style))
    story.append(
        Paragraph("2. Do not start any treatment or medicine only because of this report.", body_style)
    )
    story.append(
        Paragraph("3. If you have pain, swelling or fever, see a dentist without delay.", body_style)
    )
    story.append(Spacer(1, 0.4 * cm))

    # Disclaimer box
    disclaimer = Table(
        [
            [
                Paragraph(
                    "<b>Disclaimer:</b> This report is made by a computer program for decision support only. "
                    "It is a suggestion and not a diagnosis or a prescription. "
                    "The final diagnosis and treatment must be decided by a licensed dentist.",
                    cell_style,
                )
            ]
        ],
        colWidths=[17 * cm],
    )
    disclaimer.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, teal),
                ("BACKGROUND", (0, 0), (-1, -1), light),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(disclaimer)

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
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

        if top_confidence < LOW_CONFIDENCE:
            st.warning("Low confidence result. Please do not rely on it and ask a dentist.")

        # Sort: High urgency first, then by highest confidence
        rows = []
        for name in groups:
            plan = get_plan(name)
            order = URGENCY_ORDER[plan["urgency"]]
            rows.append((order, -groups[name]["best"], name))
        rows.sort()
        ordered_names = [row[2] for row in rows]

        # Summary card first, then one card for each condition
        top_urgency = highest_urgency(ordered_names)
        st.markdown(
            make_summary_card(len(detections), len(groups), top_urgency),
            unsafe_allow_html=True,
        )
        for order, negative_best, name in rows:
            card = make_card(name, groups[name]["count"], groups[name]["best"])
            st.markdown(card, unsafe_allow_html=True)

        # Build the PDF report and offer it for download
        created = datetime.now()
        pdf_bytes = build_pdf(
            patient_name, patient_age, input_type, annotated, groups, ordered_names, min_conf, created
        )
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=make_file_name(patient_name, created),
            mime="application/pdf",
        )
else:
    st.write("Upload an image to see the result here.")

st.markdown(
    '<div class="disclaimer">This tool is for decision support only. '
    "The final diagnosis must be made by a licensed dentist.</div>",
    unsafe_allow_html=True,
)
"""
Renders metric_glossary.py into a clean, iPad-readable PDF — the same
explanation + relevance text shown in viewer_app.py's Glossary tab, so
this file never drifts from what the app shows.

Run with: python generate_glossary_pdf.py
Writes: METRIC_GLOSSARY.pdf (nfl-analytics root)
"""
from datetime import date
from fpdf import FPDF, XPos, YPos
from metric_glossary import METRIC_META, FAMILIES

MARGIN = 18

# Core PDF fonts only support latin-1 — swap the em dashes metric_glossary.py
# uses for plain ASCII rather than pulling in a Unicode TTF for one character.
_REPLACEMENTS = {"—": " - ", "–": "-", "‘": "'", "’": "'", "“": '"', "”": '"', "…": "..."}


def clean(s):
    for src, dst in _REPLACEMENTS.items():
        s = s.replace(src, dst)
    return s.encode("latin-1", "replace").decode("latin-1")


class GlossaryPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(90, 90, 90)
        self.cell(0, 8, "NFL Metric Glossary", align="L")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def main():
    pdf = GlossaryPDF(format="A4")
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.set_auto_page_break(auto=True, margin=20)

    # ---- cover ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(20, 30, 30)
    pdf.ln(40)
    pdf.multi_cell(0, 12, "NFL Metric Glossary", align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(90, 100, 98)
    pdf.ln(4)
    pdf.multi_cell(0, 8, "Every team-level metric: what it is, in plain language, and why it's tracked.", align="C")
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 7, clean(f"Generated {date.today().isoformat()} — source: metric_glossary.py"), align="C")

    # ---- table of contents ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(20, 30, 30)
    pdf.cell(0, 10, "Contents", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(50, 60, 58)
    for fam in FAMILIES:
        count = len([m for m in METRIC_META if m[1] == fam])
        pdf.cell(0, 8, clean(f"{fam}  ({count} metrics)"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ---- one section per family ----
    for fam in FAMILIES:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 17)
        pdf.set_text_color(20, 60, 70)
        pdf.cell(0, 10, clean(fam), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_draw_color(20, 60, 70)
        pdf.set_line_width(0.6)
        pdf.line(MARGIN, pdf.get_y(), 210 - MARGIN, pdf.get_y())
        pdf.ln(6)

        for key, family, label, simple, explanation, relevance, source in METRIC_META:
            if family != fam:
                continue
            if pdf.get_y() > 250:
                pdf.add_page()

            pdf.set_font("Helvetica", "B", 12.5)
            pdf.set_text_color(20, 30, 30)
            pdf.multi_cell(0, 7, clean(label))

            pdf.set_font("Helvetica", "BI", 10)
            pdf.set_text_color(90, 100, 98)
            pdf.set_x(MARGIN)
            pdf.multi_cell(0, 6, clean(simple))

            pdf.set_font("Helvetica", "", 10.5)
            pdf.set_text_color(60, 68, 66)
            pdf.set_x(MARGIN)
            pdf.multi_cell(0, 6, clean(f"What it is: {explanation}"))

            pdf.set_font("Helvetica", "I", 10.5)
            pdf.set_text_color(58, 107, 120)
            pdf.set_x(MARGIN)
            pdf.multi_cell(0, 6, clean(f"Why it matters: {relevance}"))

            pdf.ln(4)

    pdf.output("METRIC_GLOSSARY.pdf")
    print(f"Wrote METRIC_GLOSSARY.pdf — {len(METRIC_META)} metrics across {len(FAMILIES)} families")


if __name__ == "__main__":
    main()

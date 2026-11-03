"""
Generates the SkyNova Airlines knowledge base (PDFs) + a CSV for Code Interpreter.

Usage:
    python data_generation/generate_pdfs.py
Outputs:
    data/pdfs/*.pdf
    data/csv/skynova_operational_performance_q3_2025_2026.csv
"""
import csv
import os
from collections import defaultdict

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

import skynova_data as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(ROOT, "data", "pdfs")
CSV_DIR = os.path.join(ROOT, "data", "csv")

NAVY = colors.HexColor("#0B2545")
TEAL = colors.HexColor("#13A89E")
LIGHT = colors.HexColor("#EEF4F8")
GREY = colors.HexColor("#5A6B7B")

ss = getSampleStyleSheet()
S = {
    "title": ParagraphStyle("t", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=22, textColor=NAVY, spaceAfter=6, leading=27),
    "subtitle": ParagraphStyle("st", parent=ss["Normal"], fontSize=11, textColor=GREY, alignment=TA_CENTER, spaceAfter=14),
    "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=15, textColor=NAVY, spaceBefore=12, spaceAfter=6),
    "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12, textColor=TEAL, spaceBefore=9, spaceAfter=4),
    "p": ParagraphStyle("p", parent=ss["BodyText"], fontSize=9.6, leading=13.4, spaceAfter=5),
    "cell": ParagraphStyle("c", parent=ss["BodyText"], fontSize=8.2, leading=10.2),
    "cellb": ParagraphStyle("cb", parent=ss["BodyText"], fontSize=8.2, leading=10.2, fontName="Helvetica-Bold", textColor=colors.white),
    "note": ParagraphStyle("n", parent=ss["BodyText"], fontSize=8.4, leading=11, textColor=GREY, spaceAfter=6),
    "box": ParagraphStyle("bx", parent=ss["BodyText"], fontSize=9.4, leading=13, textColor=NAVY),
}


# ------------------------------------------------------------------ helpers
def P(t):
    return Paragraph(t, S["p"])


def H1(t):
    return Paragraph(t, S["h1"])


def H2(t):
    return Paragraph(t, S["h2"])


def NOTE(t):
    return Paragraph(t, S["note"])


def BUL(items):
    return ListFlowable([ListItem(Paragraph(i, S["p"]), leftIndent=12, value="bullet") for i in items],
                        bulletType="bullet", start="•", leftIndent=12, bulletFontSize=8)


def BOX(t):
    tbl = Table([[Paragraph(t, S["box"])]], colWidths=[17 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 0.8, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return tbl


def TBL(rows, widths=None, font=8.2, zebra=True):
    data = [[Paragraph(str(c), S["cellb"]) for c in rows[0]]]
    cell = ParagraphStyle("cx", parent=S["cell"], fontSize=font, leading=font + 2)
    for r in rows[1:]:
        data.append([Paragraph(str(c), cell) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#C9D3DD")),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    if zebra:
        for i in range(2, len(data), 2):
            st.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(st))
    return t


def SP(h=6):
    return Spacer(1, h)


def build(filename, title, doc_code, version, effective, story):
    os.makedirs(PDF_DIR, exist_ok=True)
    path = os.path.join(PDF_DIR, filename)

    def on_page(canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setFillColor(NAVY)
        canvas.rect(0, h - 1.25 * cm, w, 1.25 * cm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, h - 1.4 * cm, w, 0.15 * cm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(1.8 * cm, h - 0.85 * cm, "SKYNOVA AIRLINES")
        canvas.setFont("Helvetica", 8.5)
        canvas.drawRightString(w - 1.8 * cm, h - 0.85 * cm, f"{title}  |  {doc_code}  v{version}")
        canvas.setFillColor(GREY)
        canvas.setFont("Helvetica", 7.2)
        canvas.drawString(1.8 * cm, 1.0 * cm, f"Effective {effective}. FICTIONAL document created for an educational AI challenge. "
                                              "SkyNova Airlines is not a real company.")
        canvas.drawRightString(w - 1.8 * cm, 1.0 * cm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            topMargin=2.1 * cm, bottomMargin=1.8 * cm, title=f"SkyNova Airlines - {title}",
                            author="SkyNova Airlines Customer Experience", subject=title)
    head = [Paragraph(f"SkyNova Airlines<br/>{title}", S["title"]),
            Paragraph(f"Document {doc_code} &nbsp;|&nbsp; Version {version} &nbsp;|&nbsp; Effective {effective}", S["subtitle"])]
    doc.build(head + story, onFirstPage=on_page, onLaterPages=on_page)
    print("  ✓", filename)


def about_box():
    return BOX("<b>About SkyNova Airlines.</b> SkyNova Airlines (IATA code NV) is a full-service carrier founded in 2009 "
               f"and headquartered in Madrid, Spain. Its main hub is {D.HUB}, with a secondary base at Barcelona-El Prat (BCN). "
               "SkyNova operates a fleet of 44 aircraft on 26 routes to 22 destinations in Spain, Europe, North America and Latin America, "
               "and carried 7.9 million passengers in 2025. Our promise: <i>\"Every journey, cared for.\"</i>")


# ================================================================== 01 FARES & BAGGAGE
def doc_fares_baggage():
    s = [about_box(), SP(8)]
    s += [H1("1. Purpose and scope"),
          P("This document describes SkyNova fare families, the conditions attached to each fare (changes, refunds, seat selection, "
            "miles earned) and the baggage allowance and fees that apply to all flights operated by SkyNova Airlines (flight numbers NV). "
            "Flights operated by partner airlines may apply different rules; customers should check the operating carrier shown in "
            "their booking confirmation."),
          P("Route types used throughout this document: <b>Domestic</b> (flights within Spain, including the Balearic and Canary Islands), "
            "<b>Europe</b> (flights between Spain and other European countries, and between European cities) and <b>Long-haul</b> "
            "(flights to North America and Latin America).")]

    s += [H1("2. Fare families"),
          P("SkyNova offers three Economy fare families (Basic, Classic and Flex), a Premium Economy cabin on Airbus A350-900 long-haul "
            "flights, and Business class on all jet aircraft. The table below summarises the main conditions.")]
    s.append(TBL([
        ["Condition", "Economy Basic", "Economy Classic", "Economy Flex", "Premium Economy", "Business"],
        ["Personal item (40x30x15 cm)", "Included", "Included", "Included", "Included", "Included"],
        ["Cabin bag (55x40x23 cm)", "Not included (add from €18)", "1 x 10 kg", "1 x 10 kg", "1 x 10 kg", "2 x 14 kg total"],
        ["Checked baggage", "Not included", "1 x 23 kg", "2 x 23 kg", "2 x 23 kg", "2 x 32 kg"],
        ["Date / flight changes", "Not permitted", "€60 Domestic / Europe; €150 Long-haul + fare difference",
         "Free (fare difference only)", "1st change free, then €100", "Free (fare difference only)"],
        ["Refund before departure", "Not refundable (taxes refunded on request)", "Not refundable; travel voucher for 80% of fare",
         "Fully refundable", "Refundable, fee €200", "Fully refundable"],
        ["No-show", "Ticket lost", "Ticket lost; taxes refunded", "Refund minus €50", "Refund minus €200", "Fully refundable"],
        ["Seat selection", "Paid (from €9)", "Free standard seat from 7 days before departure", "Free (incl. extra legroom)", "Free", "Free"],
        ["Horizon miles multiplier", "0.25 x km", "1.0 x km", "1.5 x km", "1.75 x km", "2.5 x km"],
        ["Priority boarding", "No", "No", "Yes", "Yes", "Yes (Group 1)"],
        ["Lounge access", "No", "No", "No", "No (bookable €35)", "Yes"],
        ["Same-day flight change (earlier flight)", "No", "€40 Domestic / Europe", "Free", "Free", "Free"],
    ], widths=[3.4 * cm, 2.6 * cm, 3.0 * cm, 2.6 * cm, 2.6 * cm, 2.8 * cm], font=7.6))
    s += [NOTE("Change and refund fees are per passenger and per direction. The fare difference is always payable when the new fare is "
               "higher. When the new fare is lower, the difference is not refunded except on Flex and Business fares, where it is "
               "returned as a travel voucher valid for 12 months.")]

    s += [H2("2.1 The 24-hour free cancellation window"),
          P("Every SkyNova booking made directly on skynova.example, the SkyNova app or the Contact Centre can be cancelled free of charge "
            "within 24 hours of purchase, provided the booking was made at least 7 days before departure. The full amount is "
            "refunded to the original form of payment. This rule applies to all fare families, including Basic."),
          H2("2.2 Name corrections and name changes"),
          P("Minor spelling corrections of up to 3 characters per name are free of charge. Tickets are personal and non-transferable, "
            "so a full name change is not permitted. If a passenger has two surnames and only one was entered, adding the second "
            "surname is treated as a free correction. Name corrections for long-haul flights to the United States must be completed "
            "at least 72 hours before departure because of ESTA / APIS requirements."),
          H2("2.3 Travel vouchers"),
          P("Travel vouchers issued by SkyNova are valid for 12 months from the date of issue, can be used for any passenger on the "
            "same booking, can be combined (up to 3 vouchers per booking) and cannot be exchanged for cash, except vouchers issued "
            "as an alternative to monetary compensation under the Passenger Care Policy (document CX-02), which may be converted to "
            "cash at any time during their validity.")]

    s += [H1("3. Cabin baggage"),
          P("All passengers may bring one personal item (handbag, laptop bag or small backpack) of maximum 40 x 30 x 15 cm that must fit "
            "under the seat in front. Cabin bags must not exceed 55 x 40 x 23 cm including wheels and handles, and 10 kg (Economy and "
            "Premium Economy) or 14 kg combined for two pieces (Business)."),
          BUL(["On ATR 72-600 aircraft (SkyNova Connect, routes MAD-BIO and MAD-SCQ) overhead bins are smaller: cabin bags are "
               "collected free of charge at the aircraft door ('valet bag') and returned at the aircraft door on arrival.",
               "When overhead space is full, cabin bags may be checked in free of charge at the gate. Customers must remove "
               "lithium batteries, medicines and valuables first.",
               "Duty-free purchases in a sealed bag are allowed in addition to the cabin allowance.",
               "Cabin bags that exceed the size or weight limit at the gate are charged the gate fee shown in section 5."])]

    s += [H1("4. Checked baggage allowance"),
          P("Each checked bag may weigh up to 23 kg (Economy and Premium Economy) or 32 kg (Business) and must not exceed 158 cm in total "
            "dimensions (length + width + height). No single bag may weigh more than 32 kg for health and safety reasons; heavier items "
            "must be sent as cargo. Horizon tier members receive additional allowance as described in the Horizon Loyalty Program "
            "guide (document CX-04): Silver +1 bag of 23 kg, Gold and Platinum +1 bag of 32 kg."),
          P("Infants under 2 years have an allowance of one checked bag of 10 kg plus one fully collapsible stroller and one car seat, "
            "free of charge. Children from 2 years have the same allowance as adults on the same fare.")]

    s += [H1("5. Baggage fees"),
          P("Prices are per bag and per direction. Purchasing online (skynova.example or the app) up to 4 hours before departure is "
            "always cheaper than paying at the airport.")]
    s.append(TBL([
        ["Item", "Domestic online", "Domestic airport", "Europe online", "Europe airport", "Long-haul online", "Long-haul airport"],
        ["Cabin bag added to Basic fare", "€18", "€35 (at gate €45)", "€22", "€40 (at gate €50)", "n/a", "n/a"],
        ["1st extra checked bag (23 kg)", "€25", "€40", "€35", "€55", "€70", "€100"],
        ["2nd extra checked bag (23 kg)", "€40", "€60", "€50", "€75", "€100", "€140"],
        ["3rd and following bags (each)", "€70", "€90", "€90", "€110", "€160", "€200"],
        ["Overweight 23.1 - 32 kg", "€40", "€50", "€50", "€75", "€75", "€100"],
        ["Oversize 158 - 203 cm", "€50", "€60", "€60", "€80", "€100", "€150"],
    ], widths=[3.9 * cm, 2.15 * cm, 2.35 * cm, 2.15 * cm, 2.35 * cm, 2.15 * cm, 2.35 * cm], font=7.8))
    s += [NOTE("Example: a passenger on an Economy Classic fare MAD-JFK (one 23 kg bag included) who wants to check a second bag of 27 kg "
               "pays €70 (1st extra bag, online) + €75 (overweight, online) = €145 per direction if purchased online, or "
               "€100 + €100 = €200 at the airport.")]

    s += [H1("6. Check-in and boarding deadlines"),
          TBL([["Step", "Domestic & Europe", "Long-haul"],
               ["Online check-in opens", "48 hours before departure", "48 hours before departure"],
               ["Online check-in closes", "1 hour before departure", "2 hours before departure"],
               ["Airport bag drop / desk closes", "45 minutes before departure", "60 minutes before departure"],
               ["Boarding gate opens", "40 minutes before departure", "60 minutes before departure"],
               ["Boarding gate closes", "20 minutes before departure", "30 minutes before departure"],
               ], widths=[6 * cm, 5.5 * cm, 5.5 * cm]),
          P("Passengers who do not present themselves at the gate before closure are considered no-shows and their seat may be "
            "re-assigned. If a passenger misses the outbound flight, return flights on the same booking are NOT cancelled "
            "automatically provided the passenger contacts SkyNova before the departure of the return flight.")]

    s += [H1("7. Items not accepted in checked baggage"),
          BUL(["Spare lithium batteries and power banks (must be carried in the cabin; maximum 2 power banks per passenger, up to "
               "100 Wh each; 100-160 Wh require prior approval; above 160 Wh are forbidden).",
               "E-cigarettes and vapes (cabin only, use on board is forbidden).",
               "Valuables such as jewellery, cash, laptops, cameras, keys and medicines: SkyNova recommends carrying them in the cabin; "
               "liability for these items in checked baggage is limited as described in document CX-02.",
               "Flammable liquids, gas cylinders, fireworks and other dangerous goods are forbidden in both cabin and hold."])]

    s += [H1("8. Damaged, delayed or lost baggage"),
          P("Customers should report any baggage irregularity at the SkyNova Baggage Services desk in the arrival hall before leaving "
            "the airport and obtain a Property Irregularity Report (PIR) reference, format <b>MADNV12345</b>. Deadlines for written claims "
            "and interim expense allowances are described in the Passenger Care and Compensation Policy (document CX-02, section 7).")]
    build("SkyNova_01_Fares_and_Baggage_Policy.pdf", "Fares and Baggage Policy", "CX-01", "4.2", "1 March 2026", s)


# ================================================================== 02 CARE & COMPENSATION
def doc_compensation():
    s = [about_box(), SP(8)]
    s += [H1("1. Our commitment"),
          P("At SkyNova we know that a disrupted journey affects plans, family and work. This policy explains what we will do for "
            "customers when a flight is delayed, cancelled or overbooked, or when baggage is delayed, damaged or lost. It applies to "
            "all flights operated by SkyNova (NV flight numbers). As a European Union carrier, SkyNova applies Regulation (EC) No "
            "261/2004 on <b>all</b> its flights, including flights departing from outside the EU. In addition, SkyNova offers voluntary "
            "goodwill gestures that go beyond the legal minimum (the <b>SkyNova Care Promise</b>, section 6)."),
          BOX("<b>Golden rule for our agents:</b> first make sure the customer can reach their destination (rebooking and care), "
              "then explain compensation. Always give the customer a case reference and a clear next step.")]

    s += [H1("2. Distance bands"),
          P("Compensation amounts depend on the great-circle distance of the flight. The table below shows the band for every SkyNova route.")]
    rows = [["Route", "Flight", "Distance (km)", "Band", "Compensation per passenger"]]
    for r in D.ROUTES:
        b = D.eu261_band(r["km"])
        band = {250: "A (up to 1,500 km)", 400: "B (1,500 - 3,500 km)", 600: "C (more than 3,500 km)"}[b]
        rows.append([f'{r["route"]} ({r["city"]})', r["flight"], f'{r["km"]:,}', band, f"€{b}"])
    s.append(TBL(rows, widths=[5.6 * cm, 1.6 * cm, 2.4 * cm, 4.0 * cm, 3.4 * cm], font=7.8))
    s.append(NOTE("Note: MAD-TFN (Tenerife North, 1,760 km) is a domestic flight but falls in band B because it is longer than 1,500 km. "
                  "MAD-MUC (1,493 km) and MAD-AMS (1,480 km) remain in band A."))

    s += [H1("3. Flight delays"),
          H2("3.1 Right to care (meals, refreshments, hotel)"),
          P("When a flight is expected to depart later than the scheduled time by at least the thresholds below, SkyNova provides meals "
            "and refreshments, two free communications (phone call or email) and, if an overnight stay becomes necessary, hotel "
            "accommodation and transport between the airport and the hotel."),
          TBL([["Band", "Departure delay that triggers care", "Meal voucher (short wait)", "Meal voucher (more than 4 h wait)"],
               ["A (up to 1,500 km)", "2 hours or more", "€12", "€25"],
               ["B (1,500 - 3,500 km)", "3 hours or more", "€15", "€25"],
               ["C (more than 3,500 km)", "4 hours or more", "€20", "€35"]],
              widths=[4 * cm, 5 * cm, 4 * cm, 4 * cm]),
          P("Vouchers are issued automatically in the SkyNova app and by email, and can also be collected at the transfer desk. They can "
            "be used in most airport restaurants at MAD and BCN. At other airports, customers who were not given vouchers may buy "
            "reasonable meals and claim reimbursement (see section 8)."),
          H2("3.2 Compensation for long delays"),
          P("Customers whose flight <b>arrives</b> at its final destination <b>3 hours or more</b> after the scheduled arrival time are entitled "
            "to compensation according to the distance band (€250 / €400 / €600), unless the delay was caused by extraordinary "
            "circumstances (section 5). For band C flights with an arrival delay of between 3 and 4 hours the compensation is reduced "
            "by 50% (€300). The arrival time is the moment at which at least one aircraft door is opened."),
          H2("3.3 Delays of 5 hours or more"),
          P("If a delay reaches 5 hours, customers who decide not to travel may obtain a full refund of the unused part of the ticket "
            "(and of already-used parts if the journey no longer serves any purpose), together with a free return flight to the "
            "point of origin when relevant.")]

    s += [H1("4. Cancellations and denied boarding"),
          H2("4.1 Cancellations"),
          P("When SkyNova cancels a flight, customers may choose between (a) a full refund within 7 days, (b) rerouting to the final "
            "destination at the earliest opportunity, including on partner airlines or by train (Renfe AVE for Spanish domestic routes "
            "where available), or (c) rerouting at a later date of their choice, subject to seat availability. Care is provided while "
            "waiting for the rerouted flight."),
          TBL([["When the customer was informed", "Compensation is NOT payable if the alternative flight..."],
               ["14 days or more before departure", "Compensation never payable"],
               ["Between 7 and 13 days before departure", "departs no more than 2 hours earlier AND arrives less than 4 hours later than originally scheduled"],
               ["Less than 7 days before departure", "departs no more than 1 hour earlier AND arrives less than 2 hours later than originally scheduled"]],
              widths=[6 * cm, 11 * cm]),
          H2("4.2 Overbooking and denied boarding"),
          P("SkyNova first asks for volunteers. Volunteers receive a travel voucher of €300 (band A), €450 (band B) or €700 (band C), "
            "plus a confirmed seat on the next available flight, meals and, if needed, a hotel. If there are not enough volunteers, "
            "customers denied boarding against their will receive the full compensation for their band immediately at the airport "
            "(€250 / €400 / €600), reduced by 50% if the alternative flight arrives within 2 hours (band A), 3 hours (band B) or "
            "4 hours (band C) of the original schedule. Priority to keep their seat is given to unaccompanied minors, passengers "
            "with reduced mobility and their companions, and Horizon Platinum members."),
          H2("4.3 Downgrading"),
          P("If a customer is placed in a lower cabin than the one booked, SkyNova refunds 30% (band A), 50% (band B) or 75% (band C) "
            "of the ticket price for that flight within 7 days, plus the difference in any ancillary products not received.")]

    s += [H1("5. Extraordinary circumstances"),
          P("Compensation (sections 3.2, 4.1) is not payable when the disruption was caused by extraordinary circumstances that could not "
            "have been avoided even if all reasonable measures had been taken. Right to care, refund and rerouting <b>always</b> apply."),
          TBL([["Usually extraordinary (no compensation)", "NOT extraordinary (compensation payable)"],
               ["Air traffic control restrictions and ATC strikes", "Technical faults discovered during routine maintenance"],
               ["Severe weather incompatible with safe operation", "Strikes by SkyNova's own staff (pilots, cabin crew)"],
               ["Bird strike, lightning strike", "Crew shortages or sickness"],
               ["Security risks, airport closures, political instability", "Late inbound aircraft caused by a non-extraordinary event"],
               ["Medical emergencies and unruly passengers forcing a diversion", "Ground handling delays at the hub"]],
              widths=[8.5 * cm, 8.5 * cm]),
          P("A delay that is 'reactionary' (caused by the late arrival of the previous flight on the same aircraft) follows the cause of "
            "the original delay. Our agents can see the official delay code of any NV flight in the operations system and must share "
            "the reason with the customer in plain language.")]

    s += [H1("6. SkyNova Care Promise (voluntary, beyond EU law)"),
          P("For disruptions <b>within SkyNova's control</b>, we offer the following goodwill gestures automatically, without the customer "
            "having to claim. They do not reduce any legal compensation."),
          TBL([["Situation", "Domestic & Europe", "Long-haul"],
               ["Arrival delay 60 - 119 minutes", "1,000 Horizon miles", "2,000 Horizon miles"],
               ["Arrival delay 120 - 179 minutes", "€25 travel voucher", "€60 travel voucher"],
               ["Cancellation with rebooking on a flight the next day", "€50 travel voucher + free lounge access", "€100 travel voucher + free lounge access"],
               ["Seat not available as purchased (paid seat)", "Seat fee refunded + 500 miles", "Seat fee refunded + 1,000 miles"],
               ["Wi-Fi purchased but not working", "Refund + 300 miles", "Refund + 500 miles"]],
              widths=[7 * cm, 5 * cm, 5 * cm]),
          P("Customers may choose to receive their legal compensation as a SkyNova travel voucher worth <b>120%</b> of the cash amount (for "
            "example €480 instead of €400). This is always optional and the voucher may be converted to cash at any time during its "
            "12-month validity.")]

    s += [H1("7. Baggage irregularities"),
          TBL([["Situation", "Deadline to report / claim", "What SkyNova offers"],
               ["Delayed bag", "PIR at airport; written claim within 21 days of receiving the bag",
                "Interim expenses up to €50 per day for a maximum of 5 days (€250) with receipts. Gold and Platinum: €75 per day. "
                "Free delivery of the bag to the customer's address."],
               ["Damaged bag", "PIR at airport, or written claim within 7 days",
                "Repair through our partner network, or replacement value considering depreciation (10% per year of age, maximum 60%)."],
               ["Lost bag", "Bag declared lost after 21 days of search",
                "Compensation for proven value up to the Montreal Convention limit of 1,519 SDR (approximately €1,850) per passenger."],
               ["Pilfered contents", "Written claim within 7 days", "Assessed with receipts; valuables in checked bags not covered (see CX-01, s.7)."]],
              widths=[3 * cm, 5 * cm, 9 * cm]),
          P("Interim expenses cover essential items such as toiletries, underwear and basic clothing. For sports equipment or "
            "a delayed stroller, SkyNova covers reasonable rental costs instead of the daily allowance.")]

    s += [H1("8. How to claim and reimbursement limits"),
          BUL(["Online form: skynova.example/claims (fastest). Customers need the booking reference (6 characters, e.g. <b>NV7K2Q</b>), "
               "flight number and date, and receipts.",
               "SkyNova acknowledges claims within 48 hours and gives a final answer within <b>30 days</b>. Approved payments are made "
               "within <b>14 days</b> to the original form of payment or by bank transfer.",
               "Claims can be submitted up to <b>5 years</b> after the flight (Spanish limitation period).",
               "Customers do not need to use a claims agency; SkyNova never charges a fee for processing compensation."]),
          TBL([["Expense paid by the customer", "Reimbursement limit"],
               ["Hotel (per room, per night)", "€120 in Europe; €150 in Madrid, Barcelona, London, Paris; €180 in New York and Boston"],
               ["Meals and refreshments (per person, per day)", "€30 in Europe; €45 on long-haul"],
               ["Taxi / transport airport-hotel", "€50 per journey (receipt required)"],
               ["Phone calls", "€10"],
               ["Alternative transport arranged by the customer", "Only if pre-approved by the SkyNova Contact Centre"]],
              widths=[7 * cm, 10 * cm]),
          H1("9. Escalation"),
          P("If a customer is not satisfied with our answer, they can ask for a review by the SkyNova Customer Relations Office "
            "(answer within 15 days). After that, customers can contact the national enforcement body; for flights departing Spain "
            "this is AESA (Spanish Aviation Safety and Security Agency), or use the alternative dispute resolution entity to which "
            "SkyNova adheres.")]
    build("SkyNova_02_Passenger_Care_and_Compensation_Policy.pdf", "Passenger Care and Compensation Policy", "CX-02", "3.1",
          "1 March 2026", s)


# ================================================================== 03 SPECIAL ASSISTANCE
def doc_special():
    s = [about_box(), SP(8)]
    s += [H1("1. Assistance for passengers with reduced mobility (PRM)"),
          P("Assistance at the airport and on board is <b>free of charge</b> on all SkyNova flights. To guarantee the best service, "
            "customers should request it at least <b>48 hours before departure</b> through Manage Booking, the app or the Contact Centre. "
            "Requests made later will be handled on a best-effort basis."),
          TBL([["Code", "Description", "Typical support"],
               ["WCHR", "Can walk short distances and climb stairs, needs help for long distances", "Wheelchair to the aircraft door"],
               ["WCHS", "Cannot climb stairs but can move inside the cabin", "Wheelchair + lift / ambulift where needed"],
               ["WCHC", "Completely immobile, needs help to reach the seat", "Aisle chair on board; seat close to the toilet where possible"],
               ["BLND / DEAF", "Visually or hearing impaired passengers", "Escort, personalised safety briefing, written announcements"],
               ["DPNA", "Intellectual or developmental disability", "Escort, quiet boarding, family seating"]],
              widths=[2.3 * cm, 8.2 * cm, 6.5 * cm]),
          BUL(["Up to 2 mobility devices (wheelchair, scooter) are carried free of charge in addition to the baggage allowance.",
               "Battery-powered wheelchairs: lithium-ion batteries up to 300 Wh (or two of up to 160 Wh) must be declared 48 hours in advance.",
               "Recognised assistance dogs travel free of charge in the cabin on all routes, including long-haul.",
               "If a customer needs a companion for safety reasons, the companion's seat is offered with a 50% discount on the fare (taxes excluded).",
               "Approved portable oxygen concentrators (POC) may be used on board; the customer must bring batteries for 150% of the flight duration."])]

    s += [H1("2. Travelling with pets"),
          P("Dogs and cats are accepted in the cabin or in the hold (AVIH) on SkyNova flights, with the following conditions. "
            "Pets must be booked in advance; a maximum of 2 pets are accepted in the cabin per flight on A320neo/A321neo, 3 on A350-900 "
            "and A321XLR, and none on ATR 72-600 aircraft."),
          TBL([["", "Domestic", "Europe", "Long-haul"],
               ["In cabin (pet + carrier up to 8 kg, carrier max 45 x 35 x 25 cm)", "€50", "€70", "€150 (A350 / A321XLR only)"],
               ["In hold (pet + crate up to 45 kg)", "€80", "€120", "€250"],
               ["Booking deadline", "48 h", "48 h", "7 days (health certificate required)"]],
              widths=[7 * cm, 2.7 * cm, 2.7 * cm, 4.6 * cm]),
          BUL(["Snub-nosed (brachycephalic) dogs and cats such as Bulldogs, Pugs, Boxers and Persian cats are NOT accepted in the hold "
               "for health reasons; they may travel in the cabin if within the weight limit.",
               "Pets must be at least 12 weeks old (15 weeks for travel to another EU country, due to rabies vaccination rules).",
               "Pets are not accepted in the hold from 1 June to 15 September on long-haul routes to Miami, Mexico City and Bogota "
               "because of high ground temperatures.",
               "Customers are responsible for the entry requirements of the destination country (microchip, EU pet passport, USDA / CFIA rules)."])]

    s += [H1("3. Children and unaccompanied minors"),
          TBL([["Age", "Travelling alone", "Fee per direction", "Notes"],
               ["Under 5", "Not allowed", "-", "Must travel with a passenger aged 16 or over"],
               ["5 - 11 years", "UM service MANDATORY", "Domestic €60 / Europe €90 / Long-haul €180",
                "Max 4 UMs per flight on ATR, 8 on A320/A321, 12 on A350/A321XLR. Not on the last flight of the day or on connections."],
               ["12 - 15 years", "UM service OPTIONAL", "Same fees", "Recommended for long-haul flights"],
               ["16 - 17 years", "Travel as adults", "-", "Parental authorisation may be required by Spanish police for international travel"]],
              widths=[2.4 * cm, 3.4 * cm, 4.2 * cm, 7 * cm]),
          P("Infants (under 2 years) travel on an adult's lap. One infant per adult; infants pay a fixed €30 per direction on "
            "Domestic and Europe flights and 10% of the adult fare plus taxes on long-haul. Bassinets (for babies up to 11 kg and 70 cm) "
            "are available free of charge on A350-900 and A321XLR rows 11, 24 and 40 and must be requested in advance. "
            "A child seat (CRS) approved for aviation may be used if a seat has been purchased for the infant."),
          H1("4. Pregnancy"),
          TBL([["Stage of pregnancy", "Single pregnancy", "Multiple pregnancy"],
               ["Up to the end of week 27", "No documents needed", "No documents needed"],
               ["Weeks 28 - 36", "Medical certificate issued within 7 days of travel", "Allowed up to the end of week 32 with certificate"],
               ["From week 37", "Not accepted", "Not accepted (from week 33)"]],
              widths=[5 * cm, 6 * cm, 6 * cm])]

    s += [H1("5. Sports equipment and musical instruments"),
          P("Sports equipment can replace one piece of the free checked allowance if it fits within its size and weight limits. "
            "Otherwise the following fees apply per item and per direction (online / airport):"),
          TBL([["Item", "Max weight", "Domestic", "Europe", "Long-haul"],
               ["Golf bag (bag + shoes)", "23 kg", "€40 / €55", "€55 / €70", "€90 / €110"],
               ["Bicycle (in hard or soft case, pedals removed)", "32 kg", "€60 / €80", "€90 / €110", "€150 / €180"],
               ["Ski or snowboard set (incl. boots)", "23 kg", "€35 / €50", "€50 / €65", "€80 / €100"],
               ["Surfboard (up to 300 cm)", "23 kg", "€60 / €80", "€90 / €110", "€150 / €180"],
               ["Diving equipment (no cylinders)", "23 kg", "€35 / €50", "€50 / €65", "€80 / €100"],
               ["Musical instrument in hold (max 300 cm)", "32 kg", "€50 / €70", "€70 / €90", "€120 / €150"]],
              widths=[6.4 * cm, 2.2 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm]),
          BUL(["Small instruments (violin, guitar up to 118 x 45 x 20 cm) may be carried in the cabin as the cabin bag.",
               "Large instruments such as cellos may travel in the cabin on an extra seat (CBBG) purchased at the same fare as the musician, "
               "on jet aircraft only. Horizon miles are not earned for the extra seat.",
               "Bicycles must be booked at least 24 hours in advance; maximum 4 bicycles per flight on A320neo."])]

    s += [H1("6. Dietary and medical needs"),
          P("Special meals can be requested up to 24 hours before departure on long-haul flights and Business class on Europe "
            "flights: vegetarian (VLML), vegan (VGML), gluten-free (GFML), diabetic (DBML), kosher (KSML), halal (MOML), low-salt (LSML), "
            "child meal (CHML) and baby food (BBML). On Economy short-haul flights, the SkyNova Cafe menu offers vegan and gluten-free "
            "options for purchase. Passengers with a severe nut allergy should inform us at booking; SkyNova stops serving nuts on "
            "board on that flight but cannot guarantee a nut-free environment."),
          P("Medicines, medical liquids and syringes needed during the flight are allowed in the cabin above the 100 ml liquid "
            "limit with a prescription or medical report. Insulin must always be carried in the cabin.")]
    build("SkyNova_03_Special_Assistance_and_Travel_Needs.pdf", "Special Assistance and Travel Needs", "CX-03", "2.4",
          "1 March 2026", s)


# ================================================================== 04 HORIZON LOYALTY
def doc_loyalty():
    s = [about_box(), SP(8)]
    s += [H1("1. Programme overview"),
          P("SkyNova Horizon is the free frequent flyer programme of SkyNova Airlines. Members earn <b>Horizon Miles</b> on SkyNova flights "
            "and with partners, and climb through four tiers: <b>Blue</b>, <b>Silver</b>, <b>Gold</b> and <b>Platinum</b>. Membership is "
            "free and open to anyone aged 2 or older. The programme had 1.3 million active members at the end of 2025."),
          H1("2. Earning miles on SkyNova flights"),
          P("Horizon Miles = flown distance in kilometres x fare multiplier x (1 + tier bonus). Distances are those published in the "
            "Route Network Guide (document OPS-05). Miles are credited within 72 hours after the flight."),
          TBL([["Fare family", "Multiplier", "Example MAD-LHR (1,246 km)", "Example MAD-JFK (5,770 km)"],
               ["Economy Basic", "0.25", "311 miles", "1,442 miles"],
               ["Economy Classic", "1.0", "1,246 miles", "5,770 miles"],
               ["Economy Flex", "1.5", "1,869 miles", "8,655 miles"],
               ["Premium Economy", "1.75", "n/a", "10,097 miles"],
               ["Business", "2.5", "3,115 miles", "14,425 miles"]],
              widths=[4 * cm, 2.5 * cm, 5 * cm, 5.5 * cm]),
          TBL([["Tier", "Tier bonus on miles"], ["Blue", "0%"], ["Silver", "+25%"], ["Gold", "+50%"], ["Platinum", "+100%"]],
              widths=[4 * cm, 4 * cm]),
          NOTE("Example: a Gold member flying MAD-JFK one way in Economy Flex earns 5,770 x 1.5 x 1.5 = 12,982 miles (miles are always rounded down to the whole mile)."),
          P("A minimum of 500 miles is credited for any flight (except Basic fares). Missing miles can be claimed up to 6 months after "
            "the flight with the booking reference and boarding pass.")]

    s += [H1("3. Tiers and qualification"),
          P("Tier status is based on <b>Tier Miles</b> earned in a calendar year (January-December). Tier Miles are the miles earned from "
            "flights before the tier bonus; partner miles, purchased miles and promotional miles do not count. Alternatively, members can "
            "qualify by number of SkyNova flight segments. Status earned is valid until 31 March of the second year (e.g. status earned "
            "during 2026 is valid until 31 March 2028)."),
          TBL([["Tier", "Tier Miles required", "OR flight segments", "Soft landing"],
               ["Blue", "0", "0", "-"],
               ["Silver", "25,000", "30", "Drop maximum one tier per year"],
               ["Gold", "50,000", "60", "Drop maximum one tier per year"],
               ["Platinum", "90,000", "90", "Drop maximum one tier per year; 5 consecutive years = Platinum for Life"]],
              widths=[3 * cm, 4 * cm, 4 * cm, 6 * cm])]

    s += [H1("4. Tier benefits"),
          TBL([["Benefit", "Blue", "Silver", "Gold", "Platinum"],
               ["Extra checked bag", "-", "+1 x 23 kg", "+1 x 32 kg", "+1 x 32 kg"],
               ["Free seat selection", "Standard seat 7 days before", "Standard seats any time", "Incl. extra legroom", "Incl. extra legroom + emergency exit"],
               ["Priority check-in & boarding", "-", "Priority boarding", "Yes", "Yes"],
               ["Fast Track security (MAD, BCN)", "-", "-", "Yes", "Yes"],
               ["Lounge access", "-", "-", "SkyNova Lounges + 1 guest (on Europe & long-haul)", "All partner lounges + 2 guests"],
               ["Waitlist & standby priority", "-", "Medium", "High", "Highest"],
               ["Complimentary upgrade vouchers", "-", "-", "2 per year (Europe)", "4 per year (any route)"],
               ["Dedicated phone line", "-", "-", "Gold line 24/7", "Platinum concierge 24/7"],
               ["Guaranteed seat on full flights", "-", "-", "-", "Yes, if booked 24 h before departure (Economy)"],
               ["Mile expiry", "24 months inactivity", "Never while Silver", "Never while Gold", "Never"]],
              widths=[4.2 * cm, 2.6 * cm, 3.0 * cm, 3.6 * cm, 3.6 * cm], font=7.6)]

    s += [H1("5. Spending miles"),
          H2("5.1 Award flights (one way, per passenger, plus taxes)"),
          TBL([["Zone", "Routes", "Economy", "Premium Economy", "Business"],
               ["Domestic 1", "Spain domestic up to 1,000 km (BIO, SCQ, AGP, PMI, BCN)", "7,500", "-", "15,000"],
               ["Domestic 2", "Canary Islands (TFN)", "10,000", "-", "20,000"],
               ["Europe 1", "Up to 1,500 km (LIS, CDG, LHR, FCO, FRA, AMS, MUC)", "10,000", "-", "22,500"],
               ["Europe 2", "1,501 - 3,000 km (CPH, ATH)", "15,000", "-", "32,000"],
               ["North America", "BOS, YUL, JFK, MIA", "30,000", "45,000", "70,000"],
               ["Latin America", "BOG, MEX, EZE", "40,000", "58,000", "90,000"]],
              widths=[2.6 * cm, 6.6 * cm, 2.4 * cm, 2.8 * cm, 2.6 * cm]),
          P("Off-peak discount: award flights between 15 January - 15 March and 1 - 30 November cost <b>20% fewer miles</b>. Award tickets "
            "can be changed for 2,500 miles or cancelled with miles redeposited for 5,000 miles (free for Gold and Platinum)."),
          H2("5.2 Upgrades with miles (one way)"),
          TBL([["Upgrade", "Europe", "North America", "Latin America"],
               ["Economy Classic / Flex to Business", "8,000", "25,000", "30,000"],
               ["Economy Classic / Flex to Premium Economy", "-", "12,000", "15,000"],
               ["Premium Economy to Business", "-", "15,000", "18,000"]],
              widths=[7 * cm, 3 * cm, 3.5 * cm, 3.5 * cm]),
          NOTE("Upgrades are not available on Economy Basic fares. They can be requested up to 24 hours before departure, subject to availability."),
          H2("5.3 Other uses"),
          BUL(["Extra bag: 4,000 miles (Domestic / Europe), 9,000 miles (Long-haul).",
               "Lounge pass: 3,500 miles. Seat selection: from 1,000 miles.",
               "Miles + Cash: pay part of any fare with miles, at 1,000 miles = €8.",
               "Donate miles to the SkyNova Foundation (humanitarian flights) from 1,000 miles."])]

    s += [H1("6. Buying, pooling and partners"),
          BUL(["Buy miles: €30 per 1,000 miles, maximum 50,000 miles per calendar year.",
               "Family pooling: up to 6 members (same address) can combine miles in one Family Account; Tier Miles are not shared.",
               "Transfer miles to another member: €10 per 1,000 miles, maximum 20,000 per year.",
               "Partners: NovaStay Hotels (3 miles per €1 spent), RoadNova car rental (500 miles per rental), SkyNova Visa card "
               "(1 mile per €1, 2 miles per €1 on SkyNova purchases), Renfe AVE connections (250 miles per journey)."]),
          H1("7. Status match and challenge"),
          P("Members holding gold or higher status with another airline programme may request a one-time <b>Status Challenge</b>: SkyNova grants "
            "Gold for 90 days; to keep it until 31 March of the following year, the member must earn 15,000 Tier Miles within those 90 days. "
            "Fee: €99, refunded as 9,900 miles if the challenge is completed."),
          H1("8. General terms"),
          P("Miles have no cash value and cannot be sold. SkyNova may close accounts involved in fraud or mileage brokering. Changes to "
            "the award chart are announced at least 90 days in advance.")]
    build("SkyNova_04_Horizon_Loyalty_Program.pdf", "Horizon Loyalty Program Guide", "CX-04", "5.0", "1 January 2026", s)


# ================================================================== 05 NETWORK & FLEET
def doc_network():
    s = [about_box(), SP(8)]
    s += [H1("1. Network overview"),
          P(f"SkyNova operates {len(D.ROUTES)} routes from its hub in Madrid and its base in Barcelona: "
            f"{sum(r['haul']=='Domestic' for r in D.ROUTES)} domestic, {sum(r['haul']=='Europe' for r in D.ROUTES)} European and "
            f"{sum(r['haul']=='Long-haul' for r in D.ROUTES)} long-haul. Connections at MAD Terminal 4S use a minimum connecting time of "
            "45 minutes (Schengen to Schengen) and 60 minutes (Schengen to non-Schengen and vice versa). Bags are checked through to the "
            "final destination when all flights are on the same booking."),
          H1("2. Route table and summer schedule 2026"),
          P("Schedule valid from 29 March to 24 October 2026 (IATA summer season). Times are local departure times of the outbound flight; "
            "return flight numbers are the outbound number + 1 (e.g. NV120 MAD-LHR, NV121 LHR-MAD).")]
    rows = [["Flight", "Route", "Destination", "Km", "Aircraft", "Weekly freq.", "Departures (local)", "Block time"]]
    for r in D.ROUTES:
        rows.append([r["flight"], r["route"], f'{r["city"]}, {r["country"]}', f'{r["km"]:,}', r["ac"], r["freq"],
                     r["dep_times"], r["block"]])
    s.append(TBL(rows, widths=[1.3 * cm, 1.8 * cm, 3.6 * cm, 1.2 * cm, 2.4 * cm, 1.4 * cm, 3.4 * cm, 1.6 * cm], font=7.2))
    s.append(NOTE("Weekly frequency = number of outbound flights per week. Long-haul days of operation: "
                  + "; ".join(f'{r["route"]} {r["days"]}' for r in D.ROUTES if r["haul"] == "Long-haul") + "."))

    s += [H2("2.1 Winter 2026/27 changes (from 25 October 2026)"),
          BUL(["NEW route MAD-YYZ (Toronto, 5,980 km) starts 1 December 2026, 4 weekly flights on Airbus A321XLR, flight NV690.",
               "MAD-EZE increases from 3 to 5 weekly flights between 15 December 2026 and 28 February 2027.",
               "BCN-AMS is suspended between 9 November 2026 and 28 February 2027.",
               "MAD-PMI reduces from 4 to 2 daily flights during winter; MAD-TFN increases to 3 daily flights."])]

    s += [H1("3. Fleet"),
          TBL([["Aircraft", "Units", "Seats", "Business", "Premium Eco", "Economy", "Eco pitch", "Avg age (yrs)", "Use"]] +
              [[f["model"], f["count"], f["seats"], f["business"], f["premium"] or "-", f["economy"], f["pitch"], f["age"], f["haul"]]
               for f in D.FLEET] +
              [["TOTAL", sum(f["count"] for f in D.FLEET), "", "", "", "", "", "", ""]],
              widths=[2.8 * cm, 1.2 * cm, 1.3 * cm, 1.6 * cm, 1.9 * cm, 1.6 * cm, 1.6 * cm, 1.8 * cm, 3.2 * cm], font=7.6),
          SP(),
          TBL([["Aircraft", "Wi-Fi", "Power", "Entertainment"]] +
              [[f["model"], f["wifi"], f["power"], f["ife"]] for f in D.FLEET],
              widths=[3 * cm, 1.8 * cm, 5.2 * cm, 7 * cm], font=7.8),
          H2("3.1 Cabin products"),
          BUL(["<b>Business (A320neo / A321neo)</b>: European-style Business; blocked middle seat, 32\" pitch, full meal service.",
               "<b>Business (A350-900 / A321XLR)</b>: 'NovaSuite' fully flat bed (198 cm), direct aisle access, 1-2-1 layout on the A350, "
               "1-1 on the A321XLR, sliding door on A350 rows 1-2.",
               "<b>Premium Economy (A350-900 only)</b>: 38\" pitch, 2-4-2 layout, 48 cm wide seat, leg rest, upgraded meal.",
               "<b>Economy</b>: ergonomic slimline seats, 30-31\" pitch; extra legroom rows (34\") on rows 1-3 and emergency exits."]),
          H1("4. On-board services"),
          H2("4.1 Wi-Fi prices"),
          TBL([["Plan", "Domestic & Europe", "Long-haul"],
               ["Messaging (WhatsApp, iMessage...)", "Free for Horizon members", "Free for Horizon members"],
               ["Browse", "€6", "€14"],
               ["Stream (full flight)", "€10", "€22"],
               ["Business class & Platinum members", "Stream free", "Stream free"]],
              widths=[6 * cm, 5.5 * cm, 5.5 * cm]),
          H2("4.2 SkyNova Cafe menu (Economy, Domestic & Europe flights)"),
          P("Meals and drinks are complimentary in Business on all routes and in all cabins on long-haul flights. In Economy on "
            "domestic and European flights, the following items can be purchased by card (pre-order in the app 24 h before = 10% discount)."),
          TBL([["Item", "Price", "Dietary"],
               ["Iberian ham sandwich on tomato bread", "€8.50", "-"],
               ["Spanish omelette (tortilla) sandwich", "€6.50", "Vegetarian"],
               ["Mediterranean quinoa salad", "€7.50", "Vegan, gluten-free"],
               ["Manchego cheese & crackers", "€5.00", "Vegetarian"],
               ["Kids' box (sandwich, juice, fruit, toy)", "€7.00", "-"],
               ["Coffee / tea", "€2.50", "-"],
               ["Soft drink / juice / water 50 cl", "€2.50 / €3.00 / €2.00", "-"],
               ["Beer / glass of wine (Rioja, Rueda)", "€4.50 / €5.50", "Alcohol 18+"],
               ["Meal deal: any sandwich + drink + snack", "€11.00", "-"]],
              widths=[8 * cm, 4.5 * cm, 4.5 * cm]),
          H1("5. Lounges"),
          TBL([["Lounge", "Location", "Opening hours", "Highlights"],
               ["SkyNova Lounge Velazquez", "MAD T4S, gate area S", "05:30 - 23:59", "Long-haul lounge, shower suites, a la carte dining"],
               ["SkyNova Lounge Goya", "MAD T4, Schengen gates H-J", "05:00 - 22:30", "Terrace with runway views, family room"],
               ["SkyNova Lounge Mirador", "BCN T1, Schengen area", "05:30 - 22:00", "Mediterranean buffet, quiet zone"],
               ["Partner lounges", "LHR, CDG, FCO, JFK, MIA, MEX, BOG, EZE", "According to flight", "For eligible Business and Gold/Platinum customers"]],
              widths=[4 * cm, 4.2 * cm, 2.8 * cm, 6 * cm])]
    build("SkyNova_05_Route_Network_and_Fleet_Guide.pdf", "Route Network and Fleet Guide", "OPS-05", "2026-S",
          "29 March 2026", s)


# ================================================================== 06 PERFORMANCE REPORT
def doc_performance():
    rows26, rows25 = D.PERF_2026, D.PERF_2025
    q26, q25 = D.network_summary(rows26), D.network_summary(rows25)
    months = [m for m, _ in D.MONTHS]
    ms = {m: D.network_summary(rows26, m) for m in months}

    # route aggregates for narrative
    agg = defaultdict(lambda: defaultdict(float))
    for x in rows26:
        a = agg[x["route"]]
        for k in ("operated_flights", "on_time_flights", "cancelled_flights", "passengers", "complaints", "mishandled_bags"):
            a[k] += x[k]
    otp_route = {k: v["on_time_flights"] / v["operated_flights"] * 100 for k, v in agg.items()}
    best = sorted(otp_route.items(), key=lambda kv: -kv[1])[:3]
    worst = sorted(otp_route.items(), key=lambda kv: kv[1])[:3]

    s = [about_box(), SP(8)]
    s += [H1("1. Executive summary"),
          P(f"In the third quarter of 2026 (July-September) SkyNova operated <b>{q26['operated']:,}</b> flights and carried "
            f"<b>{q26['pax']:,}</b> passengers, with an average load factor of <b>{q26['lf']}%</b>. On-time performance (OTP, arrival "
            f"within 15 minutes of schedule) was <b>{q26['otp']}%</b>, compared with {q25['otp']}% in Q3 2025. "
            f"{q26['cancelled']} flights were cancelled ({q26['cancel_rate']}% of the schedule)."),
          P(f"August was the most challenging month (OTP {ms['Aug 2026']['otp']}%), affected by French air traffic control strikes "
            "on 6-8 and 21-22 August, which mainly disrupted Paris routes and overflights to Northern Europe, and by heat waves at "
            f"Madrid that limited ground operations. September recovered strongly to {ms['Sep 2026']['otp']}% OTP."),
          P("Best-performing routes in the quarter: " + ", ".join(f"{k} ({v:.1f}%)" for k, v in best) +
            ". Routes requiring action: " + ", ".join(f"{k} ({v:.1f}%)" for k, v in worst) + "."),
          H1("2. Network KPIs"),
          TBL([["KPI", "Jul 2026", "Aug 2026", "Sep 2026", "Q3 2026", "Q3 2025", "Target 2026"],
               ["Scheduled flights"] + [f"{ms[m]['scheduled']:,}" for m in months] + [f"{q26['scheduled']:,}", f"{q25['scheduled']:,}", "-"],
               ["Operated flights"] + [f"{ms[m]['operated']:,}" for m in months] + [f"{q26['operated']:,}", f"{q25['operated']:,}", "-"],
               ["Cancelled flights"] + [str(ms[m]['cancelled']) for m in months] + [str(q26['cancelled']), str(q25['cancelled']), "-"],
               ["Cancellation rate"] + [f"{ms[m]['cancel_rate']}%" for m in months] + [f"{q26['cancel_rate']}%", f"{q25['cancel_rate']}%", "< 1.0%"],
               ["On-time performance (A15)"] + [f"{ms[m]['otp']}%" for m in months] + [f"{q26['otp']}%", f"{q25['otp']}%", "82.0%"],
               ["Passengers"] + [f"{ms[m]['pax']:,}" for m in months] + [f"{q26['pax']:,}", f"{q25['pax']:,}", "-"],
               ["Load factor"] + [f"{ms[m]['lf']}%" for m in months] + [f"{q26['lf']}%", f"{q25['lf']}%", "86.0%"],
               ["Mishandled bags per 1,000 pax"] + [str(ms[m]['bags_per_1000']) for m in months] + [str(q26['bags_per_1000']), str(q25['bags_per_1000']), "< 5.0"],
               ["Complaints per 10,000 pax"] + [str(ms[m]['complaints_per_10k']) for m in months] + [str(q26['complaints_per_10k']), str(q25['complaints_per_10k']), "< 30"],
               ["Net Promoter Score (NPS)"] + [str(int(ms[m]['nps'])) for m in months] + [str(int(q26['nps'])), str(int(q25['nps'])), "40"]],
              widths=[4.4 * cm, 1.9 * cm, 1.9 * cm, 1.9 * cm, 2.0 * cm, 2.0 * cm, 2.0 * cm], font=7.8)]

    s += [H1("3. Delay causes"),
          P("Share of total delay minutes by primary cause (IATA delay code groups), network level:"),
          TBL([["Cause"] + months] + [[c] + [f"{D.CAUSE_SHARE[m][i]}%" for m in months] for i, c in enumerate(D.DELAY_CAUSES)],
              widths=[7 * cm, 3 * cm, 3 * cm, 3 * cm]),
          P("Reactionary delays (late inbound aircraft) remain the largest controllable driver. The Operations team has launched the "
            "'Turn 35' programme to cut A320neo turnaround time at MAD from 40 to 35 minutes and added two standby aircraft at MAD "
            "(one A320neo, one A321neo) from 1 October 2026.")]

    for m in months:
        s += [PageBreak(), H1(f"4.{months.index(m) + 1} Route performance - {m}")]
        rr = [["Route", "Flight", "Haul", "Sched.", "Oper.", "Canc.", "OTP %", "Avg delay (min)", "Pax", "LF %", "Bags", "Compl.", "NPS"]]
        for x in [y for y in rows26 if y["month"] == m]:
            rr.append([x["route"], x["flight"], x["haul"], x["scheduled_flights"], x["operated_flights"], x["cancelled_flights"],
                       x["otp_pct"], x["avg_delay_min"], f"{x['passengers']:,}", x["load_factor_pct"], x["mishandled_bags"],
                       x["complaints"], x["nps"]])
        s.append(TBL(rr, widths=[1.65 * cm, 1.2 * cm, 1.55 * cm, 1.1 * cm, 1.1 * cm, 1.0 * cm, 1.1 * cm, 1.45 * cm, 1.55 * cm,
                                 1.1 * cm, 1.0 * cm, 1.1 * cm, 1.0 * cm], font=6.9))
        s.append(NOTE("Flights counted in both directions. Avg delay = average arrival delay of flights arriving more than 15 minutes late. "
                      "Bags = mishandled bags (delayed, damaged or lost). Compl. = written complaints received."))

    s += [PageBreak(), H1("5. Customer feedback"),
          TBL([["Complaint category", "Share Q3 2026", "Share Q3 2025", "Trend"],
               ["Delays and cancellations", "41%", "37%", "Up"],
               ["Baggage (delayed / damaged)", "19%", "21%", "Down"],
               ["Refunds and vouchers processing time", "12%", "15%", "Down"],
               ["Airport experience (queues, gates)", "9%", "8%", "Stable"],
               ["Onboard product (seats, food, Wi-Fi)", "8%", "9%", "Stable"],
               ["Contact Centre waiting time", "6%", "6%", "Stable"],
               ["Horizon loyalty programme", "3%", "2%", "Up"],
               ["Other", "2%", "2%", "Stable"]],
              widths=[7 * cm, 3.3 * cm, 3.3 * cm, 3.4 * cm]),
          P(f"Total written complaints in Q3 2026: {q26['complaints']:,}. Average first-response time was 31 hours (target 48 h) and "
            "average resolution time 11.4 days (target 30 days). 87% of EU 261 compensation claims were paid within 14 days of approval."),
          H1("6. Actions for Q4 2026"),
          BUL(["Paris routes (MAD-CDG, BCN-CDG): add 15 minutes of schedule buffer on the 07:00 and 07:40 departures and pre-emptively "
               "re-route via Spanish airspace during announced French ATC strikes.",
               "Long-haul Latin America (MEX, BOG): new A350 maintenance slot at night to reduce technical delays; MEX departure moved "
               "from 14:20 to 13:50 in winter.",
               "Baggage: RFID tracking on 100% of bags at MAD from November 2026; target below 4.5 mishandled bags per 1,000 passengers.",
               "Customer Care: AI-assisted Contact Centre agent launch planned for Q4 2026 to answer policy questions 24/7."])]
    build("SkyNova_06_Operational_Performance_Report_Q3_2026.pdf", "Operational Performance Report Q3 2026", "OPS-06", "1.0",
          "15 October 2026", s)


# ================================================================== 07 CUSTOMER SERVICE FAQ
def doc_faq():
    s = [about_box(), SP(8)]
    s += [H1("1. Contact channels and opening hours"),
          TBL([["Channel", "Details", "Hours (Madrid time, CET/CEST)", "Target response"],
               ["Phone - Spain", "+34 910 000 555 (fictional)", "24/7", "Answer within 3 minutes"],
               ["Phone - International", "+44 20 0000 0555 / +1 212 000 0555 (fictional)", "24/7", "Answer within 5 minutes"],
               ["Horizon Gold / Platinum line", "Number in the app", "24/7", "Answer within 60 seconds"],
               ["Live chat & WhatsApp", "skynova.example / app", "06:00 - 24:00", "Reply within 2 minutes"],
               ["Email / web form", "skynova.example/contact", "Always open", "Reply within 48 hours"],
               ["Airport desks", "MAD T4 & T4S, BCN T1", "From first to last departure", "-"],
               ["Social media", "@SkyNovaCares", "08:00 - 22:00", "Reply within 1 hour"]],
              widths=[3.6 * cm, 5.4 * cm, 4 * cm, 4 * cm], font=7.8)]

    s += [H1("2. Customer service standards"),
          P("All SkyNova customer-facing staff and digital assistants follow the <b>CARE</b> model:"),
          BUL(["<b>C - Connect</b>: greet the customer warmly, use their name when known, and thank them for flying with SkyNova.",
               "<b>A - Acknowledge</b>: show empathy, especially in disruptions (\"I'm sorry your trip has been affected, I'll help you right away\").",
               "<b>R - Resolve</b>: give accurate information based on official policy; quote amounts, deadlines and conditions precisely. "
               "Never promise something that is not in policy; when unsure, say so and offer to escalate.",
               "<b>E - Empower</b>: always finish with the next step (link, reference, deadline) and ask if anything else is needed."]),
          P("Agents must never ask customers for full card numbers, CVV codes or passwords. Booking changes require the booking reference "
            "and the passenger's surname. Personal data is handled in accordance with the GDPR.")]

    faqs = [
        ("Can I change the date of my flight?", "Yes, depending on your fare. Classic fares pay a change fee of €60 (Domestic/Europe) or "
         "€150 (Long-haul) plus any fare difference; Flex and Business change for free; Basic fares cannot be changed. Changes are made in "
         "Manage Booking up to 2 hours before departure."),
        ("I booked yesterday and want to cancel. Will I get my money back?", "If you booked directly with SkyNova less than 24 hours ago "
         "and departure is at least 7 days away, you can cancel for free and receive a full refund, whatever your fare."),
        ("How long does a refund take?", "Refunds to credit or debit cards are processed within 7 days; bank transfers can take up to 20 days "
         "depending on your bank. Refunds for bookings made through travel agencies are handled by the agency."),
        ("My flight is delayed. What are my rights?", "You are entitled to meals and refreshments from 2, 3 or 4 hours of delay depending "
         "on the distance, and to compensation of €250, €400 or €600 if you arrive 3 hours or more late and the cause was within our control. "
         "See the Passenger Care and Compensation Policy (CX-02)."),
        ("My bag did not arrive. What should I do?", "Please go to the SkyNova Baggage Services desk before leaving the arrival hall to "
         "obtain a PIR reference. You can follow the search at skynova.example/bags. You may claim up to €50 per day (max. 5 days) for "
         "essential items; Gold and Platinum members up to €75 per day."),
        ("Can I take my dog on board?", "Dogs and cats up to 8 kg including the carrier can travel in the cabin on jet aircraft for €50 "
         "(Domestic), €70 (Europe) or €150 (Long-haul, A350/A321XLR). Pets are not accepted in the cabin on ATR 72-600 flights (MAD-BIO, MAD-SCQ)."),
        ("Can my 10-year-old fly alone?", "Yes, with our mandatory Unaccompanied Minor service (€60 Domestic, €90 Europe, €180 Long-haul per "
         "direction). Children under 5 cannot travel alone."),
        ("Is there Wi-Fi on board?", "Yes, on all jet aircraft. Messaging is free for Horizon members; Browse costs €6 (Europe) / €14 "
         "(Long-haul) and Stream €10 / €22. ATR 72-600 aircraft have no Wi-Fi."),
        ("When does online check-in open?", "48 hours before departure on all flights. It closes 1 hour before departure (Domestic/Europe) "
         "or 2 hours before (Long-haul)."),
        ("How many miles will I earn?", "Flown kilometres x fare multiplier (Basic 0.25, Classic 1.0, Flex 1.5, Premium 1.75, Business 2.5) "
         "plus your tier bonus (Silver +25%, Gold +50%, Platinum +100%)."),
        ("I missed my outbound flight. Is my return cancelled?", "No, provided you contact us before the departure of your return flight. "
         "We will keep your return booking."),
        ("Can I bring a power bank?", "Yes, in the cabin only. Up to 2 power banks of maximum 100 Wh each; 100-160 Wh require approval; "
         "above 160 Wh are not allowed. Power banks are never allowed in checked baggage."),
        ("Do I need a claims company to get compensation?", "No. You can claim directly and free of charge at skynova.example/claims. "
         "We reply within 30 days and pay within 14 days of approval."),
        ("Can I get my compensation as a voucher?", "Yes, if you prefer: the voucher is worth 120% of the cash amount and can be converted "
         "back to cash during its 12-month validity. Cash is always available."),
        ("I am pregnant. Can I fly?", "Yes. No documents are needed up to the end of week 27. From week 28 to 36 (single pregnancy) you "
         "need a medical certificate issued within 7 days of the flight."),
        ("What is the minimum connection time in Madrid?", "45 minutes between Schengen flights and 60 minutes between Schengen and "
         "non-Schengen flights at Terminal 4/4S."),
    ]
    s += [H1("3. Frequently asked questions")]
    for i, (q, a) in enumerate(faqs, 1):
        s.append(KeepTogether([H2(f"3.{i} {q}"), P(a)]))

    s += [H1("4. Example responses (tone guide)"),
          BOX("<b>Delay situation.</b> \"Good afternoon, Ms. Ortega, and thank you for contacting SkyNova. I'm truly sorry that flight NV120 "
              "to London is delayed. The current estimated departure is 13:40, about 2 hours and 30 minutes late, due to air traffic "
              "control restrictions. While you wait, a €12 meal voucher has been sent to your SkyNova app. Because ATC restrictions "
              "are considered extraordinary circumstances, EU compensation does not apply in this case, but I will keep you updated "
              "and you can rebook free of charge on today's 16:20 flight if that suits you better. Is there anything else I can help you with?\""),
          SP(),
          BOX("<b>Declining a request politely.</b> \"I completely understand that you'd like to transfer the ticket to your colleague. "
              "Unfortunately, SkyNova tickets are personal and the name can't be changed; we can only correct up to 3 characters. "
              "What I can offer is to check the refund conditions of your fare and find the best available fare for your colleague. "
              "Shall I do that for you?\""),
          H1("5. Escalation matrix"),
          TBL([["Situation", "Escalate to", "Timeframe"],
               ["Customer stranded overnight without hotel", "Airport Duty Manager", "Immediately"],
               ["Medical or safety concern", "Operations Control Centre (OCC)", "Immediately"],
               ["Compensation claim older than 30 days without answer", "Customer Relations Office", "Within 24 hours"],
               ["Complaint mentioning discrimination or accessibility", "Accessibility & Inclusion team", "Within 24 hours"],
               ["Media or social media influencer complaint", "Corporate Communications", "Within 2 hours"]],
              widths=[7.5 * cm, 5.5 * cm, 4 * cm])]
    build("SkyNova_07_Customer_Service_Guide_and_FAQ.pdf", "Customer Service Guide and FAQ", "CX-07", "1.6", "1 June 2026", s)


# ================================================================== CSV for Code Interpreter
def write_csv():
    os.makedirs(CSV_DIR, exist_ok=True)
    path = os.path.join(CSV_DIR, "skynova_operational_performance_q3_2025_2026.csv")
    rows = D.PERF_2025 + D.PERF_2026
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("  ✓", os.path.relpath(path, ROOT), f"({len(rows)} rows)")


if __name__ == "__main__":
    print("Generating SkyNova knowledge base...")
    doc_fares_baggage()
    doc_compensation()
    doc_special()
    doc_loyalty()
    doc_network()
    doc_performance()
    doc_faq()
    write_csv()
    print("Done.")

# SkyNova Agent – Test Questions

Use these prompts to check that the agent uses each of its capabilities correctly. Expected answers come from the PDFs in `data/pdfs/`.

## 1. RAG (knowledge base)

| # | Question | Expected answer | Source |
|---|----------|-----------------|--------|
| 1 | I have an Economy Classic ticket MAD–JFK. How much does it cost to add a second bag of 27 kg online? | €70 (1st extra bag, long-haul online) + €75 (overweight) = **€145** per direction | CX-01 §5 |
| 2 | Can I cancel my Basic fare booked 3 hours ago? Departure is in 10 days. | Yes, free cancellation within 24 h if booked ≥7 days before departure; full refund | CX-01 §2.1 |
| 3 | My MAD–ATH flight arrived 3h20m late because of a crew shortage. What compensation do I get? | **€400** (band B, 2,370 km); crew shortage is not extraordinary | CX-02 §2, §3.2, §5 |
| 4 | My MAD–MEX flight arrived 3h30m late due to a technical fault. How much compensation? | Band C, 3–4 h arrival delay → reduced 50% = **€300** | CX-02 §3.2 |
| 5 | My flight was delayed by a French ATC strike. Do I get compensation? | No compensation (extraordinary), but right to care applies (meals, hotel if needed) | CX-02 §5 |
| 6 | Can I take my 6 kg French Bulldog to Bilbao? | No: ATR 72-600 (MAD–BIO) accepts no pets in cabin; brachycephalic breeds not accepted in hold | CX-03 §2 |
| 7 | My 10-year-old is flying alone to Miami. How much is it? | UM service mandatory, **€180** per direction | CX-03 §3 |
| 8 | How many miles does a Gold member earn MAD–JFK in Economy Flex? | 5,770 × 1.5 × 1.5 = **12,982** | CX-04 §2 |
| 9 | How many miles do I need for a one-way Business award to Buenos Aires in November? | 90,000 − 20% off-peak = **72,000** | CX-04 §5.1 |
| 10 | My bag is delayed. I'm a Gold member. How much can I spend per day? | **€75** per day, max 5 days | CX-02 §7 |
| 11 | What's the minimum connecting time at Madrid from Paris to New York? | 60 min (Schengen → non-Schengen) | OPS-05 §1 |
| 12 | Which aircraft flies MAD–BOS and does it have Wi-Fi? | Airbus A321XLR, Wi-Fi yes | OPS-05 §2, §3 |
| 13 | What was SkyNova's on-time performance in August 2026, and why? | **73.1%**, French ATC strikes (6–8 and 21–22 Aug) + Madrid heat waves | OPS-06 §1 |
| 14 | When does the new Toronto route start? | 1 December 2026, 4 weekly flights, A321XLR, NV690 | OPS-05 §2.1 |

## 2. Code Interpreter (upload `data/csv/skynova_operational_performance_q3_2025_2026.csv` or use the table in OPS-06)

- "Plot the monthly on-time performance for the Paris routes (MAD-CDG, BCN-CDG) vs the network average in Q3 2026."
- "Which 5 routes had the most complaints per 10,000 passengers in Q3 2026? Show a bar chart."
- "Compare Q3 2026 vs Q3 2025 load factor by haul type (Domestic / Europe / Long-haul)."
- "Is there a correlation between OTP and NPS across routes? Plot a scatter with a regression line."
- "Calculate the total compensation SkyNova would pay if 150 passengers on MAD–EZE arrived 4h30m late due to a technical fault."
  → 150 × €600 = **€90,000**

## 3. MCP – GitHub (case management in `luis-martin-b/skynova-customer-cases`)

| # | Prompt | Expected behaviour |
|---|--------|--------------------|
| 1 | "I can't check in on the app, it says error NV-CHK-502." | Finds known incident #1: use the web, iOS app or kiosks; no airport fee; fix expected 4 Nov |
| 2 | "I'm flying to Paris on 12 November, is there any problem?" | Finds incident #2 (ATC strike): free change 10–20 Nov or refund; no EU 261 compensation, but right to care |
| 3 | "What's the status of my case #3? I'm Mr. Navarro." | Bag located; delivery 31 Oct 18:00–22:00 |
| 4 | "My bag didn't arrive on NV120 from Madrid to London today. PIR LHRNV10293, booking NV8HJK, I'm Ana Ruiz, Silver member." | Explains €50/day (max 5 days), asks for confirmation, then creates an issue with labels `baggage` + `created-by-agent` and gives the case number |

## 4. Combined (RAG + Code Interpreter)

- "I fly MAD–FCO on an Economy Classic fare with my infant (under 2). How much will I pay per direction for the infant's ticket plus 3 extra checked bags bought online?"
  → infant fare €30 + extra bags €35 + €50 + €90 = **€205** (the infant's own 10 kg bag, stroller and car seat are free)

# Challenge-Agent-MS-Foundry ✈️ SkyNova Airlines Customer Care Agent

An agentic solution built on **Microsoft Foundry** with the **Microsoft Foundry SDK (Python)**. The agent is a polite, professional customer-service assistant for **SkyNova Airlines**, a fictional airline.

---

## 📋 Challenge instructions

In this challenge you build an agentic solution for a scenario of your choice. It must meet these requirements:

1. **The agent uses an existing model** deployed in our Foundry Project.
2. **The agent is created in Foundry**, either in the UI or programmatically with the Foundry SDK.
3. **The agent is configured with:**
   - A **system message / instructions** that guide the agent's behaviour
   - **Code Interpreter**
   - **An MCP server integration** (research which one suits the scenario)
   - **Custom data:** sample PDF documents created with any GenAI and given to the teacher, who creates the index that the agent connects to
4. **A program that interacts with the agent**, sending prompts and receiving responses:
   - It handles authentication and the connection to the agent
   - The terminal is the first interface
5. **(EXTRA)** A web interface for interacting with the agent.

---

## 🛫 Scenario: SkyNova Airlines

SkyNova Airlines (IATA code `NV`) is a fictional full-service carrier based in Madrid (hub MAD, base BCN). It has 44 aircraft and flies 26 routes across Spain, Europe and the Americas.

The agent answers customer questions in a professional, polite customer-service tone:

| Capability | How the agent uses it |
|---|---|
| **Instructions** | Customer-service persona that follows SkyNova's *CARE* model (Connect, Acknowledge, Resolve, Empower) |
| **RAG (custom data)** | Fare rules, baggage fees, EU 261 compensation, pets and minors, loyalty programme, network and fleet, Q3 2026 performance report |
| **Code Interpreter** | Fee and compensation calculations, miles calculations, charts and analysis of operational performance data |
| **MCP server** | Live external information, such as weather or airport status (TBD) |

## 📁 Repository structure

```
├── data/
│   ├── pdfs/                 # Knowledge base for the index (7 PDFs)
│   ├── csv/                  # Performance dataset for Code Interpreter
│   └── test_questions.md     # Evaluation prompts with expected answers
├── data_generation/
│   ├── skynova_data.py       # Shared master data (routes, fleet, performance generator)
│   └── generate_pdfs.py      # Builds the PDFs + CSV with reportlab
└── requirements.txt
```

### Knowledge base (`data/pdfs/`)

| File | Content |
|---|---|
| `SkyNova_01_Fares_and_Baggage_Policy.pdf` | Fare families, change and refund rules, baggage allowances and fees, check-in deadlines |
| `SkyNova_02_Passenger_Care_and_Compensation_Policy.pdf` | Delays, cancellations, denied boarding (EU 261), SkyNova Care Promise, baggage claims |
| `SkyNova_03_Special_Assistance_and_Travel_Needs.pdf` | Reduced mobility, pets, unaccompanied minors, infants, pregnancy, sports equipment, special meals |
| `SkyNova_04_Horizon_Loyalty_Program.pdf` | Tiers, earning and award charts, upgrades, partners |
| `SkyNova_05_Route_Network_and_Fleet_Guide.pdf` | Routes, flight numbers, schedule, fleet, Wi-Fi, onboard menu, lounges |
| `SkyNova_06_Operational_Performance_Report_Q3_2026.pdf` | KPIs, delay causes, route performance per month, complaints |
| `SkyNova_07_Customer_Service_Guide_and_FAQ.pdf` | Contact channels, CARE model, FAQs, tone examples, escalation |

All data is internally consistent: routes, distances, compensation bands and fares match across documents.

### Regenerate the data

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python data_generation/generate_pdfs.py
```

## 🗺️ Roadmap

- [x] Synthetic knowledge base (PDFs + CSV)
- [ ] Hand the PDFs to the teacher for indexing (Azure AI Search)
- [ ] Create the agent in the Foundry portal (model, instructions, Code Interpreter, MCP, AI Search index)
- [ ] Terminal client with the Foundry SDK (`azure-ai-projects` + `azure-identity`)
- [ ] (EXTRA) Web interface

> ⚠️ SkyNova Airlines is fictional. All documents were generated for educational purposes.

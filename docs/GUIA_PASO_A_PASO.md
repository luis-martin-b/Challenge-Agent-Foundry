# Guía paso a paso: agente SkyNova en Microsoft Foundry

> Documento de estudio. Explica **todo** lo que se hizo para construir el agente: qué, cómo y **por qué**, incluidos los errores que aparecieron y cómo se resolvieron.

---

## 🚀 Chuleta rápida: volver a abrir la web después de reiniciar el Mac

Abre la app **Terminal** y pega **esta única línea** (todo en una; si algún paso falla, se para):

```bash
cd "$HOME/Desktop/Obsidian Master/Masters/01 Courses/01 Cloud Computing/03 Unai Azure/Challenge 4/Challenge-Agent-Foundry" && git pull && source .venv/bin/activate && python app/web.py
```

Qué hace cada parte: `cd` entra en la carpeta del proyecto, `git pull` trae los cambios de GitHub, `source .venv/bin/activate` activa el entorno virtual y `python app/web.py` arranca el servidor.

> ⚠️ No pegues los comandos en varias líneas con comentarios (`# ...`): a veces el `cd` no se ejecuta y todo lo demás falla (`not a git repository`, `.venv/bin/activate: No such file`, `python: command not found`). Si el prompt sigue mostrando `~`, es que no has entrado en la carpeta.
> `python` solo existe **con el venv activado**; fuera de él, el Mac solo tiene `python3`.

Cuando aparezca `SkyNova web app -> http://localhost:8000`, abre **http://localhost:8000** en el navegador.

- Deja la Terminal abierta mientras uses la web. Para apagarla: **Ctrl + C**.
- Para usar el cliente de **terminal** en lugar de la web: `python app/cli.py` (mismos tres primeros comandos).
- Si da error de autenticación (porque la sesión de Azure ha caducado): ejecuta `az login`, entra con la cuenta `madi12@madiunavoutlook.onmicrosoft.com` y vuelve a lanzar el comando.
- Si dice `address already in use` (puerto 8000 ocupado): ya hay un servidor encendido. Abre la web directamente o ciérralo con `lsof -ti:8000 | xargs kill`.

---

## Índice
0. [El reto](#0-el-reto)
1. [Elección del escenario](#1-elección-del-escenario)
2. [Datos sintéticos (PDFs + CSV)](#2-datos-sintéticos-pdfs--csv)
3. [Repositorio de GitHub](#3-repositorio-de-github)
4. [Crear el agente en el portal de Foundry](#4-crear-el-agente-en-el-portal-de-foundry)
5. [Knowledge base (RAG) y el error de permisos](#5-knowledge-base-rag-y-el-error-de-permisos)
6. [MCP de GitHub como sistema de casos](#6-mcp-de-github-como-sistema-de-casos)
7. [Instrucciones del sistema](#7-instrucciones-del-sistema)
8. [Pruebas en el Playground](#8-pruebas-en-el-playground)
9. [Cliente de terminal con el Foundry SDK](#9-cliente-de-terminal-con-el-foundry-sdk)
10. [Web app (EXTRA)](#10-web-app-extra)
11. [Entorno local, venv y Git](#11-entorno-local-venv-y-git)
12. [Tabla de errores y soluciones](#12-tabla-de-errores-y-soluciones)
13. [Conceptos clave para estudiar](#13-conceptos-clave-para-estudiar)
14. [Preguntas típicas del profesor](#14-preguntas-típicas-del-profesor)

---

## 0. El reto

Requisitos del challenge (profesor Unai, Cloud Computing):

| Requisito | Cómo se cumple |
|---|---|
| Usar un modelo existente del Foundry Project | `gpt-5.4-mini`, ya desplegado en `foundry-tecnun-project` |
| Crear el agente en Foundry (UI o SDK) | Creado en el **portal** con el nombre `skynova-customer-care` |
| Instrucciones del sistema | `agent/system_instructions.md` (persona "Nova", modelo CARE, reglas de uso de herramientas) |
| Code Interpreter | Activado, con el CSV `skynova_operational_performance_q3_2025_2026.csv` subido |
| Integración MCP | **GitHub MCP** (Issues del repo `skynova-customer-cases` como sistema de tickets) |
| Datos propios (PDFs → índice del profesor) | 7 PDFs generados con Python e indexados por el profesor en Azure AI Search / Foundry IQ |
| Programa que habla con el agente (auth + conexión) | `app/skynova_client.py` + `app/cli.py` (terminal) |
| EXTRA: interfaz web | `app/web.py` (FastAPI) + `app/static/` (HTML/CSS/JS al estilo apple.com) |

---

## 1. Elección del escenario

Se propusieron 5 escenarios: FinOps cloud, aerolínea, onboarding de ingeniería, RRHH y banca. El criterio para elegir fue que **cada herramienta tuviera un papel claro**:

- **RAG** → datos privados e inventados que el modelo **no puede saber** por sí mismo. Así se demuestra que de verdad usa el índice.
- **Code Interpreter** → tablas numéricas sobre las que calcular o hacer gráficos.
- **MCP** → algo externo o "vivo" que no está en los PDFs.

Se eligió la **aerolínea ficticia SkyNova Airlines** (código NV, hub en Madrid), en inglés y con tono de atención al cliente profesional y educado.

---

## 2. Datos sintéticos (PDFs + CSV)

### 2.1 Qué se generó (`data/`)

| Doc | Archivo | Contenido |
|---|---|---|
| CX-01 | `SkyNova_01_Fares_and_Baggage_Policy.pdf` | Tarifas (Basic/Classic/Flex/Premium/Business), cambios, reembolsos, equipaje y tasas, plazos de check-in |
| CX-02 | `SkyNova_02_Passenger_Care_and_Compensation_Policy.pdf` | Compensación EU 261 (€250/€400/€600) por ruta, retrasos, cancelaciones, overbooking, Care Promise, equipaje perdido |
| CX-03 | `SkyNova_03_Special_Assistance_and_Travel_Needs.pdf` | Movilidad reducida, mascotas, menores no acompañados, bebés, embarazo, equipamiento deportivo |
| CX-04 | `SkyNova_04_Horizon_Loyalty_Program.pdf` | Programa de fidelización: niveles, fórmula de millas, tabla de canje, upgrades |
| OPS-05 | `SkyNova_05_Route_Network_and_Fleet_Guide.pdf` | 26 rutas, números de vuelo, horarios, flota de 44 aviones, Wi-Fi, menú, salas VIP |
| OPS-06 | `SkyNova_06_Operational_Performance_Report_Q3_2026.pdf` | KPIs, causas de retraso, rendimiento por ruta y mes, quejas |
| CX-07 | `SkyNova_07_Customer_Service_Guide_and_FAQ.pdf` | Canales de contacto, modelo CARE, FAQs, ejemplos de tono, escalado |

Además:
- `data/csv/skynova_operational_performance_q3_2025_2026.csv`: 156 filas (26 rutas × 3 meses × 2 años) para **Code Interpreter**.
- `data/test_questions.md`: preguntas de prueba con la respuesta esperada.

### 2.2 Cómo se generó (`data_generation/`)
- `skynova_data.py`: **datos maestros únicos** (rutas, distancias, flota, generador de rendimiento con semilla fija).
- `generate_pdfs.py`: construye los PDFs con **reportlab** (cabecera, tablas, pie "ficticio") y exporta el CSV.

**¿Por qué una única fuente de datos?** Para que todo sea **coherente entre documentos**: la distancia MAD–ATH (2,370 km) determina la banda de compensación (€400) en CX-02, las millas en CX-04 y la ruta en OPS-05. Si el agente cruza datos de varios PDFs, la respuesta cuadra.

Para regenerar los datos: `python data_generation/generate_pdfs.py`.

### 2.3 Fallos corregidos durante la generación
- **Números de vuelo duplicados** (NV850 aparecía dos veces) porque se usaba un índice global. Se cambió a contadores por grupo: doméstico NV3xx, MAD–Europa NV1xx, BCN–Europa NV7xx, largo radio NV6xx.
- **Recuento de destinos**: hay 26 rutas pero solo 22 destinos únicos, así que se corrigió el texto "25 destinations".
- **Redondeo de millas**: se hizo explícito "rounded down" (5,770 × 1.5 × 1.5 = 12,982).
- **Pregunta de prueba ambigua**: "coste extra" no deja claro si incluye la tarifa del bebé. Se reescribió para que lo diga.

### 2.4 Entrega
Los 7 PDFs se subieron para que **el profesor creara el índice** (Azure AI Search / Foundry IQ knowledge base `challenge4-index-kb`).

---

## 3. Repositorio de GitHub

- Repo principal: **[luis-martin-b/Challenge-Agent-Foundry](https://github.com/luis-martin-b/Challenge-Agent-Foundry)** (público).
- Repo de casos: **[luis-martin-b/skynova-customer-cases](https://github.com/luis-martin-b/skynova-customer-cases)** (privado). Ver sección 6.

Estructura:
```
├── README.md                     # Enunciado del reto + documentación
├── requirements.txt              # Dependencias de Python
├── .env.example                  # Plantilla de configuración
├── .devcontainer/                # Configuración para GitHub Codespaces
├── agent/system_instructions.md  # Instrucciones del agente
├── app/
│   ├── skynova_client.py         # Núcleo: auth, conexión, conversación, parseo
│   ├── cli.py                    # Cliente de terminal
│   ├── web.py                    # Backend web (FastAPI)
│   └── static/                   # Frontend web (index.html, styles.css, app.js)
├── data/                         # PDFs, CSV, preguntas de prueba
├── data_generation/              # Generador de datos
└── docs/                         # Esta guía + capturas
```

---

## 4. Crear el agente en el portal de Foundry

Portal: **https://ai.azure.com**, proyecto `foundry-tecnun-project`.

1. **Modelo**: en *Models + endpoints* se comprobó que estaba desplegado **`gpt-5.4-mini`**.
2. **Crear el agente**: *Agents → New agent*, con nombre **`skynova-customer-care`** y el modelo `gpt-5.4-mini`.
3. **Instrucciones**: se pegó el contenido de `agent/system_instructions.md` (ver sección 7).
4. **Code Interpreter**: *Tools → Add → Code Interpreter* y se subió el **CSV**.
   - Los archivos subidos al agente están disponibles en **todas** las conversaciones, así que los clientes no tienen que subirlos.
   - Code Interpreter **no puede leer el índice de búsqueda**. Para calcular con datos de los PDFs, el modelo primero los busca (RAG) y luego le pasa los números al código.
5. **Knowledge**: *Add → Azure AI Search / knowledge base*, eligiendo la conexión y el índice del profesor. Se añadió una **descripción**: el modelo la lee para decidir cuándo usar la herramienta.
6. **MCP de GitHub** (ver sección 6).

**Descubrimiento importante: la "Toolbox".** El portal nuevo agrupa Code Interpreter y GitHub en una **Toolbox** (`skynova-customer-care-toolbox`) que el agente consume **como un servidor MCP**. La knowledge base es **otro servidor MCP**. Por eso, en la respuesta de la API, Code Interpreter aparece como `mcp_call` y no como `code_interpreter_call`. Se descubrió inspeccionando el agente con el SDK:
```python
agent = project.agents.get(agent_name="skynova-customer-care")
agent.versions.latest.definition["tools"]   # → 2 herramientas de tipo "mcp"
```

---

## 5. Knowledge base (RAG) y el error de permisos

**Error:**
```
ErrorMcpProtocolException ... invoking tool foundryiq...: Access denied.
Check your permissions or managed identity access to the search service.
```

**Diagnóstico:** el error **no venía de GitHub**: el nombre `foundryiq...` corresponde a la knowledge base. La **identidad administrada (managed identity)** del proyecto de Foundry no tenía permisos sobre el servicio de Azure AI Search del profesor.

**Solución (la aplicó el profesor, que es el dueño del Search):**
- En el recurso de **Azure AI Search → Access control (IAM)**, asignar a la managed identity del proyecto los roles:
  - **Search Index Data Reader** (leer documentos del índice)
  - **Search Service Contributor** (necesario para las knowledge bases de Foundry IQ)
- Comprobar que *Keys → API access control* está en **RBAC** o **Both**.
- Esperar de 5 a 10 minutos a que se propaguen los permisos.

**Lección:** en Azure, los servicios se hablan entre sí con **identidades administradas + RBAC** (control de acceso basado en roles), sin claves. Si falta un rol, aparece "Access denied".

---

## 6. MCP de GitHub como sistema de casos

### 6.1 La idea (recomendación del profesor: "GitHub MCP → Repo → Issues")
Se usan los **Issues de un repo de GitHub como sistema de tickets** de atención al cliente:
- **Leer**: incidencias conocidas (label `known-incident`) y el estado de un caso (por ejemplo, el caso #3).
- **Escribir**: abrir un caso nuevo (equipaje perdido, reclamación...) con su título, descripción y labels.

Esto complementa la matriz de escalado del PDF CX-07: **el agente informa (RAG), calcula (Code Interpreter) y escala o hace seguimiento (GitHub)**.

### 6.2 Preparación del repo de casos (con `gh` CLI)
- Repo privado `skynova-customer-cases`.
- 10 labels: `complaint`, `baggage`, `compensation`, `refund`, `accessibility`, `booking`, `loyalty`, `priority-high`, `known-incident`, `created-by-agent`.
- 5 issues de ejemplo, coherentes con los PDFs:
  - #1 Incidencia conocida: error **NV-CHK-502** en la app Android 8.4.0, con workaround y fecha de arreglo (4 de noviembre)
  - #2 Incidencia conocida: huelga de control aéreo francés el 12 y 13 de noviembre, vuelos a París
  - #3 Maleta retrasada MAD–JFK (cliente Gold), con un comentario de actualización
  - #4 Reclamación de €400 por MAD–ATH (pagada y **cerrada**)
  - #5 Asistencia WCHC en MAD–MEX (prioridad alta)

### 6.3 Token de GitHub (Fine-grained PAT)
*GitHub → Settings → Developer settings → Fine-grained tokens*
- **Resource owner**: `luis-martin-b`
- **Repository access**: *Only select repositories* → `skynova-customer-cases`
- **Permissions**: **Issues: Read and write** (Metadata: read se añade solo)
- **Principio de mínimo privilegio**: el token solo puede tocar los issues de ese repo.
- El token **nunca** se pega en el chat ni en el código; va directamente al portal de Foundry.

### 6.4 Añadir el MCP en Foundry (*Tools → Add → Custom → MCP*)
| Campo | Valor |
|---|---|
| Name | `github` (en el agente final quedó como `github1`) |
| URL | `https://api.githubcopilot.com/mcp/x/issues` (`/x/issues` = solo las herramientas de issues) |
| Auth | Header `Authorization` = `Bearer <token>` |
| Approval | **Never** |

### 6.5 Problemas que aparecieron y cómo se resolvieron
| Problema | Causa | Solución |
|---|---|---|
| Pedía **aprobación** en cada llamada | Por defecto, los MCP tienen "Always require approval" | Cambiar la aprobación a **Never** |
| `search_issues: missing properties: ["query"]` | El modelo llamó a la herramienta sin su parámetro obligatorio | En las instrucciones: `query` es obligatorio, con un ejemplo |
| `Could not resolve to a Repository` | El token o la conexión enviada por Foundry no podían ver el repo privado. La prueba con `curl` daba 200, así que el token estaba bien y el fallo era la conexión | Rehacer la conexión MCP **custom** con el header correcto |
| `fields: updatedAt does not equal any of [... updated_at ...]` | El modelo usó camelCase y GitHub espera snake_case | En las instrucciones: no pasar `fields` |
| El agente dijo "no hay incidencia" sin mirar en GitHub | Solo consultó la knowledge base | Regla **obligatoria**: ante errores de la app, huelgas o incidencias, llamar a `list_issues` con `known-incident` **antes** de responder |

Prueba del token sin exponerlo (en una terminal propia):
```bash
read -s -p "Token: " T; echo; curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $T" https://api.github.com/repos/luis-martin-b/skynova-customer-cases/issues; unset T
# 200 = OK · 404 = el token no ve el repo · 401 = token inválido
```

---

## 7. Instrucciones del sistema

Archivo: `agent/system_instructions.md` (unos 7,400 caracteres). Partes:
1. **Persona**: "Nova", asistente de SkyNova.
2. **Tono con el modelo CARE**: *Connect* (saludar, usar el nombre), *Acknowledge* (empatía), *Resolve* (datos exactos de la política), *Empower* (siguiente paso). Responde en el idioma del cliente.
3. **Cuándo usar cada herramienta**:
   - Knowledge base: **siempre** para políticas, citando el documento (CX-02...).
   - Code Interpreter: cálculos y gráficos. Incluye las columnas del CSV y cómo cargarlo:
     `pd.read_csv(glob.glob('/mnt/data/*skynova_operational_performance*.csv')[0])`, porque **Foundry añade un prefijo `assistant-...-` al nombre del archivo subido**.
   - GitHub: owner y repo exactos, cuándo leer o crear casos, formato del título y del cuerpo, labels y **cómo llamar a cada herramienta** (parámetros correctos).
4. **Reglas**: no inventar, distinguir EU 261 del Care Promise, no pedir datos de tarjeta, no meter datos sensibles en los issues, no cerrar ni editar issues.

**Lección sobre prompt engineering:** cada error del agente se corrigió añadiendo una regla **concreta, con ejemplo** a las instrucciones. Además, la **descripción de cada herramienta** también influye en cuándo la usa el modelo.

> Hubo un intento de acortar las instrucciones a unos 3,400 caracteres porque el portal no dejaba guardar, pero se volvió a la versión completa.

---

## 8. Pruebas en el Playground

En `data/test_questions.md` hay prompts con la respuesta esperada. Los principales:

| Herramienta | Prompt | Esperado |
|---|---|---|
| RAG | MAD–ATH, 3h20m de retraso, falta de tripulación | **€400** (banda B; no es circunstancia extraordinaria) |
| RAG | MAD–MEX, 3h30m, fallo técnico | **€300** (banda C, retraso de 3–4 h → 50%) |
| RAG | Bulldog francés de 6 kg a Bilbao | **No** (el ATR no admite mascotas; raza braquicéfala) |
| Code Interpreter | Millas de un Gold MAD–JFK en Flex | **12,982** |
| Code Interpreter | OTP mensual de las rutas de París vs la red | Gráfico (agosto, el peor mes: red 73.1%) |
| GitHub | "Error NV-CHK-502 en la app" | Incidencia #1 con workaround |
| GitHub | "Estado del caso #3, soy Mr. Navarro" | Maleta localizada, entrega el 31 de octubre |
| GitHub | Maleta perdida en NV120 | Crea un issue nuevo con labels |

---

## 9. Cliente de terminal con el Foundry SDK

### 9.1 Librerías
- **`azure-ai-projects` 2.x** = **Microsoft Foundry SDK**
- **`azure-identity`** = autenticación con Microsoft Entra ID
- `python-dotenv` (lee `.env`), `rich` (terminal bonita)

### 9.2 Autenticación
```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
```
`DefaultAzureCredential` prueba varias fuentes en orden: variables de entorno, **managed identity** (si corre en Azure), **Azure CLI** (`az login`), VS Code... En local usa la sesión de `az login`. **No hay claves en el código.**

### 9.3 Conexión al proyecto y al agente
```python
from azure.ai.projects import AIProjectClient
project = AIProjectClient(endpoint=ENDPOINT, credential=credential)
agent = project.agents.get(agent_name="skynova-customer-care")   # comprueba que existe y que hay permisos
openai = project.get_openai_client()   # cliente OpenAI autenticado con Entra ID (scope ai.azure.com)
```
`ENDPOINT = https://foundry-tecnun-resource.services.ai.azure.com/api/projects/foundry-tecnun-project`

### 9.4 Conversación y envío de mensajes (Responses API)
```python
conv = openai.conversations.create()          # memoria multi-turno, guardada en Foundry
response = openai.responses.create(
    conversation=conv.id,
    input="Hi, who are you?",
    extra_body={"agent_reference": {"name": "skynova-customer-care", "type": "agent_reference"}},
)
print(response.output_text)
```
- `agent_reference` indica que responda **el agente** (con sus instrucciones y herramientas), no el modelo "a pelo".
- En la versión 2.x el parámetro se llama `agent_reference`; antes era `agent`. Es un *breaking change* documentado en el changelog del SDK.

### 9.5 Leer la respuesta
`response.output` es una **lista de items**:
| Tipo de item | Significado |
|---|---|
| `mcp_list_tools` | El agente lista las herramientas de cada servidor MCP |
| `reasoning` | Razonamiento interno del modelo |
| `mcp_call` | Llamada a una herramienta (knowledge base, Code Interpreter, GitHub). Incluye `server_label`, `name`, `arguments`, `output` y `error` |
| `mcp_approval_request` | Una herramienta pide aprobación (si no está en "Never") |
| `message` | El texto final, con `annotations` (citas, archivos) |

Qué hace `skynova_client.py` con todo esto:
1. **Detecta qué herramientas se usaron** (🔎 knowledge, 🐍 code, 🐙 github) a partir de `mcp_call.name`.
2. **Citas del RAG**: vienen como `url_citation`, con marcadores `【6:8†source】` en el texto. Se quitan los marcadores y se **decodifica el nombre del PDF**, que va en **base64** dentro del `chunk_id` de Azure AI Search.
3. **Gráficos**: la Toolbox devuelve dentro de `mcp_call.output` un JSON con `container_file_citations` (`container_id` + `file_id`). Se descarga cada archivo:
   ```python
   data = openai.containers.files.content.retrieve(file_id, container_id=container_id).read()
   ```
   Se guardan en `outputs/`. Code Interpreter devuelve **dos copias** (una vista previa `cfile_xxx.png` y el archivo con nombre), así que se descarta la vista previa.
4. Los enlaces `sandbox:/mnt/data/x.png` (solo válidos en el portal) se sustituyen por la ruta local.
5. **Aprobaciones**: si llega un `mcp_approval_request`, se responde automáticamente con `mcp_approval_response` (`approve: True`).

### 9.6 La interfaz de terminal (`app/cli.py`)
- Paneles con Markdown, indicador "Nova is typing...", herramientas usadas, fuentes y gráficos (que se abren solos).
- Comandos: `/new` (nueva conversación), `/help` y `/exit`.

---

## 10. Web app (EXTRA)

### 10.1 Por qué FastAPI y no Streamlit
Para conseguir el estilo de **apple.com** hace falta control total del HTML y el CSS, y Streamlit apenas deja personalizarlo. FastAPI sirve una API y archivos estáticos propios.

### 10.2 Arquitectura
```
Navegador (index.html + app.js)
   │  POST /api/chat {message, conversation_id}
   ▼
FastAPI (app/web.py)  ──►  SkyNovaAgent.ask()  (el mismo núcleo que la terminal)
   │                              │
   │                              ▼
   │                     Foundry Responses API (agent_reference)
   │                              │  knowledge base · Code Interpreter · GitHub MCP
   ▼
JSON {text, tools, sources, files} → el navegador lo pinta (Markdown + gráficos + fuentes)
```
Endpoints:
- `GET /`: la página
- `GET /api/info`: nombre del agente, versión y modelo
- `POST /api/conversation`: crea una conversación nueva
- `POST /api/chat`: envía un mensaje y devuelve la respuesta
- `/outputs/...`: sirve los gráficos descargados
- `GET /api/history`, `GET /api/history/{id}` y `DELETE /api/history/{id}`: historial de chats

**Historial de chats:** cada conversación se guarda en `history/<conversation_id>.json` (en local, ignorado por Git), con el título (el primer mensaje), las fechas y todos los mensajes (texto, herramientas, fuentes y gráficos). La barra lateral los lista y, al abrir uno, se repinta entero. Si sigues escribiendo, el agente **recuerda el contexto**, porque se reutiliza el mismo `conversation_id` de Foundry. Al borrar un chat se elimina el JSON y también la conversación en Foundry. El chat abierto se recuerda en `localStorage`, así que recargar la página no lo pierde.

Detalles:
- Un único cliente autenticado para todo el servidor, y **una conversación de Foundry por chat**.
- Los endpoints son `def` (no `async`), así que FastAPI los ejecuta en un *thread pool* y la llamada bloqueante al SDK no congela el servidor.
- Para eso se modificó el núcleo: `ask(message, conversation_id=...)`.

### 10.3 Diseño (estilo apple.com)
- Fuente del sistema (San Francisco), mucho espacio en blanco, titular grande "**SkyNova** Customer Care" con "SkyNova" en degradado azul.
- Barra lateral de historial (☰ para abrir o cerrar; en el móvil se superpone al contenido).
- Barra de navegación translúcida (`backdrop-filter: blur`), tarjetas con esquinas redondeadas y sombra suave, botones tipo píldora.
- Burbujas azules para el usuario, texto limpio para Nova, badges de herramientas y gráficos integrados (con zoom).
- **Modo oscuro** automático (`prefers-color-scheme`) y diseño **responsive** para móvil.
- Markdown con `marked` + `DOMPurify` (sanitiza el HTML para evitar XSS).

---

## 11. Entorno local, venv y Git

### 11.1 Dónde está todo
```
~/Desktop/Obsidian Master/Masters/01 Courses/01 Cloud Computing/03 Unai Azure/Challenge 4/Challenge-Agent-Foundry
```
| Elemento | ¿En GitHub? | Por qué |
|---|---|---|
| Código, PDFs, CSV, docs | ✅ | Es el proyecto |
| `.venv/` | ❌ | Entorno virtual: Python + librerías (~100 MB). Se recrea con `pip install -r requirements.txt` |
| `.env` | ❌ | Configuración personal (endpoint, nombre del agente). La plantilla es `.env.example` |
| `outputs/` | ❌ | Gráficos generados en ejecución |
| `history/` | ❌ | Historial de chats de la web (un JSON por conversación) |

### 11.2 El entorno virtual (venv)
- Es un Python privado del proyecto, con sus propias librerías en `.venv/lib/python3.13/site-packages/`.
- `source .venv/bin/activate` lo activa: el prompt muestra `(.venv)` y `python` pasa a ser el del venv.
- Sin activarlo aparece `ModuleNotFoundError: No module named 'azure'`.
- **Si se mueve la carpeta, hay que recrear el venv**, porque guarda rutas absolutas:
  `rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`

### 11.3 Git: local ↔ GitHub
- Son **dos copias**, y no se sincronizan solas.
- Si editas en github.com, en local: `git pull`.
- Si editas en local: `git add -A && git commit -m "mensaje" && git push`.
- Regla de oro: **`git pull` antes de empezar, `push` al terminar.** Si se cambian las mismas líneas en los dos sitios, hay un *merge conflict*: se resuelve a mano y no se pierde nada.

### 11.4 Montar el proyecto desde cero en otro ordenador
```bash
git clone https://github.com/luis-martin-b/Challenge-Agent-Foundry
cd Challenge-Agent-Foundry
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # y rellenar FOUNDRY_PROJECT_ENDPOINT
az login
python app/web.py           # o python app/cli.py
```

### 11.5 Alternativas sin nada en local (probadas o comentadas)
- **GitHub Codespaces**: VS Code en el navegador. Hay un `.devcontainer/` que instala Python, Azure CLI y las dependencias. La primera vez es lento (de 3 a 6 minutos).
- **Azure Cloud Shell** (shell.azure.com): terminal en el navegador, ya logueado en Azure. `git clone` + `pip install --user` + `export FOUNDRY_PROJECT_ENDPOINT=...` + `python app/cli.py`.

---

## 12. Tabla de errores y soluciones

| Error | Dónde | Causa | Solución |
|---|---|---|---|
| `Access denied ... search service` | Knowledge base | La managed identity del proyecto no tiene roles sobre AI Search | RBAC: Search Index Data Reader + Search Service Contributor |
| Pide aprobación en cada llamada | MCP | Approval = Always | Approval = **Never** |
| `missing properties: ["query"]` | GitHub `search_issues` | Faltaba el parámetro obligatorio | Regla y ejemplo en las instrucciones |
| `Could not resolve to a Repository` | GitHub | La credencial de la conexión no ve el repo privado | Revisar el token y rehacer la conexión custom con `Bearer <token>` |
| `fields ... updatedAt` | GitHub `list_issues` | camelCase en lugar de snake_case | "No pases `fields`" |
| No consulta GitHub | Agente | Solo miró la knowledge base | Regla OBLIGATORIA en las instrucciones |
| `FileNotFoundError` con el CSV | Code Interpreter | Foundry añade un prefijo al archivo | Cargarlo con `glob` |
| Instrucciones que "no se guardan" | Portal | (posible límite de longitud) | Se probó una versión corta y se volvió a la completa |
| Gráfico guardado dos veces | Cliente | Vista previa + archivo con nombre | Quedarse solo con los archivos con nombre |
| `ModuleNotFoundError: azure` | Terminal | venv sin activar | `source .venv/bin/activate` |
| `address already in use` | Web | El puerto 8000 está ocupado | `lsof -ti:8000 \| xargs kill` |

---

## 13. Conceptos clave para estudiar

- **Microsoft Foundry**: la plataforma de Azure para crear apps y agentes de IA. Un **Foundry Project** agrupa los modelos desplegados, los agentes, las conexiones y los datos.
- **Agente**: modelo + **instrucciones** + **herramientas**. Decide por sí mismo qué herramienta usar en cada turno.
- **RAG (Retrieval-Augmented Generation)**: antes de responder, el agente **busca** fragmentos relevantes en un índice (Azure AI Search / Foundry IQ) y responde basándose en ellos, con citas. Así se reducen las alucinaciones y se usan datos privados.
- **Índice / chunks**: los PDFs se dividen en fragmentos (chunks) que se indexan, con búsqueda híbrida (palabras clave + vectores) y semántica.
- **Code Interpreter**: un sandbox de Python en la nube (un "container") donde el agente ejecuta código para cálculos exactos y gráficos. Los archivos generados se descargan por `container_id` y `file_id`.
- **MCP (Model Context Protocol)**: un estándar abierto para conectar modelos con herramientas externas. El servidor MCP expone *tools* (por ejemplo, `list_issues`) y el agente las descubre (`mcp_list_tools`) y las llama (`mcp_call`).
- **Toolbox**: agrupación de herramientas en Foundry que se expone como un único endpoint MCP.
- **Microsoft Entra ID**: el sistema de identidad de Azure (antes Azure AD). **`DefaultAzureCredential`** obtiene tokens sin claves en el código.
- **Managed identity + RBAC**: los recursos de Azure tienen identidad propia y permisos por roles. Así se autentican entre servicios.
- **Fine-grained PAT**: token de GitHub con permisos mínimos y limitado a repos concretos.
- **Responses API + Conversations**: la API compatible con OpenAI que usa Foundry. `conversations` guarda el historial y `agent_reference` apunta al agente.
- **Prompt engineering**: instrucciones claras, con reglas concretas y ejemplos, más descripciones de herramientas. Cada fallo observado se convirtió en una regla.

---

## 14. Preguntas típicas del profesor

**¿Cómo se autentica tu programa?**
Con Microsoft Entra ID mediante `DefaultAzureCredential`. En local usa `az login`; desplegado usaría managed identity. No hay API keys en el código.

**¿Cómo se conecta al agente?**
`AIProjectClient(endpoint, credential)` → `get_openai_client()` → `responses.create(..., extra_body={"agent_reference": {...}})`, dentro de una conversación.

**¿Por qué GitHub como MCP?**
Hace de sistema de tickets: leer incidencias y casos, y crear casos nuevos. Aporta información "viva" que no está en los PDFs y acciones (escribir), no solo lectura.

**¿Qué diferencia hay entre RAG y Code Interpreter?**
RAG **recupera texto** del índice para fundamentar la respuesta. Code Interpreter **ejecuta código** para calcular con exactitud o generar gráficos. Se combinan: el RAG da las tarifas y Code Interpreter calcula el total.

**¿Cómo evitas que el agente se invente cosas?**
Con instrucciones ("si no está en la knowledge base, dilo y deriva al Contact Centre"), consultando siempre el RAG con citas, y con datos ficticios que solo pueden salir del índice (así se comprueba que lo usa).

**¿Qué pasaría si se filtra el token de GitHub?**
Solo da acceso a los issues de un repo de prueba (mínimo privilegio), caduca y se puede revocar en GitHub.

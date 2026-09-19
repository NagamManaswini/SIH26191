# Feature 1 — AI Disaster Management Assistant

## Overview
The AI Disaster Management Assistant is a decision-support module built inside the SIH26191 disaster application. It empowers emergency officials to query real-time database state, hazard classifications, carrying capacity metrics, evacuation detour routes, and relocation strategies.

---

## Architecture

```
Frontend (AIAssistantPage.tsx)
          │
          ▼
   POST /api/v1/assistant/chat
          │
          ▼
FastAPI Router (routers/ai_assistant.py)
          │
          ▼
Context Retriever (services/ai_assistant/context_retriever.py)
          │ (Retrieves grounded records from DB)
          ▼
AI Assistant Service (services/ai_assistant/assistant_service.py)
          │
          ├─► Rule-Based Precision Grounded Engine (Default/Fallback)
          └─► Configurable External LLM (Gemini / OpenAI API)
          │
          ▼
Response JSON { answer, sources, related_data, disclaimer }
```

---

## Database & Data Grounding
The AI Assistant retrieves verified data from:
- `HazardZone` records & ML XGBoost risk scores
- `Shelter` capacity & `ShelterResource` inventories
- `Population` & vulnerable group counts
- `RainfallRecord` stations
- `EvacuationRoute` Dijkstra paths
- `Animal` & `AnimalShelter` safety records
- `Alert` & `CommunicationMessage` broadcasts

> [!IMPORTANT]
> The assistant distinguishes between verified project data, calculated engine results, recommendations, and unavailable information. It **never invents or hallucinates disaster statistics**.

---

## REST API Specification

### Endpoint: `POST /api/v1/assistant/chat`

#### Request Body
```json
{
  "message": "Which shelters can accept people from the critical zone?"
}
```

#### Response Body
```json
{
  "answer": "Currently, there is a remaining carrying capacity of 1,495 beds across active shelters. St. Joseph Higher Secondary School Shelter has 530 spaces available, and Meppadi Relief Auditorium has 890 spaces available.",
  "sources": [
    "Shelter Database Table",
    "Carrying Capacity Assessment Engine"
  ],
  "related_data": {
    "available_shelters": [
      {
        "id": 1,
        "name": "St. Joseph Higher Secondary School Shelter",
        "available_capacity": 530
      }
    ]
  },
  "disclaimer": "AI-generated recommendations are decision-support information and should be verified by authorized disaster-management personnel."
}
```

---

## Environment Variables
Configurable in `.env`:
```env
LLM_PROVIDER=rule_based # Options: rule_based, gemini, openai
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ASSISTANT_MODEL=gemini-1.5-flash
```

---

## Implementation Status
- [x] **IMPLEMENTED**: Grounded database retrieval & precision response service
- [x] **IMPLEMENTED**: Rule-based fallback intelligence
- [x] **IMPLEMENTED**: Configurable Gemini REST API integration
- [x] **IMPLEMENTED**: Clean frontend chat interface with quick suggested questions & data references
- [ ] **FUTURE INTEGRATION**: Real-time voice speech-to-text input

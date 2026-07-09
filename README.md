# QCM App : Iktibar

Application QCM basee sur une architecture microservices Python/FastAPI.

<img width="5715" height="2508" alt="mermaid-diagram-2026-07-09-185457" src="https://github.com/user-attachments/assets/4d57fc0a-93ad-438f-b9ba-f197d8617bbb" />

Nom de l'application : **Iktibar** 

## Stockage

Le projet utilise une seule instance PostgreSQL pour les donnees metier. Chaque
microservice possede ses propres tables, organisees par schema PostgreSQL.

Les fichiers PDF/exports seront stockes dans un File Storage separe. Les
embeddings sont stockes dans FAISS.

## Auth Service

Endpoints disponibles :

```text
GET  /health
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /auth/me
```

## Frontend

Le frontend Iktibar utilise React, TypeScript, Vite et Tailwind CSS.

Vues disponibles :

```text
GET /
GET /login
GET /register
GET /dashboard
```

Le dashboard est protege par JWT. Le frontend consomme Auth Service pour :

```text
POST /auth/login
POST /auth/register
POST /auth/logout
GET  /auth/me
```


## User Service

Le User Service utilise le JWT emis par Auth Service.
Endpoints disponibles :

```text
GET   /health
GET   /users/me
PATCH /users/me
GET   /users/{auth_user_id}
GET   /users
```

## Document Service

Le Document Service gere les PDF selon le schema initial :

```text
PDF Manager
- upload PDF
- delete PDF
- list PDFs

Data Extractor
- extract text
- extract images
- extract tables si PyMuPDF le permet
- extract metadata

Cache Manager
- PDF hash
- extracted pages
- OCR status
- metadata
- knowledge indexing status
```



## Knowledge Service

Le Knowledge Service prend les pages extraites par le Document Service et gere :

```text
Semantic Chunker
- decoupage en phrases
- detection de ruptures semantiques avec MiniLM
- chunks optimises pour le contexte LLM

Embedding Service
- model: sentence-transformers/all-MiniLM-L6-v2

Vector Store
- FAISS local dans ./vector_store

Retrieval Service
- query embedding
- similarity search
- Top-K chunks pour AI Service
```


## AI Service

Le AI Service consomme le Knowledge Service et gere :

```text
LLM Provider
- classe abstraite BaseLLMProvider
- implementation concrete OpenRouter

Context Builder
- appelle Knowledge Service
- recupere les Top-K chunks
- construit le contexte source

Prompt Builder
- QCM
- Summary
- MindMap

Response Parser
- JSON
- Mermaid
- objets Python
```


## Generation Service

Le Generation Service transforme les reponses du AI Service en objets metier
modifiables :

```text
QCM Manager
- generate
- edit
- delete

QCM Settings
- number of questions
- number of options
- difficulty
- source selection : documents, pages, chunks, focus text
- source filters are sent to AI Service and enforced during Knowledge retrieval
- duplication check

Summary Generator
- sources selectionnables
- resume concis et structure
- limite de sections/tokens

MindMap Generator
- Mermaid
- JSON

Source Identifier
- document
- page
- chunk
- citation

Generation History
- AI request ids
- model
- parameters
- generated payload
- ready for Review/Learning Service
```

## Evaluation Service

Le Evaluation Service gere les feedbacks prof et les metrics

```text
Metrics
- quality score
- difficulty score
- hallucination score
- invalid questions
- invalid answers
- ambiguous questions
- weak distractors

Feedback Manager
- note globale
- question incorrecte
- reponse incorrecte
- distracteurs trop faciles
- question ambigue
- difficulte mal adaptee
- commentaire libre
- version corrigee optionnelle
- exemples valides pour learning futur

Hallucination Reports
- reason
- evidence
- status
```


## Learning Service

Le Learning Service exploite les donnees du Evaluation Service pour ameliorer les
generations futures. il construit une memoire exploitable par les prompts.

```text
Feedback Analyzer
- classify feedback
- detect recurrent issues
- quality trends

Prompt Memory
- generation rules
- teacher preferences
- prompt versions

Feedback Knowledge Base
- corrected questions
- validated examples
- MiniLM embeddings
- FAISS feedback vector store dans ./vector_store/feedback

Generation History / Strategy
- strategy scores
- evidence payloads
- donnees pretes pour injection dans AI/Generation

Integration
- Generation Service appelle /learning/prompt-context quand disponible
- les regles, preferences et exemples similaires sont injectes dans le prompt final
- l'appel est non bloquant pour garder la generation utilisable meme sans donnees learning
```


## Export Service

Le Export Service consomme les objets du Generation Service et produit des
fichiers dans le File Storage.

```text
Export PDF / DOCX
- QCM
- resumes

Export PNG
- mindmap Mermaid sous forme d'image

Export Mermaid Diagram Code
- fichier .mmd recuperable et reutilisable

```



## Lancer avec Docker

```bash
docker compose up --build
```

Frontend :

```text
http://localhost:5173
```

Auth Service :

```text
http://localhost:8001
http://localhost:8001/docs
http://localhost:8001/redoc
http://localhost:8001/openapi.json
```

User Service :

```text
http://localhost:8002
http://localhost:8002/docs
http://localhost:8002/redoc
http://localhost:8002/openapi.json
```

Document Service :

```text
http://localhost:8003
http://localhost:8003/docs
http://localhost:8003/redoc
http://localhost:8003/openapi.json
```

Knowledge Service :

```text
http://localhost:8004
http://localhost:8004/docs
http://localhost:8004/redoc
http://localhost:8004/openapi.json
```

AI Service :

```text
http://localhost:8005
http://localhost:8005/docs
http://localhost:8005/redoc
http://localhost:8005/openapi.json
```

Generation Service :

```text
http://localhost:8006
http://localhost:8006/docs
http://localhost:8006/redoc
http://localhost:8006/openapi.json
```

Evaluation Service :

```text
http://localhost:8007
http://localhost:8007/docs
http://localhost:8007/redoc
http://localhost:8007/openapi.json
```

Learning Service :

```text
http://localhost:8008
http://localhost:8008/docs
http://localhost:8008/redoc
http://localhost:8008/openapi.json
```

Export Service :

```text
http://localhost:8009
http://localhost:8009/docs
http://localhost:8009/redoc
http://localhost:8009/openapi.json
```


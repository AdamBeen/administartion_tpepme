# AdminTPE GraphRAG V1

**⚠️ AVERTISSEMENT : Cette version V1 est volontairement non sécurisée. Ne pas utiliser en production.**

Copilote interne d'instruction administrative pour les agents traitant des dossiers TPE/PME au Maroc. Le système permet à un administrateur de poser une question métier sur un dossier client/société, d'uploader des fichiers, et de recevoir une analyse structurée avec recommandation, niveau de confiance et déclenchement HITL.

## Stack technique

- **Backend** : Python 3.11+, FastAPI, LangGraph
- **LLM court** : Groq API (Llama 3.x) — classification, JSON repair, construction de requêtes
- **LLM long** : Google Gemini API — extraction de dossier, analyse administrative finale
- **Base de données** : DataStax Astra DB (Cassandra compatible)
- **Frontend** : HTML/CSS/JS vanilla (palette blanc / beige / marron)
- **Visualisation KG** : Export Obsidian (Markdown interconnecté)

## Installation

### 1. Cloner le projet et installer les dépendances

```bash
cd "Administration TPEPME"
pip install -r requirements.txt
```

### 2. Configuration

Copiez `.env.example` en `.env` et remplissez les valeurs :

```bash
cp .env.example .env
```

Variables requises :
- `ASTRA_DB_APPLICATION_TOKEN` — Token Astra DB
- `ASTRA_DB_API_ENDPOINT` — URL endpoint Astra DB
- `ASTRA_DB_KEYSPACE` — Nom du keyspace (ex: `admin_tpepme`)
- `GROQ_API_KEY` — Clé API Groq
- `GOOGLE_API_KEY` — Clé API Google Gemini

### 3. Initialiser la base de données

```bash
cd backend
python -c "from db.schema import init_schema; init_schema()"
```

### 4. Seeder le Knowledge Graph

```bash
python ingestion/seed_kg.py
```

### 5. Ingérer le document RAG vectoriel

```bash
python ingestion/ingest_rag.py
```

### 6. Exporter le Knowledge Graph vers Obsidian (optionnel)

```bash
python ingestion/export_obsidian.py
```

### 7. Lancer le backend

```bash
python main.py
```

Le backend démarre sur `http://localhost:8000`. L'interface frontend est servie sur la même URL à la racine `/`.

## Utilisation

1. Ouvrez `http://localhost:8000` dans votre navigateur
2. Saisissez votre question administrative
3. Sélectionnez le type de dossier (ou laissez "inconnu" pour classification automatique)
4. Uploadez les fichiers du dossier client (PDF, CSV, XLS, XLSX, TXT, MD)
5. Cliquez sur "Analyser le dossier"
6. Consultez les résultats : résumé, pièces manquantes, incohérences, recommandation, HITL, GraphRAG
7. Activez le mode Debug pour voir les requêtes internes et vulnérabilités

## Architecture

```
Frontend (HTML/CSS/JS)
    ↓
FastAPI Backend
    ↓
LangGraph Workflow (16 nœuds)
    ├── Extraction fichiers
    ├── Résumé dossier temporaire (Gemini)
    ├── Classification demande (Groq)
    ├── RAG vectoriel (Astra DB)
    ├── GraphRAG multi-hop (Astra DB)
    ├── Fusion contextes
    ├── Analyse LLM (Gemini)
    ├── Validation JSON (Groq repair)
    ├── HITL Router
    ├── Nettoyage réponse
    └── Persistance logs
```

## Séparation des données

> Le GraphRAG ne stocke pas les dossiers des sociétés. Il stocke uniquement la connaissance administrative structurée. Les dossiers sociétés sont fournis par l'administrateur au moment de la question et sont traités comme contexte temporaire non persistant dans le graphe métier.

## Sécurité

**Cette V1 est volontairement vulnérable.** Voir `SECURITY.md` pour la liste complète des vulnérabilités connues et la préparation Red Team.

## API Endpoints

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/health` | GET | Healthcheck (Astra + config) |
| `/api/analyze` | POST | Analyser un dossier (question + fichiers) |
| `/api/run/{run_id}` | GET | Récupérer un run précédent |
| `/api/runs` | GET | Lister les runs |
| `/api/kg/nodes` | GET | Lister les nœuds du Knowledge Graph |
| `/api/kg/edges` | GET | Lister les relations du Knowledge Graph |
| `/api/kg/export-obsidian` | POST | Exporter le KG vers Obsidian |
| `/docs` | GET | Documentation API Swagger |

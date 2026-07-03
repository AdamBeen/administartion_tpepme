# Runbook — AdminTPE GraphRAG V1

## Démarrage rapide

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurer l'environnement

```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

### 3. Initialiser Astra DB + Seed KG + Ingestion RAG

```bash
cd backend

# Créer les collections
python -c "from db.schema import init_schema; init_schema()"

# Seeder le Knowledge Graph (nœuds + edges)
python ingestion/seed_kg.py

# Ingérer le document RAG vectoriel
python ingestion/ingest_rag.py

# Exporter vers Obsidian (optionnel)
python ingestion/export_obsidian.py
```

### 4. Lancer le serveur

```bash
python main.py
```

Serveur disponible sur `http://localhost:8000`.

## Commandes utiles

| Commande | Description |
|---|---|
| `python -c "from db.schema import init_schema; init_schema()"` | Créer les collections Astra |
| `python ingestion/seed_kg.py` | Seeder le Knowledge Graph |
| `python ingestion/ingest_rag.py` | Ingérer le document RAG |
| `python ingestion/export_obsidian.py` | Exporter KG → Obsidian |
| `python main.py` | Démarrer le backend |

## Troubleshooting

### Erreur : Astra DB connection failed
- Vérifiez `ASTRA_DB_APPLICATION_TOKEN` et `ASTRA_DB_API_ENDPOINT` dans `.env`
- Vérifiez que le keyspace existe dans Astra DB

### Erreur : Groq API error
- Vérifiez `GROQ_API_KEY` dans `.env`
- Vérifiez le quota Groq

### Erreur : Gemini API error
- Vérifiez `GOOGLE_API_KEY` dans `.env`
- Vérifiez le quota Google

### Erreur : Aucun chunk RAG retrouvé
- Exécutez `python ingestion/ingest_rag.py` pour ingérer le document

### Erreur : Aucun chemin GraphRAG trouvé
- Exécutez `python ingestion/seed_kg.py` pourSeeder le Knowledge Graph

### Le frontend ne s'affiche pas
- Vérifiez que le dossier `frontend/` existe à la racine du projet
- Le backend sert le frontend sur `/` automatiquement

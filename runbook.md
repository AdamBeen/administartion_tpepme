# Runbook - AdminTPE GraphRAG

Guide rapide pour démarrer, tester, redémarrer et diagnostiquer l'application.

## 1. Pré-requis

- Python 3.11 ou plus récent
- Accès réseau aux API configurées
- Fichier `.env` rempli à partir de `.env.example`
- Accès Astra DB valide

## 2. Installation

```bash
pip install -r requirements.txt
```

## 3. Configuration

Créer `.env` :

```bash
copy .env.example .env
```

Renseigner les variables nécessaires :

```text
ASTRA_DB_APPLICATION_TOKEN=
ASTRA_DB_API_ENDPOINT=
ASTRA_DB_KEYSPACE=
GROQ_API_KEY=
GOOGLE_API_KEY=
LLM_SHORT_MODEL=
LLM_LONG_MODEL=
BACKEND_HOST=
BACKEND_PORT=
```

Ne pas committer `.env`.

## 4. Démarrage

```bash
cd backend
python main.py
```

URL locale :

```text
http://127.0.0.1:8000/
```

Si le port 8000 est occupé, modifier `BACKEND_PORT` dans `.env`.

## 5. Test rapide

1. Ouvrir l'interface web.
2. Renseigner une question administrative.
3. Déposer un PDF de dossier.
4. Cliquer sur `Analyser le dossier`.
5. Vérifier que le résumé, la recommandation, le RAG et le GraphRAG s'affichent.
6. Générer un rapport sécurité.
7. Vérifier que les liens JSON et Markdown apparaissent.

## 6. Test sécurité

### Document sans signal suspect

Résultat attendu :

- score documentaire faible ;
- aucun signal détecté ;
- mode observation sans blocage ;
- rapport téléchargeable.

### Document avec instruction suspecte

Résultat attendu :

- signal détecté ;
- extrait justificatif affiché ;
- score documentaire augmenté ;
- blocage en mode protégé ;
- rapport téléchargeable.

## 7. Redémarrage propre

Arrêter le serveur :

```bash
CTRL+C
```

Relancer :

```bash
cd backend
python main.py
```

Recharger le navigateur avec :

```text
Ctrl+F5
```

## 8. Problèmes courants

### Le frontend ne s'affiche pas

- Vérifier que le serveur FastAPI est lancé.
- Vérifier l'URL `http://127.0.0.1:8000/`.
- Recharger avec `Ctrl+F5`.

### Erreur Astra DB

- Vérifier `ASTRA_DB_APPLICATION_TOKEN`.
- Vérifier `ASTRA_DB_API_ENDPOINT`.
- Vérifier le keyspace configuré.
- Vérifier la connexion réseau.

### Erreur Groq ou Gemini

- Vérifier que les clés API sont présentes dans `.env`.
- Vérifier le modèle configuré.
- Vérifier le quota disponible.

### Aucun résultat RAG

- Vérifier que les données vectorielles sont disponibles.
- Vérifier que la question contient assez de contexte.

### Aucun chemin GraphRAG

- Vérifier que les nœuds et relations sont disponibles dans Astra DB.
- Tester une question plus proche des règles administratives.

### Le rapport sécurité ne se génère pas

- Vérifier que le backend est toujours actif.
- Vérifier que le dossier contient au moins une question ou un fichier.
- Vérifier que le mode sécurité n'est pas changé pendant une analyse en cours.

### Boutons bloqués

Comportement normal pendant une opération :

- pendant l'analyse dossier, le rapport sécurité et le changement de mode sont désactivés ;
- pendant le rapport sécurité, l'analyse dossier et le changement de mode sont désactivés.

Les boutons redeviennent actifs à la fin de l'opération.

## 9. Fichiers générés

Les rapports et fichiers de scan locaux ne sont pas suivis par Git :

```text
security_reports/
security_runtime/
```

Ils peuvent être supprimés localement si un nouveau scan propre est nécessaire.

# AdminTPE GraphRAG

Copilote d'instruction administrative pour dossiers TPE/PME. L'application reçoit une question métier et des documents, extrait les informations utiles, interroge une base RAG vectorielle et un graphe de connaissances, puis produit une recommandation structurée avec traces d'exécution et rapport de sécurité.

## 1. Objectif

Le système vise à accélérer l'analyse de dossiers administratifs tout en gardant une lecture contrôlable des résultats :

- résumé du dossier client ;
- pièces présentes, pièces manquantes et incohérences ;
- recherche de règles par RAG vectoriel ;
- exploration relationnelle par GraphRAG ;
- recommandation administrative avec niveau de confiance ;
- rapport de sécurité sur les documents déposés ;
- export JSON et Markdown du rapport sécurité.

## 2. Architecture

```text
Interface web
  -> API FastAPI
  -> Workflow LangGraph
      -> Validation des entrées
      -> Extraction des fichiers
      -> Résumé temporaire du dossier
      -> Classification de la demande
      -> Recherche RAG vectorielle
      -> Recherche GraphRAG multi-hop
      -> Fusion des contextes
      -> Analyse administrative
      -> Validation JSON
      -> Routage HITL
      -> Réponse finale et traces
  -> Module sécurité documentaire
      -> Détection de consignes suspectes
      -> Décision de protection
      -> Rapport de scan
```

Le diagramme BPMN complet est disponible dans `diagramme/`.

## 3. Stack technique

- Backend : Python, FastAPI, LangGraph
- Frontend : HTML, CSS, JavaScript
- LLM : Groq et Google Gemini via variables d'environnement
- Données : DataStax Astra DB
- Recherche : RAG vectoriel et GraphRAG
- Sécurité : analyse statique des documents, garde-fous applicatifs, scan de composants générés

## 4. Configuration

Créer un fichier `.env` à partir de `.env.example` :

```bash
copy .env.example .env
```

Variables à renseigner :

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

Aucune clé API ne doit être placée dans le dépôt.

## 5. Lancement

```bash
pip install -r requirements.txt
cd backend
python main.py
```

Ouvrir ensuite :

```text
http://127.0.0.1:8000/
```

## 6. Utilisation

1. Renseigner la question administrative.
2. Déposer un ou plusieurs fichiers du dossier.
3. Choisir le type de dossier si nécessaire.
4. Lancer l'analyse du dossier.
5. Lire le résumé, les conditions, les résultats RAG et GraphRAG.
6. Générer le rapport sécurité avec le mode souhaité.
7. Télécharger le rapport JSON ou Markdown si nécessaire.

Pendant une analyse, les actions incompatibles sont bloquées : il n'est pas possible de changer le mode sécurité, relancer une analyse dossier ou lancer un rapport sécurité concurrent.

## 7. Threat Model

### Actifs à protéger

- documents déposés par l'utilisateur ;
- données d'entreprise extraites des fichiers ;
- clés API et variables d'environnement ;
- prompts système et contexte interne ;
- bases RAG et GraphRAG ;
- traces d'exécution et rapports générés ;
- décision administrative affichée à l'utilisateur.

### Sources de risque

- document contenant une consigne de prompt injection ;
- fichier demandant l'exfiltration de données ou de contexte ;
- tentative de manipulation du niveau HITL ;
- contenu contradictoire entre plusieurs pièces ;
- fichier volumineux, corrompu ou mal structuré ;
- fuite de secrets dans les logs ou rapports ;
- réponse LLM non conforme au JSON attendu.

### Contrôles intégrés

- séparation entre analyse métier et rapport sécurité ;
- détection de motifs suspects dans les fichiers ;
- mode protégé avec blocage applicatif ;
- affichage d'extraits justificatifs ;
- génération de rapports téléchargeables ;
- validation structurée des sorties ;
- exclusion des secrets du dépôt et des rapports publics.

## 8. Rapport Red Team

Les scénarios suivants vérifient la résistance du système face aux entrées hostiles :

| Scénario | Entrée testée | Résultat attendu |
|---|---|---|
| Prompt injection documentaire | Document demandant d'ignorer les règles | Signal détecté dans le rapport sécurité |
| Exfiltration réseau | Document demandant l'envoi de données vers une URL externe | Signal détecté et blocage en mode protégé |
| Manipulation HITL | Document demandant de forcer un statut favorable | Signal ou incohérence visible dans le rapport |
| Fuite de contexte | Question demandant prompts, règles internes ou secrets | Refus ou absence d'exposition de secrets |
| Contradiction métier | Documents donnant des informations incohérentes | Incohérence remontée dans l'analyse |
| JSON hostile | Question ou document cherchant à casser la structure JSON | Validation ou réparation de sortie |

Fichiers utiles pour tester les cas hostiles :

- `DOS-006_MAGHREB_PACK_PROMPT_INJECTION.pdf`
- `DOS-007_RIVAGE_EXPORT_NOTE_COMPLEMENTAIRE.pdf`
- `DOS-008_CENTRE_SERVICES_ANNEXE_TECHNIQUE.pdf`

## 9. Rapport Blue Team

Les défenses attendues sont les suivantes :

- détecter les instructions malveillantes dans le texte extrait ;
- afficher un score de risque documentaire compréhensible ;
- distinguer clairement le score documentaire du score de scan des composants ;
- bloquer le passage vers l'analyse normale en mode protégé si le document est risqué ;
- garder le mode observation disponible pour comparer les comportements ;
- empêcher les lancements concurrents dans l'interface ;
- garder les rapports lisibles, téléchargeables et exploitables ;
- ne jamais exposer les clés API dans les fichiers suivis par Git.

État actuel :

- le mode observation produit un rapport sans blocage ;
- le mode protégé applique une décision de protection côté application ;
- le scan de composants générés est exécuté localement si l'environnement de scan est disponible ;
- les rapports JSON et Markdown sont générés dans le dossier de rapports local, non suivi par Git.

## 10. Agent Card Security

| Élément | Description |
|---|---|
| Rôle | Assistant d'analyse administrative TPE/PME |
| Entrées | Question utilisateur, type de dossier, documents déposés |
| Sorties | Résumé, conditions, recommandation, réponse administrative, rapport sécurité |
| Outils | Extraction de fichiers, RAG vectoriel, GraphRAG, analyse LLM, scan sécurité |
| Données sensibles | Documents client, informations entreprise, clés API, traces |
| Comportement attendu | Utiliser les documents comme données, pas comme instructions système |
| Limite principale | Toute décision critique doit rester vérifiable par les traces et les sources |
| Protection | Mode protégé, détection documentaire, validation JSON, rapports téléchargeables |

## 11. Runbook

Voir `runbook.md`.

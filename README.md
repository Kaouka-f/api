# Kaouka API

Backend **Flask** de l’application **Kaouka** : une API proxy qui expose les fonctionnalités sociales, géolocalisées et médias de la plateforme (publications, likes, commentaires, messagerie, feed vidéo, notifications push, etc.).

L’API écoute par défaut sur le port **8000**. Toutes les routes sont préfixées par `/proxy/`.

---

## Sommaire

- [Ce que fait ce dépôt](#ce-que-fait-ce-dépôt)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Initialiser la base de données](#initialiser-la-base-de-données)
- [Lancer l’API](#lancer-lapi)
  - [1. Mode développement — `main.py`](#1-mode-développement--mainpy)
  - [2. Mode production — Gunicorn](#2-mode-production--gunicorn)
  - [3. Docker](#3-docker)
- [Aperçu des endpoints](#aperçu-des-endpoints)
- [Déploiement avancé](#déploiement-avancé)

---

## Ce que fait ce dépôt

Kaouka API agit comme **couche serveur** entre les clients (mobile / web) et les services de données :

| Domaine | Description |
|---------|-------------|
| **Utilisateurs** | Profils, photo de profil, visibilité, connexion / déconnexion |
| **Publications (`requests`)** | Création, suppression, likes, commentaires, signalement |
| **Géolocalisation** | Recherche d’utilisateurs à proximité via Redis GEO (`getArrounds`) |
| **Messagerie** | Envoi / suppression de messages, gestion des conversations |
| **Médias** | Upload de fichiers (images, vidéos), streaming et prévisualisation (FFmpeg) |
| **Feed** | Flux de contenus vidéo servis depuis le stockage local |
| **Notifications** | Push notifications via **Firebase Admin SDK** |
| **Modération / analyse** | Outils internes (`analyzer/`) : bots, scan Redis, gestion de hash |
| **Persistance** | Schéma PostgreSQL (SQLAlchemy) pour utilisateurs, requêtes, messages, etc. |

Les données « chaudes » (sessions, géolocalisation, cache) passent par **Redis**. Les données structurées sont stockées dans **PostgreSQL**.

---

## Stack technique

- **Python 3.9+**
- **Flask** + **Flask-CORS**
- **Gunicorn** + **Gevent** (production)
- **Redis** (géolocalisation, cache, messagerie temps réel)
- **PostgreSQL** + **SQLAlchemy**
- **Firebase Admin** (notifications push)
- **FFmpeg** + **Pillow** (traitement média)

---

## Structure du projet

```
api/
├── Dockerfile              # Image Docker (Python 3.9 + FFmpeg)
├── deployment.yaml         # Manifest Kubernetes (exemple)
├── kaouka-wsgi.service     # Unit systemd pour Gunicorn
├── kaouka-proxy.service    # Unit systemd pour main.py
├── requirements.txt
└── src/
    ├── main.py             # Point d’entrée développement
    ├── proxy.py            # Application Flask, routes, objet `app` (Gunicorn)
    ├── redisIface.py       # Interface Redis
    ├── pgIface.py          # Utilitaires PostgreSQL bas niveau
    ├── utils.py            # Helpers (fichiers, emails, notifications…)
    ├── get/                # Handlers HTTP GET
    ├── post/               # Handlers HTTP POST
    ├── analyzer/           # Outils d’administration / modération
    ├── future/             # Fonctionnalités en cours (non branchées au proxy)
    └── schema/             # Modèles SQLAlchemy et scripts DB
        ├── models.py
        ├── database.py
        └── create_database.py
```

---

## Prérequis

Avant de démarrer, assurez-vous d’avoir :

1. **Python 3.9** (ou compatible avec le `Dockerfile`)
2. **Redis** accessible sur `localhost:6379`
3. **PostgreSQL** avec une base créée (voir [Initialiser la base de données](#initialiser-la-base-de-données))
4. **FFmpeg** installé sur la machine (ou via Docker)
5. Le fichier de credentials **Firebase** :
   - En dev (`MODE=test`) : `src/key/kaouka-460308906bec.json`
   - En prod / Docker : monté en `/key/kaouka-460308906bec.json`
6. Un répertoire de stockage média : **`/opt/files/`** (créez-le et donnez-lui les droits d’écriture)

---

## Installation

```bash
# Cloner le dépôt
git clone <url-du-repo> kaouka-api
cd kaouka-api

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Répertoire média (Linux / macOS)
sudo mkdir -p /opt/files/videos
sudo chown "$USER" /opt/files
```

---

## Configuration

Créez un fichier `src/.env` (non versionné) avec vos variables :

```env
# Mode "test" active le debug Flask et le chemin Firebase local (./key/)
MODE=test

# PostgreSQL — soit une URL complète :
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/kaouka_db

# Soit des variables séparées (valeurs par défaut dans database.py) :
# POSTGRES_DB=kaouka_db
# POSTGRES_USER=kaoukakeet
# POSTGRES_PASSWORD=...
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
```

| Variable | Rôle |
|----------|------|
| `MODE=test` | Debug Flask activé, credentials Firebase dans `./key/` |
| `DATABASE_URL` | URL SQLAlchemy PostgreSQL (prioritaire) |
| `POSTGRES_*` | Alternative à `DATABASE_URL` |
| `kaouka97_password` | Mot de passe SMTP pour les emails de confirmation (optionnel) |

> **Firebase** : placez le JSON de service account dans `src/key/` pour le développement local.

---

## Initialiser la base de données

Depuis la racine du dépôt, avec `src/` sur le `PYTHONPATH` :

```bash
cd src

# Créer uniquement les tables (base déjà existante)
python -m schema.create_database

# Créer la base PostgreSQL si elle n’existe pas, puis les tables
python -m schema.create_database --create-db
```

Les modèles sont définis dans `src/schema/models.py` (`users`, `requests`, `comments`, `messages`, etc.).

---

## Lancer l’API

Trois méthodes sont prévues selon le contexte (dev local, production, conteneur).

### 1. Mode développement — `main.py`

Recommandé pour le développement local : serveur Flask intégré, rechargement et logs détaillés.

```bash
cd src
export MODE=test          # optionnel mais recommandé en local
python main.py
```

L’API est disponible sur **http://0.0.0.0:8000**.

- Avec `MODE=test` : `debug=True`, credentials Firebase lus depuis `./key/`
- Sans `MODE=test` : `debug=False`, credentials Firebase lus depuis `/key/`

### 2. Mode production — Gunicorn

Recommandé en production : workers Gevent, meilleure concurrence et stabilité.

```bash
cd src

# Ne pas définir MODE=test en production
gunicorn -k gevent -w 4 -b 0.0.0.0:8000 proxy:app
```

| Option | Signification |
|--------|---------------|
| `-k gevent` | Worker async adapté aux I/O (Redis, DB, fichiers) |
| `-w 4` | 4 processus workers (ajuster selon la machine) |
| `-b 0.0.0.0:8000` | Écoute sur toutes les interfaces, port 8000 |
| `proxy:app` | Objet Flask exporté par `proxy.py` |

Un fichier d’exemple systemd est fourni : `kaouka-wsgi.service`.

> **Important** : lancer Gunicorn depuis le répertoire `src/`, car l’application s’importe via `proxy:app`.

### 3. Docker

Le `Dockerfile` embarque Python 3.9, les dépendances et FFmpeg.

**Construire l’image :**

```bash
docker build -t kaouka-api .
```

**Lancer le conteneur :**

```bash
docker run -d \
  --name kaouka-api \
  -p 8000:8000 \
  -v /chemin/vers/firebase-key:/key:ro \
  -v /chemin/vers/medias:/opt/files \
  -e DATABASE_URL="postgresql+psycopg2://user:pass@host.docker.internal:5432/kaouka_db" \
  --network host \
  kaouka-api \
  sh -c "pip install -r requirements.txt && python main.py"
```

Pour la production en conteneur, préférez Gunicorn :

```bash
docker run -d \
  --name kaouka-api \
  -p 8000:8000 \
  -v /chemin/vers/firebase-key:/key:ro \
  -v /chemin/vers/medias:/opt/files \
  -e DATABASE_URL="..." \
  kaouka-api \
  sh -c "pip install -r requirements.txt && gunicorn -k gevent -w 4 -b 0.0.0.0:8000 proxy:app"
```

**Volumes à monter :**

| Chemin conteneur | Contenu |
|------------------|---------|
| `/key/` | Fichier `kaouka-460308906bec.json` (Firebase) |
| `/opt/files/` | Médias uploadés et vidéos du feed |

> Redis et PostgreSQL doivent être accessibles depuis le conteneur (réseau Docker, `host.docker.internal`, ou `--network host`).

Un script `deploy.sh` et des manifests Kubernetes (`deployment.yaml`, `skaffold.yaml`) sont fournis pour un déploiement cluster.

---

## Aperçu des endpoints

Toutes les routes sont sous le préfixe `/proxy/`.

### GET (lecture)

| Route | Rôle |
|-------|------|
| `/proxy/getArrounds` | Utilisateurs à proximité (géolocalisation) |
| `/proxy/getFeed` | Feed vidéo |
| `/proxy/getRequest` | Détail d’une publication |
| `/proxy/getAllReqs` | Liste des publications |
| `/proxy/getOwnReqs` | Publications de l’utilisateur |
| `/proxy/getComments` | Commentaires d’une publication |
| `/proxy/getLikes` | Likes d’une publication |
| `/proxy/getMsgs` | Messages d’une conversation |
| `/proxy/getInfos` | Informations utilisateur |
| `/proxy/getGraphqlUser` | Données utilisateur (GraphQL) |
| `/proxy/isBlocked` | Vérifier si un utilisateur est bloqué |
| `/proxy/stream/<path>` | Streaming de fichiers média |
| `/proxy/preview` | Miniature / aperçu d’un média |
| `/proxy/nbUser` | Nombre d’utilisateurs connectés |

### POST (écriture)

| Route | Rôle |
|-------|------|
| `/proxy/postReq` | Créer une publication |
| `/proxy/deleteReq` | Supprimer une publication |
| `/proxy/likeReq` | Liker / unliker |
| `/proxy/postComments` | Ajouter un commentaire |
| `/proxy/sendMsg` | Envoyer un message |
| `/proxy/postPP` | Mettre à jour la photo de profil |
| `/proxy/postLocation` | Mettre à jour la position |
| `/proxy/connect` / `/proxy/onConnection` | Connexion utilisateur |
| `/proxy/onDisconnection` | Déconnexion utilisateur |
| `/proxy/blockUser` | Bloquer un utilisateur |
| `/proxy/signal_request` | Signaler une publication |

### Analyzer (administration interne)

| Route | Rôle |
|-------|------|
| `/proxy/getBots` | Lister les bots |
| `/proxy/createBot` | Créer un bot |
| `/proxy/scanRequests` | Scanner les clés Redis |
| `/proxy/hashGetAll` | Lire un hash Redis |
| `/proxy/postBotInfos` | Mettre à jour un bot |
| `/proxy/deleteHash` | Supprimer une entrée Redis |

Consultez `src/proxy.py` pour la liste exhaustive et le câblage des handlers.

---

## Déploiement avancé

| Fichier | Usage |
|---------|-------|
| `kaouka-wsgi.service` | Service systemd avec Gunicorn |
| `kaouka-proxy.service` | Service systemd avec `main.py` |
| `deployment.yaml` | Déploiement Kubernetes (NodePort 30100) |
| `volumes.yaml` | PVC pour le stockage streaming |
| `skaffold.yaml` | Build + deploy local Kubernetes |
| `deploy.sh` | Build et push de l’image Docker |

---

## Démarrage rapide (récap)

```bash
# 1. Installer
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configurer src/.env et placer la clé Firebase dans src/key/

# 3. Démarrer Redis et PostgreSQL, puis initialiser le schéma
cd src && python -m schema.create_database --create-db

# 4. Lancer (au choix)
python main.py                                          # dev
gunicorn -k gevent -w 4 -b 0.0.0.0:8000 proxy:app      # prod
docker build -t kaouka-api . && docker run -p 8000:8000 ...  # docker
```

---

## Contribuer

1. Créer une branche depuis `main`
2. Travailler dans `src/` en respectant la séparation `get/`, `post/`, `analyzer/`
3. Tester localement avec `MODE=test python main.py`
4. Ouvrir une pull request

Pour toute question sur l’architecture ou un endpoint précis, commencer par lire `src/proxy.py` puis le handler correspondant dans `src/get/` ou `src/post/`.

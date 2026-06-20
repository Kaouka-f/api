"""
Crée la base PostgreSQL (optionnel) et toutes les tables / contraintes / FK
définies dans models.py via SQLAlchemy.

Exécution (répertoire src/ sur le PYTHONPATH) :

    python -m schema.create_database
    python -m schema.create_database --create-db

Variables d’environnement : comme schema.database (DATABASE_URL ou POSTGRES_*).
"""
from __future__ import annotations

import argparse
import os
import sys

import psycopg2
from psycopg2 import sql
from sqlalchemy.engine.url import make_url

from database import Base, build_database_url, engine


def ensure_postgres_database_exists() -> None:
    """Se connecte au serveur et crée la base cible si elle n’existe pas."""
    url = make_url(build_database_url())
    if not url.drivername.startswith("postgres"):
        print("URL non PostgreSQL : --create-db ignoré.", file=sys.stderr)
        return

    db_name = url.database
    if not db_name:
        raise SystemExit("L’URL ne contient pas de nom de base de données.")

    maintenance = os.getenv("POSTGRES_MAINTENANCE_DB", "postgres")
    conn = psycopg2.connect(
        host=url.host or "localhost",
        port=url.port or 5432,
        user=url.username,
        password=url.password or "",
        dbname=maintenance,
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (db_name,),
            )
            if cur.fetchone():
                print(f"La base « {db_name} » existe déjà.")
                return
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"Base « {db_name} » créée.")
    finally:
        conn.close()


def create_schema_tables() -> None:
    """Charge les modèles et applique Base.metadata.create_all sur l’engine."""
    try:
        from schema import models  # noqa: F401
    except ModuleNotFoundError:
        import models  # type: ignore  # noqa: F401

    Base.metadata.create_all(bind=engine)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crée les tables SQLAlchemy décrites dans schema/models.py.",
    )
    parser.add_argument(
        "--create-db",
        action="store_true",
        help="Crée la base PostgreSQL sur le serveur si elle est absente "
        "(connexion à POSTGRES_MAINTENANCE_DB, défaut : postgres).",
    )
    args = parser.parse_args()

    if args.create_db:
        ensure_postgres_database_exists()

    create_schema_tables()
    names = [t.name for t in Base.metadata.sorted_tables]
    print("Tables présentes dans le schéma (create_all) :", ", ".join(names))


if __name__ == "__main__":
    main()

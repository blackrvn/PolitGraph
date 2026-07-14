#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE reader WITH LOGIN PASSWORD '${READER_PASSWORD}';
    CREATE ROLE writer WITH LOGIN PASSWORD '${WRITER_PASSWORD}';

    CREATE TABLE vector (
        vector_id  SERIAL PRIMARY KEY,
        tfidf_vector BYTEA,
        w2v_vector   BYTEA
    );

    CREATE TABLE member (
        member_id  INTEGER PRIMARY KEY,
        first_name TEXT    NOT NULL,
        last_name  TEXT    NOT NULL,
        active     BOOLEAN NOT NULL,
        party      TEXT,
        updated_at TEXT    NOT NULL,
        vector_id  INTEGER NOT NULL REFERENCES vector(vector_id)
    );

    CREATE TABLE affair (
        affair_id  INTEGER PRIMARY KEY,
        title      TEXT    NOT NULL,
        updated_at TEXT    NOT NULL,
        member_id  INTEGER NOT NULL REFERENCES member(member_id),
        vector_id  INTEGER NOT NULL REFERENCES vector(vector_id)
    );

    CREATE TABLE edge (
        edge_id          SERIAL  PRIMARY KEY,
        weight           REAL    NOT NULL,
        source_member_id INTEGER NOT NULL REFERENCES member(member_id),
        target_member_id INTEGER NOT NULL REFERENCES member(member_id)
    );

    GRANT SELECT ON ALL TABLES    IN SCHEMA public TO reader;
    GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO reader;

    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES    IN SCHEMA public TO writer;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO writer;
EOSQL

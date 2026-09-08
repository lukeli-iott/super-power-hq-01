-- Super Powers HQ — submissions schema
-- This is the existing database your project will connect to.

CREATE TABLE submissions (
  id        INTEGER PRIMARY KEY,
  hero_name TEXT,
  powers    TEXT,
  age       TEXT,
  location  TEXT,
  email     TEXT
);

CREATE TABLE member
(
  member_id INTEGER NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  active INTEGER(1) NOT NULL,
  party TEXT,
  updated_at TEXT NOT NULL,
  vector_id INTEGER NOT NULL,
  PRIMARY KEY (member_id),
  UNIQUE (member_id),
  FOREIGN KEY (vector_id) REFERENCES vector(vector_id)
);

CREATE TABLE affair
(
  affair_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  member_id INTEGER NOT NULL,
  vector_id INTEGER NOT NULL,
  PRIMARY KEY (affair_id),
  FOREIGN KEY (member_id) REFERENCES member(member_id),
  FOREIGN KEY (vector_id) REFERENCES vector(vector_id),
  UNIQUE (affair_id)
);

CREATE TABLE edge
(
  edge_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  weight INTEGER NOT NULL,
  source_member_id INTEGER NOT NULL,
  target_member_id INTEGER NOT NULL,
  FOREIGN KEY (source_member_id) REFERENCES member(member_id),
  FOREIGN KEY (target_member_id) REFERENCES member(member_id)
);

CREATE TABLE vector
(
  vector_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  tfidf_vector BLOB,
  w2v_vector BLOB
);
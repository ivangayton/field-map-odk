DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS project;
DROP TABLE IF EXISTS task;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE project (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  base_dir TEXT,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE task (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   task_number INTEGER NOT NULL,
   project_id INTEGER NOT NULL,
   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   in_progress INTEGER NOT NULL DEFAULT 0,
   task_doer INTEGER,
   last_selected TIMESTAMP,
   FOREIGN KEY (project_id) REFERENCES project (id)
   FOREIGN KEY (task_doer) REFERENCES user (id)
 );

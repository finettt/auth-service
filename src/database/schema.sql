CREATE TABLE IF NOT EXISTS "users" (
	"id" INTEGER NOT NULL UNIQUE AUTOINCREMENT,
	"login" VARCHAR UNIQUE,
	"password_hash" TEXT,
	"created_at" DATETIME,
	"last_login" DATETIME,
	PRIMARY KEY("id")
);



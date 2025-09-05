CREATE TABLE IF NOT EXISTS "users" (
	"id" INTEGER NOT NULL UNIQUE,
	"email" VARCHAR,
	"password_hash" TEXT,
	"created_at" DATETIME,
	PRIMARY KEY("id")
);



BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "texts" (
	"id"	integer,
	"name"	text,
	"desc"	text,
	"str1"	text,
	"str2"	text,
	"str3"	text,
	"str4"	text,
	"str5"	text,
	"str6"	text,
	"str7"	text,
	"str8"	text,
	"str9"	text,
	"str10"	text,
	"str11"	text,
	"str12"	text,
	"str13"	text,
	"str14"	text,
	"str15"	text,
	"str16"	text,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "datas" (
	"id"	integer DEFAULT 0,
	"ot"	integer DEFAULT 0,
	"alias"	integer DEFAULT 0,
	"setcode"	integer DEFAULT 0,
	"type"	integer DEFAULT 0,
	"atk"	integer DEFAULT 0,
	"def"	integer DEFAULT 0,
	"level"	integer DEFAULT 0,
	"race"	integer DEFAULT 0,
	"attribute"	integer DEFAULT 0,
	"category"	integer DEFAULT 0,
	"genre"	integer DEFAULT 0,
	"script"	blob,
	"support"	integer DEFAULT 0,
	"ocgdate"	integer DEFAULT 253402207200,
	"tcgdate"	integer DEFAULT 253402207200,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "setcodes" (
	"officialcode"	integer,
	"betacode"	integer,
	"name"	text UNIQUE,
	"cardid"	integer DEFAULT 0
);
COMMIT;

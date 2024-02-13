BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "ja_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "es_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "it_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "de_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "fr_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "pt_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "scripts" (
	"name"	TEXT NOT NULL DEFAULT '',
	"script"	BLOB,
	PRIMARY KEY("name")
);
CREATE TABLE IF NOT EXISTS "betaids" (
	"beta"	INTEGER NOT NULL,
	"official"	INTEGER NOT NULL,
	PRIMARY KEY("beta")
);
CREATE TABLE IF NOT EXISTS "changelog" (
	"id"	INTEGER NOT NULL,
	"wdate"	TEXT,
	"flag"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL DEFAULT '',
	"desc"	TEXT NOT NULL DEFAULT '',
	"str1"	TEXT NOT NULL DEFAULT '',
	"str2"	TEXT NOT NULL DEFAULT '',
	"str3"	TEXT NOT NULL DEFAULT '',
	"str4"	TEXT NOT NULL DEFAULT '',
	"str5"	TEXT NOT NULL DEFAULT '',
	"str6"	TEXT NOT NULL DEFAULT '',
	"str7"	TEXT NOT NULL DEFAULT '',
	"str8"	TEXT NOT NULL DEFAULT '',
	"str9"	TEXT NOT NULL DEFAULT '',
	"str10"	TEXT NOT NULL DEFAULT '',
	"str11"	TEXT NOT NULL DEFAULT '',
	"str12"	TEXT NOT NULL DEFAULT '',
	"str13"	TEXT NOT NULL DEFAULT '',
	"str14"	TEXT NOT NULL DEFAULT '',
	"str15"	TEXT NOT NULL DEFAULT '',
	"str16"	TEXT NOT NULL DEFAULT '',
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "zhcn_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "zhtw_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "th_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "ko_texts" (
	"id"	integer,
	"name"	TEXT,
	"desc"	TEXT,
	"str1"	TEXT,
	"str2"	TEXT,
	"str3"	TEXT,
	"str4"	TEXT,
	"str5"	TEXT,
	"str6"	TEXT,
	"str7"	TEXT,
	"str8"	TEXT,
	"str9"	TEXT,
	"str10"	TEXT,
	"str11"	TEXT,
	"str12"	TEXT,
	"str13"	TEXT,
	"str14"	TEXT,
	"str15"	TEXT,
	"str16"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "ar_texts" (
	"id"	integer,
	"name"	varchar(128),
	"desc"	varchar(1024),
	"str1"	varchar(256),
	"str2"	varchar(256),
	"str3"	varchar(256),
	"str4"	varchar(256),
	"str5"	varchar(256),
	"str6"	varchar(256),
	"str7"	varchar(256),
	"str8"	varchar(256),
	"str9"	varchar(256),
	"str10"	varchar(256),
	"str11"	varchar(256),
	"str12"	varchar(256),
	"str13"	varchar(256),
	"str14"	varchar(256),
	"str15"	varchar(256),
	"str16"	varchar(256),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "vi_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "koids" (
	"id"	INTEGER NOT NULL UNIQUE,
	"koid"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "banlists" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "packs" (
	"id"	INTEGER NOT NULL,
	"abbr"	TEXT,
	"name"	TEXT,
	"ocgdate"	INTEGER NOT NULL DEFAULT 253402214400,
	"tcgdate"	INTEGER NOT NULL DEFAULT 253402214400,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "datas" (
	"id"	INTEGER NOT NULL DEFAULT 0,
	"ot"	INTEGER NOT NULL DEFAULT 0,
	"alias"	INTEGER NOT NULL DEFAULT 0,
	"setcode"	INTEGER NOT NULL DEFAULT 0,
	"type"	INTEGER NOT NULL DEFAULT 0,
	"atk"	INTEGER NOT NULL DEFAULT 0,
	"def"	INTEGER NOT NULL DEFAULT 0,
	"level"	INTEGER NOT NULL DEFAULT 0,
	"race"	INTEGER NOT NULL DEFAULT 0,
	"attribute"	INTEGER NOT NULL DEFAULT 0,
	"category"	INTEGER NOT NULL DEFAULT 0,
	"genre"	INTEGER NOT NULL DEFAULT 0,
	"script"	BLOB,
	"support"	INTEGER NOT NULL DEFAULT 0,
	"ocgdate"	INTEGER NOT NULL DEFAULT 253402207200,
	"tcgdate"	INTEGER NOT NULL DEFAULT 253402207200,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "relations" (
	"cardid"	INTEGER NOT NULL,
	"packid"	INTEGER NOT NULL,
	FOREIGN KEY("cardid") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("cardid","packid")
);
CREATE TABLE IF NOT EXISTS "prices" (
	"id"	INTEGER,
	"tcgplayer"	INTEGER NOT NULL,
	"cardmarket"	INTEGER NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "rarities" (
	"id"	INTEGER,
	"tcgrarity"	INTEGER NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "skills" (
	"cardid"	INTEGER NOT NULL,
	"charid"	INTEGER NOT NULL,
	FOREIGN KEY("cardid") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("cardid" ASC,"charid")
);
CREATE TABLE IF NOT EXISTS "bandatas" (
	"id"	integer DEFAULT 1,
	"flag"	integer NOT NULL DEFAULT 0,
	"banlistid"	integer NOT NULL DEFAULT 0,
	"flagtype"	integer NOT NULL DEFAULT 0,
	"limits"	integer NOT NULL DEFAULT 0,
	"mode"	integer NOT NULL DEFAULT 0,
	"location"	integer NOT NULL DEFAULT 0,
	FOREIGN KEY("banlistid") REFERENCES "banlists"("id") ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "setcodes" (
	"officialcode"	INTEGER NOT NULL,
	"betacode"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL UNIQUE,
	"cardid"	INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "hu_texts" (
	"id"	integer NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"str1"	TEXT NOT NULL,
	"str2"	TEXT NOT NULL,
	"str3"	TEXT NOT NULL,
	"str4"	TEXT NOT NULL,
	"str5"	TEXT NOT NULL,
	"str6"	TEXT NOT NULL,
	"str7"	TEXT NOT NULL,
	"str8"	TEXT NOT NULL,
	"str9"	TEXT NOT NULL,
	"str10"	TEXT NOT NULL,
	"str11"	TEXT NOT NULL,
	"str12"	TEXT NOT NULL,
	"str13"	TEXT NOT NULL,
	"str14"	TEXT NOT NULL,
	"str15"	TEXT NOT NULL,
	"str16"	TEXT NOT NULL,
	FOREIGN KEY("id") REFERENCES "datas"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
COMMIT;

CREATE TABLE IF NOT EXISTS guilds(
    GuildID integer PRIMARY KEY,
    Prefix text DEFAULT ">"
);

CREATE TABLE IF NOT EXISTS exp(
    UserID integer PRIMARY KEY,
    XP integer DEFAULT 0,
    Level integer DEFAULT 0,
    XPlock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mutes(
    UserID integer PRIMARY KEY,
    RolesIDs text,
    Endtime text
);

CREATE TABLE IF NOT EXISTS starboard(
    RootMessageID integer PRIMARY KEY,
    StarMessageID integer,
    Stars integer DEFAULT 1
);

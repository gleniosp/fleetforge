CREATE TABLE assignments (
    assignment_id TEXT PRIMARY KEY NOT NULL,
    asset_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    authority_id TEXT NOT NULL,
    CHECK(asset_id <> device_id)
) STRICT;
CREATE TABLE identity (
    singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
    assignment_id TEXT NOT NULL REFERENCES assignments(assignment_id)
) STRICT;
PRAGMA user_version = 1;

//! Startup-only SQLite ownership: called once on the bounded blocking worker.
use crate::config::Config;
use rusqlite::{Connection, OpenFlags, params};
use std::{fs, path::Path, time::Duration};

const SQLITE_BUSY_TIMEOUT: Duration = Duration::from_millis(500);

const MIGRATION_1: &str = include_str!("../migrations/0001_identity.sql");

pub fn initialize(config: &Config) -> Result<(), String> {
    initialize_inner(config).map_err(|e| {
        format!(
            "identity store: {e}; preserve state and recover explicitly, never delete it to retry"
        )
    })
}

fn initialize_inner(config: &Config) -> Result<(), Box<dyn std::error::Error>> {
    let directory = config.state_dir.join("identity-store");
    // Exclusive directory creation arbitrates first provisioning. Its continued
    // existence prevents a lost/empty database from being silently recreated.
    let fresh = match fs::create_dir(&directory) {
        Ok(()) => {
            sync_directory(&config.state_dir)?;
            true
        }
        Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => false,
        Err(e) => return Err(e.into()),
    };
    if fs::symlink_metadata(&directory)?.file_type().is_symlink() || !directory.is_dir() {
        return Err("store must be a real directory".into());
    }
    let path = directory.join("identity.sqlite3");
    let flags = OpenFlags::SQLITE_OPEN_READ_WRITE | OpenFlags::SQLITE_OPEN_NO_MUTEX;
    if !fresh && !fs::symlink_metadata(&path)?.file_type().is_file() {
        return Err("lost database or invalid database path".into());
    }
    let mut db = Connection::open_with_flags(
        &path,
        if fresh {
            flags | OpenFlags::SQLITE_OPEN_CREATE
        } else {
            flags
        },
    )?;
    db.busy_timeout(SQLITE_BUSY_TIMEOUT)?;
    let integrity: String = db.query_row("PRAGMA quick_check", [], |row| row.get(0))?;
    if integrity != "ok" {
        return Err("corrupt database".into());
    }
    let version: i64 = db.query_row("PRAGMA user_version", [], |row| row.get(0))?;
    if !fresh && version != 1 {
        return Err("unsupported schema version or incomplete initialization".into());
    }
    configure_durability(&db)?;
    let tx = db.transaction_with_behavior(rusqlite::TransactionBehavior::Immediate)?;
    let version: i64 = tx.query_row("PRAGMA user_version", [], |row| row.get(0))?;
    match (fresh, version) {
        (true, 0) => {
            tx.execute_batch(MIGRATION_1)?;
            tx.execute(
                "INSERT INTO assignments VALUES (?1, ?2, ?3, ?4, ?5)",
                params![
                    config.assignment.assignment_id.to_string(),
                    config.asset_id.to_string(),
                    config.device_id.to_string(),
                    config.assignment.tenant_id.to_string(),
                    config.assignment.authority_id.to_string()
                ],
            )?;
            tx.execute(
                "INSERT INTO identity VALUES (1, ?1)",
                [config.assignment.assignment_id.to_string()],
            )?;
        }
        (false, 1) => {}
        _ => return Err("unsupported schema version or incomplete initialization".into()),
    }
    let stored: (String, String, String, String, String) = tx.query_row(
        "SELECT a.assignment_id, a.asset_id, a.device_id, a.tenant_id, a.authority_id
         FROM identity i JOIN assignments a USING (assignment_id) WHERE i.singleton = 1",
        [],
        |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?, r.get(4)?)),
    )?;
    let expected = (
        config.assignment.assignment_id.to_string(),
        config.asset_id.to_string(),
        config.device_id.to_string(),
        config.assignment.tenant_id.to_string(),
        config.assignment.authority_id.to_string(),
    );
    if stored != expected {
        return Err("identity/assignment mismatch".into());
    }
    if tx.prepare("PRAGMA foreign_key_check")?.exists([])? {
        return Err("invalid assignment reference".into());
    }
    tx.commit()?;
    db.close().map_err(|(_, e)| e)?;
    sync_directory(&directory)?;
    Ok(())
}

fn configure_durability(db: &Connection) -> Result<(), Box<dyn std::error::Error>> {
    db.execute_batch("PRAGMA foreign_keys = ON; PRAGMA synchronous = FULL;")?;
    let journal: String = db.query_row("PRAGMA journal_mode = WAL", [], |row| row.get(0))?;
    if journal != "wal" {
        return Err("WAL unavailable".into());
    }
    Ok(())
}

fn sync_directory(path: &Path) -> std::io::Result<()> {
    fs::File::open(path)?.sync_all()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn configured_connection_enforces_durability_settings() {
        let path = std::env::temp_dir().join(format!(
            "fleetforge-settings-{}.sqlite3",
            crate::identity::CanonicalId::generate().unwrap()
        ));
        let db = Connection::open(&path).unwrap();
        configure_durability(&db).unwrap();
        for (pragma, expected) in [("foreign_keys", 1), ("synchronous", 2)] {
            assert_eq!(
                db.pragma_query_value(None, pragma, |r| r.get::<_, i64>(0))
                    .unwrap(),
                expected
            );
        }
        assert_eq!(
            db.pragma_query_value(None, "journal_mode", |r| r.get::<_, String>(0))
                .unwrap(),
            "wal"
        );
        db.close().unwrap();
        fs::remove_file(path).unwrap();
    }

    #[test]
    fn migration_enforces_assignment_reference() {
        let path = std::env::temp_dir().join(format!(
            "fleetforge-foreign-key-{}.sqlite3",
            crate::identity::CanonicalId::generate().unwrap()
        ));
        let db = Connection::open(&path).unwrap();
        db.execute_batch("PRAGMA foreign_keys=ON").unwrap();
        db.execute_batch(MIGRATION_1).unwrap();
        let error = db
            .execute("INSERT INTO identity VALUES (1, 'missing')", [])
            .unwrap_err();
        assert_eq!(
            error.sqlite_error_code(),
            Some(rusqlite::ErrorCode::ConstraintViolation)
        );
        db.close().unwrap();
        fs::remove_file(path).unwrap();
    }

    #[test]
    fn full_disk_rolls_back_schema_and_version() {
        let path = std::env::temp_dir().join(format!(
            "fleetforge-storage-{}.sqlite3",
            crate::identity::CanonicalId::generate().unwrap()
        ));
        let mut db = Connection::open(&path).unwrap();
        db.execute_batch("PRAGMA max_page_count=1").unwrap();
        {
            let tx = db.transaction().unwrap();
            let error = tx.execute_batch(MIGRATION_1).unwrap_err();
            assert_eq!(
                error.sqlite_error_code(),
                Some(rusqlite::ErrorCode::DiskFull)
            );
        }
        assert_eq!(
            db.query_row("PRAGMA user_version", [], |r| r.get::<_, i64>(0))
                .unwrap(),
            0
        );
        assert_eq!(
            db.query_row("SELECT count(*) FROM sqlite_schema", [], |r| r
                .get::<_, i64>(0))
                .unwrap(),
            0
        );
        db.close().unwrap();
        fs::remove_file(path).unwrap();
    }
}

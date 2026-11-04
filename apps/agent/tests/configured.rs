#![cfg(unix)]
use std::io::{BufRead, BufReader};
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Duration;

struct Fixture(PathBuf);
impl Fixture {
    fn new() -> Self {
        static NEXT: AtomicU64 = AtomicU64::new(0);
        let path = std::env::temp_dir().join(format!(
            "fleetforge-identity-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        std::fs::create_dir(&path).unwrap();
        let path = path.canonicalize().unwrap();
        std::fs::create_dir(path.join("state")).unwrap();
        std::fs::create_dir(path.join("runtime")).unwrap();
        Self(path)
    }
    fn config(&self) -> String {
        format!(
            r#"asset_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
device_id = "01ARZ3NDEKTSV4RRFFQ69G5FAW"
state_dir = "{}/state"
runtime_dir = "{}/runtime"
authority_endpoint = "wss://localhost:8443/agent"
[assignment]
asset_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
device_id = "01ARZ3NDEKTSV4RRFFQ69G5FAW"
tenant_id = "01ARZ3NDEKTSV4RRFFQ69G5FAX"
authority_id = "01ARZ3NDEKTSV4RRFFQ69G5FAY"
assignment_id = "01ARZ3NDEKTSV4RRFFQ69G5FAZ"
"#,
            self.0.display(),
            self.0.display()
        )
    }
    fn write(&self, config: &str) -> PathBuf {
        let path = self.0.join("agent.toml");
        std::fs::write(&path, config).unwrap();
        path
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        std::fs::remove_dir_all(&self.0).unwrap();
    }
}
struct Agent(Child);
impl Drop for Agent {
    fn drop(&mut self) {
        let _ = self.0.kill();
        let _ = self.0.wait();
    }
}
fn bounded_output(command: &mut Command) -> std::process::Output {
    let mut agent = Agent(
        command
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap(),
    );
    let deadline = std::time::Instant::now() + Duration::from_secs(8);
    while agent.0.try_wait().unwrap().is_none() {
        assert!(
            std::time::Instant::now() < deadline,
            "agent failed to exit before deadline"
        );
        std::thread::sleep(Duration::from_millis(10));
    }
    let mut stdout = Vec::new();
    let mut stderr = Vec::new();
    use std::io::Read;
    agent
        .0
        .stdout
        .take()
        .unwrap()
        .read_to_end(&mut stdout)
        .unwrap();
    agent
        .0
        .stderr
        .take()
        .unwrap()
        .read_to_end(&mut stderr)
        .unwrap();
    std::process::Output {
        status: agent.0.wait().unwrap(),
        stdout,
        stderr,
    }
}

fn binary() -> Command {
    Command::new(env!("CARGO_BIN_EXE_fleetforge-agent"))
}

#[test]
fn provisioning_never_overwrites_existing_identity() {
    let fixture = Fixture::new();
    let path = fixture.0.join("device.id");
    assert!(
        binary()
            .arg("--new-id")
            .arg(&path)
            .status()
            .unwrap()
            .success()
    );
    let id = std::fs::read(&path).unwrap();
    assert_eq!(id.len(), 27);
    let output = binary().arg("--new-id").arg(&path).output().unwrap();
    assert!(!output.status.success());
    assert!(
        String::from_utf8(output.stderr)
            .unwrap()
            .contains("conflict")
    );
    assert_eq!(std::fs::read(&path).unwrap(), id);
}

#[test]
fn invalid_configuration_fails_without_leaking_input() {
    let fixture = Fixture::new();
    let valid = fixture.config();
    for invalid in [
        valid.replacen(
            "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "01ARZ3NDEKTSV4RRFFQ69G5FAX",
            1,
        ),
        valid.replace("01ARZ3NDEKTSV4RRFFQ69G5FAW", "01ARZ3NDEKTSV4RRFFQ69G5FAV"),
        valid.replace("wss://localhost:8443/agent", "ws://localhost/agent"),
        valid.replace("wss://localhost:8443/agent", "wss://secret@localhost/agent"),
        valid.replace("wss://localhost:8443/agent", "wss://localhost:99999/agent"),
        valid.replace("wss://localhost:8443/agent", "wss://localhost/agent#secret"),
        valid.replace("/runtime", "/state"),
        valid.replace("/runtime", "/absent"),
        valid.replace("01ARZ3NDEKTSV4RRFFQ69G5FAZ", "invalid-secret"),
        format!("secret = 'invalid-secret'\n{valid}"),
        "x".repeat(16 * 1024 + 1),
    ] {
        let output = bounded_output(binary().arg("--config").arg(fixture.write(&invalid)));
        assert!(!output.status.success(), "accepted {invalid}");
        assert!(output.stdout.is_empty());
        assert!(!String::from_utf8(output.stderr).unwrap().contains("secret"));
    }
}

#[test]
fn real_liveness_and_graceful_signals_have_fresh_instance_identity() {
    let fixture = Fixture::new();
    let path = fixture.write(&fixture.config());
    let mut instances = Vec::new();
    for signal in ["-TERM", "-INT"] {
        let mut agent = Agent(
            binary()
                .arg("--config")
                .arg(&path)
                .stderr(Stdio::piped())
                .spawn()
                .unwrap(),
        );
        let stderr = agent.0.stderr.take().unwrap();
        let (sender, receiver) = std::sync::mpsc::channel();
        let reader = std::thread::spawn(move || {
            for line in BufReader::new(stderr).lines() {
                if sender.send(line.unwrap()).is_err() {
                    break;
                }
            }
        });
        let started = receiver.recv_timeout(Duration::from_secs(10)).unwrap();
        assert!(started.contains("agent_started"), "{started}");
        assert!(started.contains("\"workload_health\":\"unknown\""));
        assert!(started.contains("\"workload_process\":\"absent\""));
        assert!(started.contains("01ARZ3NDEKTSV4RRFFQ69G5FAV"));
        instances.push(started.split("\"agent_instance\":\"").nth(1).unwrap()[..26].to_string());
        assert!(
            Command::new("kill")
                .args([signal, &agent.0.id().to_string()])
                .status()
                .unwrap()
                .success()
        );
        loop {
            let line = receiver.recv_timeout(Duration::from_secs(3)).unwrap();
            if line.contains("agent_stopped") {
                break;
            }
        }
        // The logging writer can close just before process exit.
        while receiver.recv_timeout(Duration::from_secs(3)).is_ok() {}
        let deadline = std::time::Instant::now() + Duration::from_secs(3);
        let status = loop {
            if let Some(status) = agent.0.try_wait().unwrap() {
                break status;
            }
            assert!(std::time::Instant::now() < deadline);
            std::thread::sleep(Duration::from_millis(10));
        };
        assert!(status.success());
        reader.join().unwrap();
    }
    assert_ne!(instances[0], instances[1]);
    assert_eq!(std::fs::read_to_string(path).unwrap(), fixture.config());
    assert!(
        fixture
            .0
            .join("state/identity-store/identity.sqlite3")
            .is_file()
    );
}

#[cfg(target_os = "linux")]
#[test]
fn stalled_startup_has_a_deadline() {
    let fixture = Fixture::new();
    let pipe = fixture.0.join("blocked.toml");
    assert!(
        Command::new("mkfifo")
            .arg(&pipe)
            .status()
            .unwrap()
            .success()
    );
    let started = std::time::Instant::now();
    let output = bounded_output(binary().arg("--config").arg(&pipe));
    assert_eq!(output.status.code(), Some(1));
    assert!(started.elapsed() < Duration::from_secs(8));
    assert!(
        String::from_utf8(output.stderr)
            .unwrap()
            .contains("startup exceeded")
    );
}

fn start_and_kill(fixture: &Fixture) {
    let mut agent = Agent(
        binary()
            .arg("--config")
            .arg(fixture.write(&fixture.config()))
            .stderr(Stdio::piped())
            .spawn()
            .unwrap(),
    );
    let stderr = agent.0.stderr.take().unwrap();
    let (sender, receiver) = std::sync::mpsc::channel();
    let reader = std::thread::spawn(move || {
        for line in BufReader::new(stderr).lines() {
            if sender.send(line.unwrap()).is_err() {
                break;
            }
        }
    });
    let started = receiver.recv_timeout(Duration::from_secs(10)).unwrap();
    assert!(started.contains("agent_started"), "{started}");
    agent.0.kill().unwrap();
    agent.0.wait().unwrap();
    drop(receiver);
    reader.join().unwrap();
}

#[test]
fn abrupt_restart_preserves_identity_and_rejects_every_binding_change() {
    let fixture = Fixture::new();
    start_and_kill(&fixture);
    start_and_kill(&fixture);
    let database = fixture.0.join("state/identity-store/identity.sqlite3");
    let db = rusqlite::Connection::open(&database).unwrap();
    assert_eq!(
        db.query_row("PRAGMA user_version", [], |r| r.get::<_, i64>(0))
            .unwrap(),
        1
    );
    assert_eq!(
        db.query_row("PRAGMA journal_mode", [], |r| r.get::<_, String>(0))
            .unwrap(),
        "wal"
    );
    for id in [
        "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "01ARZ3NDEKTSV4RRFFQ69G5FAW",
        "01ARZ3NDEKTSV4RRFFQ69G5FAX",
        "01ARZ3NDEKTSV4RRFFQ69G5FAY",
        "01ARZ3NDEKTSV4RRFFQ69G5FAZ",
    ] {
        let changed = fixture.config().replace(id, "01ARZ3NDEKTSV4RRFFQ69G5FB0");
        let output = bounded_output(binary().arg("--config").arg(fixture.write(&changed)));
        assert_eq!(output.status.code(), Some(1));
        assert!(String::from_utf8_lossy(&output.stderr).contains("identity/assignment mismatch"));
    }
    assert_eq!(
        db.query_row("SELECT count(*) FROM assignments", [], |r| r
            .get::<_, i64>(0))
            .unwrap(),
        1
    );
}

#[test]
fn missing_corrupt_empty_and_future_databases_are_preserved() {
    for failure in ["missing", "corrupt", "empty", "future", "lost-row"] {
        let fixture = Fixture::new();
        start_and_kill(&fixture);
        let database = fixture.0.join("state/identity-store/identity.sqlite3");
        match failure {
            "missing" => std::fs::remove_file(&database).unwrap(),
            "corrupt" => std::fs::write(&database, b"corrupt database").unwrap(),
            "empty" => std::fs::write(&database, []).unwrap(),
            "future" => rusqlite::Connection::open(&database)
                .unwrap()
                .execute_batch("PRAGMA user_version=999")
                .unwrap(),
            _ => rusqlite::Connection::open(&database)
                .unwrap()
                .execute_batch("DELETE FROM identity")
                .unwrap(),
        }
        let before = std::fs::read(&database).ok();
        let output = bounded_output(
            binary()
                .arg("--config")
                .arg(fixture.write(&fixture.config())),
        );
        assert_eq!(output.status.code(), Some(1), "{failure}");
        assert!(String::from_utf8_lossy(&output.stderr).contains("identity store"));
        assert_eq!(std::fs::read(&database).ok(), before, "{failure}");
    }
}

#[test]
fn locked_database_and_unwritable_store_fail_before_liveness() {
    let fixture = Fixture::new();
    start_and_kill(&fixture);
    let db = rusqlite::Connection::open(fixture.0.join("state/identity-store/identity.sqlite3"))
        .unwrap();
    db.execute_batch("BEGIN IMMEDIATE").unwrap();
    let started = std::time::Instant::now();
    let output = bounded_output(
        binary()
            .arg("--config")
            .arg(fixture.write(&fixture.config())),
    );
    assert_eq!(output.status.code(), Some(1));
    assert!(String::from_utf8_lossy(&output.stderr).contains("locked"));
    assert!(started.elapsed() < Duration::from_secs(3));
    db.execute_batch("ROLLBACK").unwrap();

    let fixture = Fixture::new();
    std::fs::write(fixture.0.join("state/identity-store"), b"occupied").unwrap();
    let output = bounded_output(
        binary()
            .arg("--config")
            .arg(fixture.write(&fixture.config())),
    );
    assert_eq!(output.status.code(), Some(1));
    assert_eq!(
        std::fs::read(fixture.0.join("state/identity-store")).unwrap(),
        b"occupied"
    );
}

#[test]
fn interrupted_initialization_is_not_retried_as_new_identity() {
    let fixture = Fixture::new();
    let store = fixture.0.join("state/identity-store");
    std::fs::create_dir(&store).unwrap();
    let output = bounded_output(
        binary()
            .arg("--config")
            .arg(fixture.write(&fixture.config())),
    );
    assert_eq!(output.status.code(), Some(1));
    assert!(String::from_utf8_lossy(&output.stderr).contains("identity store"));
    assert!(!store.join("identity.sqlite3").exists());
}

#[test]
fn nonregular_database_paths_are_rejected_without_following_them() {
    for kind in ["symlink", "directory", "fifo"] {
        let fixture = Fixture::new();
        let store = fixture.0.join("state/identity-store");
        std::fs::create_dir(&store).unwrap();
        let database = store.join("identity.sqlite3");
        let target = fixture.0.join("untouched");
        std::fs::write(&target, b"retain this").unwrap();
        match kind {
            "symlink" => std::os::unix::fs::symlink(&target, &database).unwrap(),
            "directory" => std::fs::create_dir(&database).unwrap(),
            _ => assert!(
                Command::new("mkfifo")
                    .arg(&database)
                    .status()
                    .unwrap()
                    .success()
            ),
        }
        let output = bounded_output(
            binary()
                .arg("--config")
                .arg(fixture.write(&fixture.config())),
        );
        assert_eq!(output.status.code(), Some(1), "{kind}");
        assert!(String::from_utf8_lossy(&output.stderr).contains("invalid database path"));
        assert_eq!(std::fs::read(&target).unwrap(), b"retain this");
    }
}

#[test]
fn unreadable_database_is_preserved() {
    use std::os::unix::fs::PermissionsExt;
    // Root bypasses ordinary Unix read permissions; this check requires an
    // unprivileged test user. Container privilege isolation belongs to #87.
    if Command::new("id").arg("-u").output().unwrap().stdout == b"0\n" {
        eprintln!("unreadable-database permission check requires a non-root test user");
        return;
    }
    let fixture = Fixture::new();
    start_and_kill(&fixture);
    let database = fixture.0.join("state/identity-store/identity.sqlite3");
    let before = std::fs::read(&database).unwrap();
    std::fs::set_permissions(&database, std::fs::Permissions::from_mode(0o0)).unwrap();
    let output = bounded_output(
        binary()
            .arg("--config")
            .arg(fixture.write(&fixture.config())),
    );
    std::fs::set_permissions(&database, std::fs::Permissions::from_mode(0o600)).unwrap();
    assert_eq!(output.status.code(), Some(1));
    let error = String::from_utf8_lossy(&output.stderr);
    assert!(error.contains("identity store"));
    assert!(!error.contains("agent_started"));
    assert_eq!(std::fs::read(database).unwrap(), before);
}

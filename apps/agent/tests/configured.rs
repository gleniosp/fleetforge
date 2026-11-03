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
        // Output closure confirms the process finished within the deadline.
        while receiver.recv_timeout(Duration::from_secs(3)).is_ok() {}
        assert!(agent.0.try_wait().unwrap().unwrap().success());
        reader.join().unwrap();
    }
    assert_ne!(instances[0], instances[1]);
    assert_eq!(std::fs::read_to_string(path).unwrap(), fixture.config());
    assert!(
        std::fs::read_dir(fixture.0.join("state"))
            .unwrap()
            .next()
            .is_none()
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

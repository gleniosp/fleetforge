use std::process::{Command, Output};

fn agent(arguments: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_fleetforge-agent"))
        .args(arguments)
        .output()
        .expect("the agent executable should start")
}

#[test]
fn no_arguments_report_compiled_version_and_platform() {
    let output = agent(&[]);

    assert_eq!(output.status.code(), Some(0));
    assert_eq!(
        String::from_utf8(output.stdout).unwrap(),
        format!(
            "fleetforge-agent {} ({}-{}; bootstrap diagnostic)\n",
            env!("CARGO_PKG_VERSION"),
            std::env::consts::ARCH,
            std::env::consts::OS,
        )
    );
    assert!(output.stderr.is_empty());
}

#[test]
fn help_describes_the_supported_interface() {
    let output = agent(&["--help"]);

    assert_eq!(output.status.code(), Some(0));
    assert_eq!(
        String::from_utf8(output.stdout).unwrap(),
        "FleetForge agent bootstrap diagnostic

Usage: fleetforge-agent [--help | --version]

With no arguments, print the compiled package version and platform.

Options:
  --help     Show this help
  --version  Show the package version\n"
    );
    assert!(output.stderr.is_empty());
}

#[test]
fn version_reports_only_the_package_name_and_version() {
    let output = agent(&["--version"]);

    assert_eq!(output.status.code(), Some(0));
    assert_eq!(
        String::from_utf8(output.stdout).unwrap(),
        format!("fleetforge-agent {}\n", env!("CARGO_PKG_VERSION"))
    );
    assert!(output.stderr.is_empty());
}

#[test]
fn unsupported_arguments_report_usage_errors() {
    for argument in ["--unknown", "start", "--help=true", "", "--"] {
        let output = agent(&[argument]);

        assert_eq!(output.status.code(), Some(2), "argument: {argument:?}");
        assert!(output.stdout.is_empty(), "argument: {argument:?}");
        assert_eq!(
            String::from_utf8(output.stderr).unwrap(),
            format!(
                "error: unexpected argument {argument:?}\n\nFor usage, run 'fleetforge-agent --help'.\n"
            )
        );
    }
}

#[test]
fn extra_arguments_fail_before_printing_success_output() {
    for (arguments, unexpected) in [
        (["--help", "--version"], "--version"),
        (["--version", "--help"], "--help"),
        (["--help", "--help"], "--help"),
        (["--version", "--version"], "--version"),
        (["--help", "start"], "start"),
        (["--version", "--unknown"], "--unknown"),
    ] {
        let output = agent(&arguments);

        assert_eq!(output.status.code(), Some(2), "arguments: {arguments:?}");
        assert!(output.stdout.is_empty(), "arguments: {arguments:?}");
        assert_eq!(
            String::from_utf8(output.stderr).unwrap(),
            format!(
                "error: unexpected argument {unexpected:?}\n\nFor usage, run 'fleetforge-agent --help'.\n"
            )
        );
    }
}

#[cfg(unix)]
#[test]
fn non_utf8_arguments_report_a_usage_error_without_panicking() {
    use std::ffi::OsStr;
    use std::os::unix::ffi::OsStrExt;

    let output = Command::new(env!("CARGO_BIN_EXE_fleetforge-agent"))
        .arg(OsStr::from_bytes(b"\xff"))
        .output()
        .expect("the agent executable should start");

    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    assert_eq!(
        String::from_utf8(output.stderr).unwrap(),
        "error: unexpected argument \"\\xFF\"\n\nFor usage, run 'fleetforge-agent --help'.\n"
    );
}

#[cfg(unix)]
#[test]
fn closed_stdout_pipe_returns_io_failure() {
    for arguments in [&[][..], &["--help"][..], &["--version"][..]] {
        let (reader, writer) = std::io::pipe().expect("a pipe should be created");
        // Close the reader before spawning so failure does not depend on timing.
        drop(reader);
        let output = Command::new(env!("CARGO_BIN_EXE_fleetforge-agent"))
            .args(arguments)
            .stdout(writer)
            .output()
            .expect("the agent executable should start");

        assert_eq!(output.status.code(), Some(1), "arguments: {arguments:?}");
        let stderr = String::from_utf8(output.stderr).unwrap();
        assert!(stderr.starts_with("Error: "), "{stderr}");
        assert!(!stderr.contains("panicked"), "{stderr}");
    }
}

#[cfg(target_os = "linux")]
#[test]
fn full_stdout_returns_io_failure() {
    for arguments in [&[][..], &["--help"][..], &["--version"][..]] {
        let full = std::fs::OpenOptions::new()
            .write(true)
            .open("/dev/full")
            .expect("Linux /dev/full should be available");
        let output = Command::new(env!("CARGO_BIN_EXE_fleetforge-agent"))
            .args(arguments)
            .stdout(full)
            .output()
            .expect("the agent executable should start");

        assert_eq!(output.status.code(), Some(1), "arguments: {arguments:?}");
        let stderr = String::from_utf8(output.stderr).unwrap();
        assert!(stderr.starts_with("Error: "), "{stderr}");
        assert!(!stderr.contains("panicked"), "{stderr}");
    }
}

#[cfg(target_os = "linux")]
#[test]
fn full_stderr_returns_io_failure() {
    let full = std::fs::OpenOptions::new()
        .write(true)
        .open("/dev/full")
        .expect("Linux /dev/full should be available");
    let output = Command::new(env!("CARGO_BIN_EXE_fleetforge-agent"))
        .arg("--unknown")
        .stderr(full)
        .output()
        .expect("the agent executable should start");

    assert_eq!(output.status.code(), Some(1));
    assert!(output.stdout.is_empty());
}

#[cfg(target_os = "linux")]
#[test]
fn failed_error_reporting_returns_io_failure() {
    let full = std::fs::OpenOptions::new()
        .write(true)
        .open("/dev/full")
        .expect("Linux /dev/full should be available");
    let output = Command::new(env!("CARGO_BIN_EXE_fleetforge-agent"))
        .arg("--help")
        .stdout(full.try_clone().expect("the file handle should be cloned"))
        .stderr(full)
        .output()
        .expect("the agent executable should start");

    assert_eq!(output.status.code(), Some(1));
}

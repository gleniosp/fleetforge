mod config;
mod identity;
mod runtime;
mod storage;

use std::ffi::OsStr;
use std::io::{self, Write};
use std::process::ExitCode;

const HELP: &str = "FleetForge agent bootstrap diagnostic

Usage: fleetforge-agent [--help | --version | --config PATH | --new-id PATH]

With no arguments, print the compiled package version and platform.

Options:
  --help     Show this help
  --version  Show the package version
  --config PATH  Run the configured agent until SIGINT/SIGTERM
  --new-id PATH  Provision one canonical ID in a new file";

enum Action {
    Diagnostic,
    Help,
    Version,
}

fn main() -> io::Result<ExitCode> {
    let mut arguments = std::env::args_os().skip(1);
    let first = arguments.next();
    if first.as_deref() == Some(OsStr::new("--config"))
        || first.as_deref() == Some(OsStr::new("--new-id"))
    {
        let Some(path) = arguments.next() else {
            return invalid_argument(OsStr::new("missing path"));
        };
        if let Some(extra) = arguments.next() {
            return invalid_argument(&extra);
        }
        let result = if first.as_deref() == Some(OsStr::new("--config")) {
            runtime::run(std::path::PathBuf::from(&path))
        } else {
            provision(std::path::Path::new(&path))
        };
        return match result {
            Ok(()) => Ok(ExitCode::SUCCESS),
            Err(message) => {
                writeln!(io::stderr().lock(), "error: {message}")?;
                Ok(ExitCode::FAILURE)
            }
        };
    }
    let action = match first {
        None => Action::Diagnostic,
        Some(argument) if argument == "--help" => Action::Help,
        Some(argument) if argument == "--version" => Action::Version,
        Some(argument) => return invalid_argument(&argument),
    };

    if let Some(argument) = arguments.next() {
        return invalid_argument(&argument);
    }

    let mut stdout = io::stdout().lock();
    match action {
        Action::Diagnostic => writeln!(
            stdout,
            "{} {} ({}-{}; bootstrap diagnostic)",
            env!("CARGO_PKG_NAME"),
            env!("CARGO_PKG_VERSION"),
            std::env::consts::ARCH,
            std::env::consts::OS,
        ),
        Action::Help => writeln!(stdout, "{HELP}"),
        Action::Version => writeln!(
            stdout,
            "{} {}",
            env!("CARGO_PKG_NAME"),
            env!("CARGO_PKG_VERSION")
        ),
    }?;
    stdout.flush()?;

    Ok(ExitCode::SUCCESS)
}

fn invalid_argument(argument: &OsStr) -> io::Result<ExitCode> {
    let mut stderr = io::stderr().lock();
    writeln!(
        stderr,
        "error: unexpected argument {argument:?}\n\nFor usage, run 'fleetforge-agent --help'."
    )?;
    stderr.flush()?;
    Ok(ExitCode::from(2))
}

fn provision(path: &std::path::Path) -> Result<(), String> {
    let id = identity::CanonicalId::generate()?;
    let mut file = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .map_err(|e| {
            if e.kind() == io::ErrorKind::AlreadyExists {
                "identity provisioning conflict: destination already exists".into()
            } else {
                format!("create identity file: {e}")
            }
        })?;
    writeln!(file, "{id}")
        .and_then(|()| file.sync_all())
        .map_err(|e| {
            format!("write identity file (preserve and inspect destination before retry): {e}")
        })
}

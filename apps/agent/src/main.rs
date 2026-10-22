use std::ffi::OsStr;
use std::io::{self, Write};
use std::process::ExitCode;

const HELP: &str = "FleetForge agent bootstrap diagnostic

Usage: fleetforge-agent [--help | --version]

With no arguments, print the compiled package version and platform.

Options:
  --help     Show this help
  --version  Show the package version";

enum Action {
    Diagnostic,
    Help,
    Version,
}

fn main()->io::Result<ExitCode>{
    let mut arguments = std::env::args_os().skip(1);
    let action = match arguments.next() {
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

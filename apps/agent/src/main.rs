fn main() {
    println!(
        "{} {} ({}-{}; bootstrap diagnostic)",
        env!("CARGO_PKG_NAME"),
        env!("CARGO_PKG_VERSION"),
        std::env::consts::ARCH,
        std::env::consts::OS,
    );
}

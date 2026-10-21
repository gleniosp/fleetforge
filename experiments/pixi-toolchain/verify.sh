#!/usr/bin/env bash
# Run inside a disposable Ubuntu 24.04 container; see the experiment report.
set -euo pipefail

export PATH=/usr/local/bin:/usr/bin:/bin
export PIXI_NO_CONFIG=true
export PIXI_NO_PROGRESS=true

for tool in rustup rustc cargo cc gcc ld prek cz; do
    if command -v "$tool"; then
        printf 'Unexpected host tool: %s\n' "$tool" >&2
        exit 1
    fi
done
test "$(command -v git)" = /usr/bin/git
git --version

work=$(mktemp -d /tmp/fleetforge-toolchain.XXXXXX)
cp /source/pixi.toml /source/pixi.lock /source/Cargo.toml /source/Cargo.lock "$work/"
mkdir -p "$work/apps"
cp -r /source/apps/agent "$work/apps/"
cd "$work"

snapshot() {
    find . -path './.pixi' -prune -o -path './target' -prune -o \
        -type f -exec sha256sum {} + | sort
}

expect_failure() {
    local pattern=$1
    shift
    snapshot > /tmp/before-failure.sha256
    if "$@" > /tmp/expected-failure.log 2>&1; then
        printf 'Unexpected success: %s\n' "$*" >&2
        exit 1
    fi
    cat /tmp/expected-failure.log
    grep -Ei "$pattern" /tmp/expected-failure.log
    snapshot > /tmp/after-failure.sha256
    cmp /tmp/before-failure.sha256 /tmp/after-failure.sha256
}

pixi --version
cat /etc/os-release
getconf GNU_LIBC_VERSION
dpkg-query -W ca-certificates
snapshot > /tmp/original.sha256
pixi install --locked --all

for environment in default dev; do
    pixi run --locked -e "$environment" bash -eu -c '
        for tool in rustc cargo rustfmt cargo-clippy; do
            path=$(command -v "$tool")
            printf "%s=%s\n" "$tool" "$path"
            case "$path" in "$CONDA_PREFIX"/bin/*) ;; *) exit 1 ;; esac
        done
        linker=$(command -v "$CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_LINKER")
        printf "linker=%s\n" "$linker"
        case "$linker" in "$CONDA_PREFIX"/bin/*) ;; *) exit 1 ;; esac
        rustc --version
        cargo --version
        rustfmt --version
        cargo clippy --version
        "$linker" --version
        if [ "$PIXI_ENVIRONMENT_NAME" = default ]; then
            ! command -v prek
            ! command -v cz
            ! command -v python
        else
            for tool in prek cz; do
                path=$(command -v "$tool")
                printf "%s=%s\n" "$tool" "$path"
                case "$path" in "$CONDA_PREFIX"/bin/*) ;; *) exit 1 ;; esac
            done
            prek --version
            cz version
        fi
        # Contributor commands use the host prerequisite, not a locked Git.
        test "$(command -v git)" = /usr/bin/git
    '
    # Distinct output trees ensure each environment compiles and links afresh.
    CARGO_TARGET_DIR="$work/target/$environment" pixi run --locked -e "$environment" \
        cargo build --workspace --locked --offline --verbose
done

pixi run --locked -e dev cargo fmt --all -- --check
pixi run --locked -e dev cargo clippy --workspace --all-targets --locked --offline -- -D warnings
pixi run --locked cargo build --workspace --release --locked --offline
output=$(pixi run --locked cargo run --locked --offline -p fleetforge-agent)
test "$output" = 'fleetforge-agent 0.1.0 (x86_64-linux; bootstrap diagnostic)'
snapshot > /tmp/validated.sha256
cmp /tmp/original.sha256 /tmp/validated.sha256

# Test drift on disposable copies only, including all source/lockfile hashes.
sed -i 's/rust = "=1.98.1"/rust = "=1.98.0"/' pixi.toml
expect_failure 'not up.to.date|out.of.date' pixi install --locked
expect_failure 'not up.to.date|out.of.date' pixi run --locked cargo build --locked
cp /source/pixi.toml pixi.toml

sed -i 's/version = "0.1.0"/version = "0.1.1"/' Cargo.toml
expect_failure 'lock.*needs to be updated|cannot update.*lock' \
    pixi run --locked cargo build --workspace --locked --offline
cp /source/Cargo.toml Cargo.toml

printf 'fn main() { unsafe {} }\n' > apps/agent/src/main.rs
expect_failure 'usage of an.*unsafe.*block' \
    pixi run --locked cargo check --workspace --locked --offline
cp /source/apps/agent/src/main.rs apps/agent/src/main.rs

snapshot > /tmp/restored.sha256
cmp /tmp/original.sha256 /tmp/restored.sha256
printf 'PASS: fresh installs, isolated tool paths, builds, lock rejection, inherited unsafe lint, source preservation\n'

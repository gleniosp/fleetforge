FROM ghcr.io/prefix-dev/pixi:0.83.0@sha256:3dce86c6e87371c58035aa41b09f2b56ca8f011722320551e0c2bfc1c59da5fb AS pixi

FROM ubuntu:24.04@sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac

# Host prerequisites; Rust and contributor checks must come from Pixi.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=pixi /usr/local/bin/pixi /usr/local/bin/pixi
COPY pixi.toml pixi.lock Cargo.toml Cargo.lock LICENSE dprint.json prek.toml .cz.toml .editorconfig .gitignore .gitattributes /source/
COPY .vscode/settings.json .vscode/extensions.json /source/.vscode/
COPY apps/agent/Cargo.toml /source/apps/agent/
COPY apps/agent/src/main.rs /source/apps/agent/src/
COPY apps/agent/tests/cli.rs /source/apps/agent/tests/
COPY experiments/pixi-toolchain/verify.sh /source/experiments/pixi-toolchain/
CMD ["bash", "/source/experiments/pixi-toolchain/verify.sh"]

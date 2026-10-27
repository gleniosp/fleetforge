FROM ghcr.io/prefix-dev/pixi:0.83.0@sha256:3dce86c6e87371c58035aa41b09f2b56ca8f011722320551e0c2bfc1c59da5fb AS pixi

FROM ubuntu:24.04@sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac

# The container supplies system trust; Python and ROS come from the release locks.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=pixi /usr/local/bin/pixi /usr/local/bin/pixi

ENV PIXI_NO_CONFIG=true
CMD ["bash", "/source/examples/ros-workloads/run-demo.sh"]

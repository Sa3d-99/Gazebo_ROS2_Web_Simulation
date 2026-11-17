ARG UBUNTU_VERSION=24.04
FROM ubuntu:${UBUNTU_VERSION}

LABEL org.opencontainers.image.title="Gazebo ROS 2 Web Simulation" \
      org.opencontainers.image.source="https://github.com/Sa3d-99/Gazebo_ROS2_Web_Simulation" \
      org.opencontainers.image.licenses="MIT"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV LANG=C.UTF-8 \
    DISPLAY_NUM=:1 \
    WEB_PORT=8080 \
    VNC_PORT=5900 \
    LOG_DIR=/workspace/gazebo-novnc-logs \
    LIBGL_ALWAYS_SOFTWARE=1 \
    GAZEBO_PREINSTALLED=1

WORKDIR /opt/gazebo-web
# Keep dependency installation cached when only the launcher changes.
COPY install.sh install-utils.sh gazebo.sh requirements.txt ./
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install -y --no-install-recommends tini curl procps \
    && bash install.sh \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip /workspace/gazebo-novnc-logs

COPY novnc.sh stop.sh LICENSE ./
COPY docker/entrypoint.sh docker/healthcheck.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.sh \
    && mkdir -p /workspace/worlds

EXPOSE 8080
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=15s --timeout=5s --start-period=90s --retries=3 \
    CMD ["/usr/local/bin/healthcheck.sh"]
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["desktop"]

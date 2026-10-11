# CH6 Part B - Break the Lock :: Linux/System Security container
# Matches Section 10.6: Debian-slim base, SSH on container port 22
# (mapped to host 2222), a single intentional sudoers misconfiguration.

FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-server sudo && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/run/sshd

# Player account. Password is set at build time (see build.sh) to the
# CREDENTIAL recovered from CH6 Part A - never hardcode it here.
ARG PLAYER_PASSWORD
RUN useradd -m -s /bin/bash player && \
    echo "player:${PLAYER_PASSWORD}" | chpasswd

# The intentionally vulnerable administrative script.
COPY logrotate_check.sh /opt/novagrid/logrotate_check.sh
RUN chmod +x /opt/novagrid/logrotate_check.sh

# Intentional misconfiguration (Section 10.6): unrestricted sudo on this one
# script, with no argument restriction -> arbitrary command execution as root
# through the script's unsanitised parameter.
COPY novagrid.sudoers /etc/sudoers.d/novagrid
RUN chmod 0440 /etc/sudoers.d/novagrid && visudo -cf /etc/sudoers.d/novagrid

# Final flag - only this flag is scored (Section 10.6: recovering the Part A
# credential alone does not award points).
ARG FLAG_VALUE
RUN echo "${FLAG_VALUE}" > /root/flag.txt && chmod 600 /root/flag.txt

# Disable password auth hardening defaults that would block our intentionally
# simple player account, but keep root login and empty passwords disabled.
RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    ssh-keygen -A

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

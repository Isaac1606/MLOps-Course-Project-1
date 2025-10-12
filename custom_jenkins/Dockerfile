# Use the Jenkins image as the base image
FROM jenkins/jenkins:lts

# Switch to root user to install dependencies
USER root

# Install prerequisites and Podman
RUN apt-get update -y && \
    apt-get install -y apt-transport-https ca-certificates curl gnupg software-properties-common podman && \
    apt-get clean

# Configure Podman for rootless operation
RUN mkdir -p /home/jenkins/.config/containers && \
    chown -R jenkins:jenkins /home/jenkins/.config

# Configure storage for Podman
RUN mkdir -p /var/lib/containers && \
    chown -R jenkins:jenkins /var/lib/containers

# Add subuid and subgid mappings for jenkins user (required for rootless Podman)
RUN echo "jenkins:100000:65536" >> /etc/subuid && \
    echo "jenkins:100000:65536" >> /etc/subgid

# Configure Podman to use the correct storage driver
RUN mkdir -p /etc/containers && \
    echo '[storage]' > /etc/containers/storage.conf && \
    echo 'driver = "overlay"' >> /etc/containers/storage.conf && \
    echo 'runroot = "/run/containers/storage"' >> /etc/containers/storage.conf && \
    echo 'graphroot = "/var/lib/containers/storage"' >> /etc/containers/storage.conf

# Create necessary directories
RUN mkdir -p /var/lib/containers/storage /run/containers/storage && \
    chown -R jenkins:jenkins /var/lib/containers /run/containers

VOLUME /var/lib/containers/storage

# Switch back to the Jenkins user
USER jenkins
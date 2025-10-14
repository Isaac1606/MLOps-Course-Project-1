FROM jenkins/jenkins:lts

USER root

RUN apt-get update -y && \
    apt-get install -y podman && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -f podman && \
    usermod -aG podman jenkins

RUN chown -R jenkins:jenkins /var/jenkins_home && \
    chmod 755 /var/jenkins_home

USER jenkins
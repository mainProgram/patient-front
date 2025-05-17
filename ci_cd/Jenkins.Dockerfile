FROM jenkins/jenkins:lts

USER root

# Installation des dépendances
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    ca-certificates \
    python3 \
    python3-pip \
    python3-venv \
    python3-full

# Installation de Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Vérification des versions
RUN node --version && npm --version

# Installation de Angular CLI globalement
RUN npm install -g @angular/cli

# Création d'un environnement virtuel Python
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installation des modules Python dans l'environnement virtuel
RUN /opt/venv/bin/pip install selenium webdriver-manager

# Revenir à l'utilisateur jenkins
USER jenkins

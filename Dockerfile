# Base Node image pour développement
FROM node:alpine AS development

# Définir le répertoire de travail
WORKDIR /usr/src/app

# Copier les fichiers nécessaires
COPY package.json package-lock.json ./

# Installer les dépendances
RUN npm install

# Copier tout le contenu dans le conteneur
COPY . .

# Exposer le port 4200 pour le mode développement
EXPOSE 4200

# Commande par défaut pour le développement
CMD ["npm", "run", "start", "--host", "0.0.0.0"]

# Stage de construction pour Production
FROM node:alpine AS build

WORKDIR /usr/src/app

COPY package.json package-lock.json ./
RUN npm install
COPY . .

RUN npm run build --prod

# Stage de production avec Nginx
FROM nginx:alpine AS production

COPY --from=build /usr/src/app/dist/patient-front/browser /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

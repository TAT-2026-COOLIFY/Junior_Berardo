# Etapa 1: Compila o Angular com as alterações novas
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Etapa 2: Configura o Nginx com o build novo e o proxy /api/
FROM nginx:alpine

# Remove a configuração padrão do Nginx e copia a sua
RUN rm -rf /usr/share/nginx/html/*
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia os arquivos compilados (funciona tanto para Angular 16- quanto Angular 17+ com pasta browser)
COPY --from=build /app/dist/ /tmp/dist/
RUN if [ -d /tmp/dist/*/browser ]; then cp -r /tmp/dist/*/browser/* /usr/share/nginx/html/; \
    elif [ -d /tmp/dist/* ]; then cp -r /tmp/dist/*/* /usr/share/nginx/html/; \
    fi && rm -rf /tmp/dist

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

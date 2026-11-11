# Etapa 1: Compilar o Angular
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build --configuration=production

# Etapa 2: Servir com Nginx
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Usa o caminho exato gerado pelo seu angular.json
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

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

# IMPORTANTE: Mude 'nome-do-seu-projeto' para o nome exato que aparece
# dentro da sua pasta dist/ quando você roda o build localmente.
# Se usar Angular 17+, pode ser necessário adicionar /browser no final
COPY --from=build /app/dist/nome-do-seu-projeto /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

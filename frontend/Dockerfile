# Dockerfile para frontend estático do eSRI
FROM nginx:alpine

# Copia todos os arquivos para o diretório padrão do Nginx
COPY . /usr/share/nginx/html

# Expõe a porta 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

FROM nginx:alpine

# Copia os arquivos estáticos para a pasta do nginx
COPY . /usr/share/nginx/html

# Expõe a porta 80 (padrão do nginx)
EXPOSE 80

# O nginx já inicia automaticamente, não precisa de CMD
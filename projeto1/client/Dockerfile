# Imagem base com o compilador GCC
FROM gcc:latest

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia todo o conteúdo da pasta local para o container
COPY . .

RUN gcc client.c -Wall -g -o client

# Define o comando que será executado ao iniciar o container
#CMD ["tail", "-f", "/dev/null"] 
CMD ["./start_client.sh"]

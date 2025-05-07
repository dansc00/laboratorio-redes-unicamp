# Imagem base com o compilador GCC
FROM gcc:latest

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia todo o conteúdo da pasta local para o container
COPY . .

RUN gcc server.c database.c sqlite3.c -o server -pthread 

# Define o comando que será executado ao iniciar o container

# Mantém o container executando para testes
CMD ["tail", "-f", "/dev/null"] 
#CMD ["./server"]

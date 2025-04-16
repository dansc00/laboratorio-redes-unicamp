# Variáveis para compilação
CC = gcc
CFLAGS = -pthread
SERVER_SRC = ./server/server.c ./server/database.c ./server/sqlite3.c
CLIENT_SRC = ./client/client.c
SERVER_OUT = ./server/server
CLIENT_OUT = ./client/client

# Alvo principal: compila servidor e cliente
.PHONY: all
all: build-server build-client

# Compila o servidor
.PHONY: build-server
build-server:
	@echo "Compilando servidor..."
	$(CC) $(SERVER_SRC) $(CFLAGS) -o $(SERVER_OUT)

# Compila o cliente
.PHONY: build-client
build-client:
	@echo "Compilando cliente..."
	$(CC) $(CLIENT_SRC) $(CFLAGS) -o $(CLIENT_OUT)

# Limpa os binários
.PHONY: clean
clean:
	@echo "Limpando arquivos de saída..."
	rm -f $(SERVER_OUT) $(CLIENT_OUT)

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>
#include <netinet/in.h>
#include <string.h>

int main(int argc, char **argv)
{

    // descritor de arquivo: inteiro que referencia um recurso aberto para o kernel
    int sock, new_sock; // descritores de arquivo para processo pai e filho
    pid_t child_pid; // pid do processo filho

    // socklen_t: inteiro de pelo menos 32 bits, utilizado para manter um padrão de tamanho, independente da arquitetura do sistema. Garante portabilidade e atendimento do padrão posix
    socklen_t client_len; // armazena tamanho em bytes de estruturas de endereço socket

    struct sockaddr_in client_addr, server_addr; // estrutura que armazena parâmetros para criação de socket

    // cria socket TCP, usando IPv4 e protocolo padrão
    sock = socket(PF_INET, SOCK_STREAM, 0);
    if(sock == -1){
        perror("Falha ao criar o socket");
        exit(EXIT_FAILURE);
    }

    memset(&server_addr, 0, sizeof(server_addr)); // zera bloco de memória, evita bugs ao utilizar bind(), connect() 

    
}
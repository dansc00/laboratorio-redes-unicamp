#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>
#include <netinet/in.h>
#include <string.h>
#include <arpa/inet.h>
#include <errno.h>

#define SERV_PORT 8080 // porta de escuta do servidor
#define BACKLOG 5 // número de conexões que podem aguardar na fila de espera
#define MAX_PAYLOAD 1024 // tamanho máximo do payload

/*
estruturas, tipos e constantes definidas em <netinet/in.h>

INADDR_ANY; possui valor 0x00000000, usado para referir todas interfaces de rede 0.0.0.0

in_port_t; equivalente ao tipo uint16_t (16 bits unsigned int)

in_addr_t; equivalente ao tipo uint32_t (32 bits unsigned int)

struct in_addr{

    in_addr_t s_addr; representa o IP
}

struct sockaddr_in{

    sa_family_t sin_family; familia de endereçamento IP (unsigned int) 
    in_port_t sin_port; número de porta
    struct in_addr sin_addr; endereço ip
}
*/

// envia todos os bytes necessários repetindo write
ssize_t write_all(int file_descriptor, void *ptr_buffer, size_t n){

    size_t n_left = n; // bytes restantes para envio
    const char *ptr = ptr_buffer; // ponteiro char aponta para o buffer, se utiliza char que possui tamanho de 1 byte para manipulação de byte por byte
    ssize_t n_written; // bytes enviados

    while(n_left > 0){
        // função de escrita, retorna quantidade de bytes escritos (pode n enviar todos de uma vez), 0 (raro) ou -1 caso ocorra um erro
        n_written = write(file_descriptor, ptr, n_left);
        if(n_written <= 0){
            if(n_written < 0 && errno == EINTR) // falha por interrupção
                n_written = 0; // reinicia
            else
                return -1; // falha real
        }
        n_left -= n_written;
        ptr += n_written;
    }
    return n;
}

// processa mensagem recebida e escreve echo
void server_echo(int new_sock)
{
    ssize_t n; // bytes lidos em dados recebidos, ssize_t é usado para contagem de bytes ou indicação de erro
    char buffer[MAX_PAYLOAD]; // buffer armazena dados recebidos

again:
    // função de leitura, retorna número de bytes lidos em caso de sucesso, 0 em caso de fim de arquivo (EOF) e número negativo caso haja erro
    n = read(new_sock, buffer, MAX_PAYLOAD); 
    while(n > 0)
        write_all(new_sock, buffer, n);
    
    if(n < 0 && errno == EINTR) // repete caso erro por interrupção
        goto again;
    else if(n < 0)
        perror("Erro de leitura");
}

int main(int argc, char **argv){
    // descritor de arquivo: inteiro que referencia um recurso aberto para o kernel
    int sock, new_sock; // descritores de arquivo para processo pai e filho
    pid_t child_pid; // pid do processo filho

    // socklen_t: inteiro de pelo menos 32 bits, utilizado para manter um padrão de tamanho, independente da arquitetura do sistema. Garante portabilidade e atendimento do padrão posix
    socklen_t client_len; // armazena tamanho em bytes de estruturas de endereço socket

    struct sockaddr_in client_addr, server_addr; // estrutura que armazena parâmetros para criação de socket

    // cria socket TCP, usando IPv4 e protocolo padrão
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if(sock == -1){
        perror("Falha ao criar o socket");
        exit(EXIT_FAILURE);
    }

    memset(&server_addr, 0, sizeof(server_addr)); // zera bloco de memória, evita bugs ao utilizar bind(), connect() 

    server_addr.sin_family = AF_INET; // define familia de endereçamento IPv4
    // htonl(); funções htonx(host to network x) convertem ordem de bytes x do host para a ordem de bytes da rede
    // ex: host usa little-endian e rede usa big-endian (ordem padrão na rede)
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY); // endereço de escuta do servidor. 0.0.0.0 escuta em todas as interfaces
    server_addr.sin_port = htons(SERV_PORT); // porta do servidor

    bind(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)); // associa socket ao endereço
    listen(sock, BACKLOG); // coloca o socket em modo de escuta

    while(1){
        client_len = sizeof(client_addr); // tamanho da struct de endereço do cliente
        new_sock = accept(sock, (struct sockaddr*)&client_addr, &client_len); // gera socket com nova conexão, preenche endereço com IP e porta do cliente
        
        child_pid = fork(); // realiza fork do servidor
        if(child_pid == 0){ // processo filho
            close(sock); // fecha socket do servidor pai no filho
            server_echo(new_sock);
            exit(EXIT_SUCCESS);
        }
        close(new_sock);  // fecha socket do filho, no filho e no pai
    }
}
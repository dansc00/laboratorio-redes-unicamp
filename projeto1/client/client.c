#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h> // funções de socket
#include <unistd.h> // read(), write(), close() ...
#include <netinet/in.h> // sockaddr_in, htons(), INADDR_ANY ...
#include <string.h>
#include <arpa/inet.h> // conversões de IP como inet_pton()
#include <errno.h>
#include <pthread.h> // threads

#define SERVER_PORT 8080 // porta de escuta do servidor
#define MAX_PAYLOAD 1024 // tamanho máximo do payload
#define MAX_CLIENTS 20 // número máximo de clientes (threads)
#define MAX_OPS 7 // número máximo de operações 

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

// estrutura de cliente passada para função de thread
typedef struct Client{

    int id; // id de cliente
    int op; // operação a ser realizada no servidor
    int sock; 
    struct sockaddr *server_addr; 
    socklen_t server_len;

} client;

// lê um caractere por vez do socket até encontrar \n ou EOF, retorna número de bytes lidos, 0 se EOF ou -1 se houver erro
ssize_t read_line(int file_descriptor, void *ptr_buffer, size_t max_len) {

    ssize_t n; // número total de bytes lidos
    ssize_t rc; // retorno de read (bytes lidos)
    char c; // caractere lido do socket
    char *ptr; // caminha no buffer

    ptr = ptr_buffer;
    for(n = 1; n < max_len; n++) {

        if((rc = read(file_descriptor, &c, 1)) == 1) { // byte lido
            *ptr= c; // adiciona caractere
            ptr++; // passa para a próxima posição

            if(c == '\n')
                break;  // fim da linha
        } 
        else if(rc == 0) {

            if(n == 1)
                return 0;  // EOF, nada lido
            else
                break;     // EOF, retornando dados lidos
        } 
        else{
            if(errno == EINTR) // sinal de interrupção de função
                continue;  // tenta novamente
            
            // falha real
            perror("Falha de escrita");
            return -1;             
        }
    }

    *ptr = 0;  // \0 termina a string
    return n;
}

// envia todos os bytes necessários repetindo write, retorna número de bytes escritos
ssize_t write_all(int file_descriptor, void *ptr_buffer, size_t n){

    size_t n_left = n; // bytes restantes para envio
    const char *ptr = ptr_buffer; // ponteiro char aponta para o buffer, se utiliza char que possui tamanho de 1 byte para manipulação de byte por byte
    ssize_t n_written; // bytes enviados

    while(n_left > 0){
        // função de escrita, retorna quantidade de bytes escritos (pode n enviar todos de uma vez), 0 (raro) ou -1 caso ocorra um erro
        n_written = write(file_descriptor, ptr, n_left);
        if(n_written <= 0){

            if(n_written < 0 && errno == EINTR) // sinal de interrupção de função
                n_written = 0; // reinicia
            else{
                perror("Falha de leitura"); // falha real
                return 0;
            } 
        }
        n_left -= n_written;
        ptr += n_written;
    }
    return n;
}

// recebe arquivo de entrada (stdin), retorna e envia ao servidor
void client_echo(FILE *fp, int sock){

    char send_buffer[MAX_PAYLOAD]; //  buffer de envio de dados
    char recv_buffer[MAX_PAYLOAD]; // buffer de recebimento de dados
    
    // lê linhas do arquivo e armazena no buffer de envio
    while(fgets(send_buffer, MAX_PAYLOAD, fp) != NULL){
        write_all(sock, send_buffer, strlen(send_buffer)); // escreve no servidor
        
        if(read_line(sock, recv_buffer, MAX_PAYLOAD) == 0){
            perror("O servidor encerrou a conexão prematuramente");
            exit(EXIT_FAILURE);
        }

        fputs(recv_buffer, stdout);
    }
}

// inicializa cliente
client* initialize_client(int id, int sock, struct sockaddr* server_addr, socklen_t server_len){

    client *new_client = malloc(sizeof(client));
    new_client->id = id;
    new_client->op = 1 + rand() % MAX_OPS;
    new_client->sock = sock;
    new_client->server_addr = server_addr;
    new_client->server_len = server_len;

    return new_client;
}

// conecta thread ao servidor
void* connect_thread(void *thread){

    client *c = (client*)thread;
    
    if(connect(c->sock, c->server_addr, c->server_len) >= 0){
        switch(c->op){

            char *request[MAX_PAYLOAD];

            case 1: // cadastrar filme
                
            break;

            case 2: // alterar gênero

            break;

            case 3: // 
            break;

            case 4:
            break;

            case 5:
            break;

            case 6:
            break;

            case 7:
            break;
        };
        exit(EXIT_SUCCESS);
    }
    else{
        perror("Erro ao tentar conexão com servidor");
        free(c);
        exit(EXIT_FAILURE);
    }
}

void print_log(int sock, int i, int op){
    printf("Cliente %d conectado via socket %d solicita operação %d no banco\n", i, sock);
}

int main(int argc, char **argv){

    int sock;
    struct sockaddr_in server_addr; 

    if(argc != 2){ // IP do servidor não foi passado por linha de comando
        perror("IP do servidor não especificado");
        exit(EXIT_FAILURE);
    }

    // CONFIGURAÇÃO DE SERVIDOR
    // zera bloco de memória, evita bugs ao utilizar bind(), connect() 
    memset(&server_addr, 0, sizeof(server_addr));

    server_addr.sin_family = AF_INET; //IPv4
    // htonx(); funções htonx(host to network x) convertem ordem de bytes x do host para a ordem de bytes da rede
    // ex: host usa little-endian e rede usa big-endian (ordem padrão na rede)
    server_addr.sin_port = htons(SERVER_PORT);
    // converte IP passado de string para formato binário e armazena no campo correto da struct
    inet_pton(AF_INET, argv[1], &server_addr.sin_addr);
    
    // CONFIGURAÇÃO DE THREADS CLIENTE
    srand(time(NULL)); // seed para gerador de pseudo-aleatórios, garante sequência diferente a cada execução
    int num_clients = 1 + rand() % MAX_CLIENTS; // gera número aleatório de cliente (mínimo de 1)
    pthread_t *clients = malloc(num_clients * sizeof(pthread_t)); // armazena clientes como IDs de thread

    for(int i = 0; i < num_clients; i++){
        sock = socket(AF_INET, SOCK_STREAM, 0); // cria socket TCP, usando IPv4 e protocolo padrão
        client *new_client = initialize_client(i, sock, (struct sockaddr*)&server_addr, sizeof(server_addr));
        pthread_create(&clients[i], NULL, connect_thread, (void*)new_client);
        print_log(sock, i, new_client->op);
    }

    for(int i = 0; i < num_clients; i++){
        pthread_join(clients[i], NULL);
    }

    free(clients);
    //client_echo(stdin, sock);
    return 0;
}
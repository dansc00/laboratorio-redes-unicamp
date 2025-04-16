#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h> // funções de socket
#include <unistd.h> // read(), write(), close() ...
#include <netinet/in.h> // sockaddr_in, htons(), INADDR_ANY ...
#include <string.h>
#include <arpa/inet.h> // conversões de IP como inet_pton()
#include <errno.h>
#include <ctype.h> // touper()
#include <pthread.h> // threads

#define SERVER_PORT 8080 // porta de escuta do servidor
#define MAX_PAYLOAD 1024 // tamanho máximo do payload
#define MAX_OPS 7 // número máximo de operações
#define MAX_CLIENTS 5 // número máximo de clientes (threads) 

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

    // argumentos de conexão
    int sock; 
    struct sockaddr *server_addr; 
    socklen_t server_len;

} client;

// lê um caractere por vez do buffer até encontrar \0, retorna número de bytes lidos, 0 se EOF ou -1 se houver erro
ssize_t read_all(int file_descriptor, void *ptr_buffer, size_t max_len) {

    ssize_t n; // número total de bytes lidos
    ssize_t rc; // retorno de cada chamada ao read()
    char c; // caractere lido
    char *ptr; // ponteiro de escrita no buffer
    char *head; // ponteiro que guarda o início do buffer

    ptr = ptr_buffer;
    head = ptr_buffer; // salva o início do buffer

    // read() -> lê n bytes via socket e armazena em c, retorna número de bytes lidos, 0 se EOF ou < 0 se houve erro
    for(n = 0; n < max_len; n++) {
        rc = read(file_descriptor, &c, 1);

        if (rc == 1) {
            *ptr = c;
            ptr++;

        } else if (rc == 0) {
            // EOF
            break;

        } else {
            if (errno == EINTR) {
                continue; // tenta de novo se for interrupção
            }
            perror("Erro de leitura\n");
            return -1;
        }
    }

    // adiciona \0 no final se houver espaço
    if (n < max_len) {
        *ptr = '\0';
    }

    // volta ponteiro ptr ao início, se você quiser reutilizar:
    ptr = head;

    return n;
}

// lê um caractere por vez do buffer até encontrar \n ou EOF, retorna número de bytes lidos, 0 se EOF ou -1 se houver erro
ssize_t read_line(int file_descriptor, void *ptr_buffer, size_t max_len) {

    ssize_t n; // número total de bytes lidos
    ssize_t rc; // retorno de read (bytes lidos)
    char c; // caractere lido do socket
    char *ptr; // caminha no buffer

    ptr = ptr_buffer;
    for(n = 1; n < max_len; n++) {

        // read() -> lê n bytes via socket e armazena em c, retorna número de bytes lidos, 0 se EOF ou < 0 se houve erro
        if((rc = read(file_descriptor, &c, 1)) == 1) { // byte lido
            *ptr= c; // adiciona caractere
            ptr++; // passa para a próxima posição

            if(c == '\n')
                break;  // fim da linha
        } 
        else if(rc == 0) {

            if(n == 1){ // primeira iteração
                printf("0 bytes lidos\n");
                return 0;  // EOF, nada lido
            }
            else
                break;     // EOF, retornando dados lidos
        } 
        else{
            if(errno == EINTR) // sinal de interrupção de função
                continue;  // tenta novamente
            
            // falha real
            perror("Falha de escrita\n");
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
        // write() -> envia conteúdo do buffer por socket, retorna número de bytes escritos
        n_written = write(file_descriptor, ptr, n_left);

        if(n_written <= 0){

            if(n_written < 0 && errno == EINTR) // sinal de interrupção de função
                n_written = 0; // reinicia
            else{
                perror("Falha de leitura\n"); // falha real
                return 0;
            } 
        }
        n_left -= n_written;
        ptr += n_written;
    }
    return n;
}

// log para teste
void print_log(int sock, int i, int op){

    printf("Cliente %d conectado via socket %d solicita operação %d no banco\n", i, sock, op);
}

// converte string em maiúscula
void capitalize_string(char *str){

    for(int i = 0; i < strlen(str); i++){
        str[i] = toupper(str[i]);
    }
}

// inicializa cliente
client* initialize_client(int id, int sock, struct sockaddr* server_addr, socklen_t server_len){

    client *new = malloc(sizeof(client));
    new->op = 1 + rand() % MAX_OPS; // número aleatório entre 1 e 7
    new->id = id;
    new->sock = sock;
    new->server_addr = server_addr;
    new->server_len = server_len;

    return new;
}

// conecta thread ao servidor
void* connect_thread(void *thread){

    ssize_t n; // ssize_t é usado para contagem de bytes
    client *c = (client*)thread;
    char response[MAX_PAYLOAD];
    char request[MAX_PAYLOAD];
    
    if(connect(c->sock, c->server_addr, c->server_len) >= 0){

        print_log(c->sock, c->id, c->op);
        
        if(fgets(request, sizeof(request), stdin) != NULL){
            
            capitalize_string(request);

            n = write_all(c->sock, request, strlen(request));
            if(n > 0){
                n = read_line(c->sock, response, MAX_PAYLOAD);

                if(n > 0){
                    fputs(response, stdout);                
                }
                else{
                    close(c->sock);
                    free(c);
                    return NULL;
                }
            }
            else{
                close(c->sock);
                free(c);
                return NULL;
            }
        }
        
    }
    else{
        perror("Erro ao tentar conexão com servidor\n");
        close(c->sock);
        free(c);
        return NULL;
    }

    close(c->sock);
    free(c);
    return NULL;
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

    // MENU
    printf("BANCO DE FILMES\n");
    printf("\n");
    printf("Entre com opção e argumentos dessa forma:\n");
    printf("Inserir filme - 1|titulo|genero|diretor|ano\n");
    printf("Atualizar gênero de filme por ID - 2|ID|genero\n");
    printf("Remover filme - 3|ID\n");
    printf("Listar títulos e IDs de todos filmes - 4\n");
    printf("Listar todas informações de todos filmes - 5\n");
    printf("Listar todas informações de filme por ID - 6|ID\n");
    printf("Listar todas informações de filme por gênero - 7|genero\n");
    printf("\n");

    // CONFIGURAÇÃO DE THREADS CLIENTE
    pthread_t *clients = malloc(MAX_CLIENTS * sizeof(pthread_t)); // armazena clientes como IDs de thread
    int i;
    srand(time(NULL));  // Define a semente baseada na hora atual para gerador de pseudo-aleatorios, evita a execução com sempre a mesma sequência
    for(i = 0; i < MAX_CLIENTS; i++){
        sock = socket(AF_INET, SOCK_STREAM, 0); // cria socket TCP, usando IPv4 e protocolo padrão
        client *new_client = initialize_client(i, sock, (struct sockaddr*)&server_addr, sizeof(server_addr));
        pthread_create(&clients[i], NULL, connect_thread, (void*)new_client);
    }

    for(i = 0; i < MAX_CLIENTS; i++){
        pthread_join(clients[i], NULL);
    }

    free(clients);

    return 0;
}
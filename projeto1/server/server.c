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

#include "database.h" // banco de dados

#define SERVER_PORT 8080 // porta de escuta do servidor
#define BACKLOG 5 // número de conexões que podem aguardar na fila de espera
#define MAX_PAYLOAD 1024 // tamanho máximo do payload

pthread_mutex_t mutex;

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

// lista ligada de threads de servidor
typedef struct ServerThread{

    int sock;
    sqlite3 *db;

} server_thread;

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

// método da divisão para strings usado como função de hashing. Gera chave com pouca probabilidade de repetição
int get_id(char *title, char *genre, char *director, char *year){

    char combined[MAX_PAYLOAD];
    int m = 1783; // número primo longe de uma potência de dois
    int result = 0;

    snprintf(combined, sizeof(combined), "%s%s%s%s", title, genre, director, year);
    
    for(int i = 0; i < strlen(combined); i++){
        result += ((combined[i] % m) * 256);
    }

    return result;
}

// processa mensagem recebida
int receive_request(int sock, sqlite3 *db){

    ssize_t n; // ssize_t é usado para contagem de bytes ou indicação de erro
    char *id, *title, *genre, *director, *year;
    int int_id = 0;
    char response[MAX_PAYLOAD];
    char rcv_buffer[MAX_PAYLOAD];
    char *opt; // opção de entrada
    char delimiter[2] = "|"; // delimitador das entradas

    n = read_line(sock, rcv_buffer, MAX_PAYLOAD);
    if(n > 0){
        
        opt = strtok(rcv_buffer, delimiter); // tokeniza entrada em strings separadas por delimitador

        switch(opt[0]){

            case '1': // cadastrar filme
                title = strtok(NULL, delimiter);
                genre = strtok(NULL, delimiter);
                director = strtok(NULL, delimiter);
                year = strtok(NULL, delimiter); 

                int_id = get_id(title, genre, director, year);

                if(id_list(db, int_id, response, sizeof(response)) == 0){ // registro não existe no banco

                    if(add_movie(db, int_id, title, genre, director, year) == 1)
                        snprintf(response, sizeof(response), "Filme inserido com sucesso\n\n");
                    
                    else
                        snprintf(response, sizeof(response), "Erro ao inserir filme\n\n");
                }
                else{
                    snprintf(response, sizeof(response), "Filme já existe no banco de dados\n\n");
                }

                n = write_all(sock, response, strlen(response));
                if(n > 0)
                    return 1;
                else
                    return 0;
            break;

            case '2': // atualizar gênero de filme
                id = strtok(NULL, delimiter);
                genre = strtok(NULL, delimiter);

                sscanf(id, "%d", &int_id); 

                if(id_list(db, int_id, response, sizeof(response)) != 0){ // registro existe no banco

                    if(genre_update(db, int_id, genre) == 1)
                        snprintf(response, sizeof(response), "Gênero alterado com sucesso\n\n");
                    
                    else
                        snprintf(response, sizeof(response), "Erro ao alterar gênero de filme\n\n");
                    
                }
                else{
                    snprintf(response, sizeof(response), "Filme não existe no banco de dados\n\n");
                }

                n = write_all(sock, response, strlen(response));
                if(n > 0)
                    return 1;
                else
                    return 0;
            break;

            case '3': // remove filme
                id = strtok(NULL, delimiter);

                sscanf(id, "%d", &int_id);

                if(id_list(db, int_id, response, sizeof(response)) != 0){ // registro existe no banco

                    if(delete_movie(db, int_id) == 1)
                        snprintf(response, sizeof(response), "Filme deletado com sucesso\n\n");
                    
                    else
                        snprintf(response, sizeof(response), "Erro ao deletar filme\n\n");
                    
                }
                else{
                    snprintf(response, sizeof(response), "Filme não existe no banco de dados\n\n");
                }

                n = write_all(sock, response, strlen(response));
                if(n > 0)
                    return 1;
                else
                    return 0;
            break;

            case '4': // listar informação básica de filmes

                if(basic_list(db, response, sizeof(response)) == 0)
                    snprintf(response, sizeof(response), "Erro ao listar filmes\n\n");
                
                n = write_all(sock, response, strlen(response));
                if(n > 0)
                    return 1;
                else
                    return 0;
            break;

            case '5': // listar todas informações de filmes
                if(all_list(db, response, sizeof(response)) == 0)
                    snprintf(response, sizeof(response), "Erro ao listar filmes\n\n");
                
                
                n = write_all(sock, response, strlen(response));
                if(n > 0)
                    return 1;
                else
                    return 0;
            break;
            
            case '6': // lista filme por id
                id = strtok(NULL, delimiter);

                sscanf(id, "%d", &int_id);

                if(id_list(db, int_id, response, sizeof(response)) != 0){ // registro existe no banco

                    if(id_list(db, int_id, response, sizeof(response)) == 0)
                        snprintf(response, sizeof(response), "Erro ao listar filme por ID\n\n");
                    
                }
                else{
                    snprintf(response, sizeof(response), "Filme não existe no banco de dados\n\n");
                }

                n = write_all(sock, response, strlen(response));
                if(n > 0)
                    return 1;
                else
                    return 0;
            break;

            case '7': // lista filmes por gênero
                genre = strtok(NULL, delimiter);

                if(genre_list(db, genre, response, sizeof(response)) == 0)
                    snprintf(response, sizeof(response), "Erro ao listar filmes por gênero\n\n");
            
                n = write_all(sock, response, strlen(response));
                if(n > 0)
                    return 1;
                else
                    return 0;
            break;

            default:
                perror("Opção de entrada inválida\n");
                return 0;
        }
    }
    else if(n == 0){
        printf("Conexão encerrada pelo cliente\n");
        return 0;
    }

    else{
        perror("Erro de leitura");
    }

    return 0;
}

// função de threads de servidor
void* thread_handler(void* sthread){

    server_thread *s = (server_thread*)sthread;

    pthread_mutex_lock(&mutex);
    receive_request(s->sock, s->db);
    pthread_mutex_unlock(&mutex);

    close(s->sock);
    free(s);
    pthread_exit(NULL);
}

int main(int argc, char **argv){

    // INICIALIZAÇÃO DO BANCO DE DADOS
    sqlite3 *db;
    if(!initialize_database(&db)){
        perror("Falha ao inicializar o banco de dados");
        exit(EXIT_FAILURE);
    }

    pthread_mutex_init(&mutex, NULL);

    // descritor de arquivo: inteiro que referencia um recurso aberto para o kernel
    int sock, new_sock; // descritores de socket para processo pai e filho

    // socklen_t: inteiro de pelo menos 32 bits, utilizado para manter um padrão de tamanho, independente da arquitetura do sistema. Garante portabilidade e atendimento do padrão posix
    socklen_t client_len; // armazena tamanho em bytes de estruturas de endereço socket

    struct sockaddr_in client_addr, server_addr; // estrutura que armazena parâmetros para criação de socket

    //CONFIGURAÇÃO DE SOCKET
    // cria socket TCP, usando IPv4 e protocolo padrão
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if(sock == -1){
        perror("Falha ao criar o socket");
        exit(EXIT_FAILURE);
    }

    memset(&server_addr, 0, sizeof(server_addr)); // zera bloco de memória, evita bugs ao utilizar bind(), connect() 

    server_addr.sin_family = AF_INET; // define familia de endereçamento IPv4
    // htonx(); funções htonx(host to network x) convertem ordem de bytes x do host para a ordem de bytes da rede
    // ex: host usa little-endian e rede usa big-endian (ordem padrão na rede)
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY); // endereço de escuta do servidor. 0.0.0.0 escuta em todas as interfaces
    server_addr.sin_port = htons(SERVER_PORT); // porta do servidor

    bind(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)); // associa socket ao endereço
    listen(sock, BACKLOG); // coloca o socket em modo de escuta

    while(1){
        client_len = sizeof(client_addr); // tamanho da struct de endereço do cliente
        new_sock = accept(sock, (struct sockaddr*)&client_addr, &client_len); // gera socket com nova conexão, preenche endereço com IP e porta do cliente

        if(new_sock >= 0){
        
            pthread_t tid; // id de thread
            server_thread *sthread = malloc(sizeof(server_thread));
            sthread->sock = new_sock;
            sthread->db = db;

            if(pthread_create(&tid, NULL, thread_handler, (void*)sthread) != 0){
                perror("Erro ao criar thread");
                close(new_sock);
                free(sthread);
                continue;
            }

            // thread destacada, não precisa dar join (evita vazamento)
            pthread_detach(tid);
        }
        else{
            if(errno == EINTR) // falha por interrupção, reinicia
                continue;
            
            perror("Falha ao receber conexão\n");
            exit(EXIT_FAILURE);
        }
    }

    close_database(db);
    pthread_mutex_destroy(&mutex);

    return 0;
}
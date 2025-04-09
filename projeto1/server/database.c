#include <stdio.h>
#include <stdlib.h>

#include "database.h"

// inicializa banco ou cria arquivo .db se não existir
int initialize_database(sqlite3 **db){

    // tenta abrir ou criar o banco
    if(sqlite3_open("filmes.db", db) != SQLITE_OK){
        fprintf(stderr, "Erro ao abrir banco de dados: %s\n", sqlite3_errmsg(*db));
        return 0;
    }

    // cria a tabela se não existir
    const char *sql =
        "CREATE TABLE IF NOT EXISTS filmes ("
        "id INTEGER PRIMARY KEY, "
        "titulo TEXT NOT NULL, "
        "genero TEXT NOT NULL, "
        "diretor TEXT NOT NULL, "
        "ano TEXT NOT NULL"
        ");";

    char *erro = NULL;
    if(sqlite3_exec(*db, sql, 0, 0, &erro) != SQLITE_OK){
        fprintf(stderr, "Erro ao criar tabela: %s\n", erro);
        sqlite3_free(erro);
        sqlite3_close(*db);
        return 0;
    }

    return 1;
}

// fecha banco
void close_database(sqlite3 *db){

    sqlite3_close(db);
}

// adiciona filme
int add_movie(sqlite3 *db, int id, const char *title, const char *genre, const char *director, const char *year){

    const char *sql = "INSERT INTO filmes (id, titulo, genero, diretor, ano) VALUES (?, ?, ?, ?, ?);";
    sqlite3_stmt *stmt; // statement

    if(sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK){
        fprintf(stderr, "Erro ao preparar INSERT: %s\n", sqlite3_errmsg(db));
        return 0;
    }

    sqlite3_bind_int(stmt, 1, id);
    sqlite3_bind_text(stmt, 2, title, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 3, genre, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 4, director, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 5, year, -1, SQLITE_STATIC);

    if(sqlite3_step(stmt) != SQLITE_DONE){
        fprintf(stderr, "Erro ao inserir filme: %s\n", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return 0;
    }

    sqlite3_finalize(stmt);
    return 1;
}

// altera gênero de filme
int genre_update(sqlite3 *db, int id, const char *new_genre){

    const char *sql = "UPDATE filmes SET genero = ? WHERE id = ?;";
    sqlite3_stmt *stmt; 

    // prepara o comando SQL
    if(sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK){
        fprintf(stderr, "Erro ao preparar UPDATE: %s\n", sqlite3_errmsg(db));
        return 0;
    }

    // associa os valores aos parâmetros do SQL
    sqlite3_bind_text(stmt, 1, new_genre, -1, SQLITE_STATIC);
    sqlite3_bind_int(stmt, 2, id);

    // executa o UPDATE
    if(sqlite3_step(stmt) != SQLITE_DONE){

        fprintf(stderr, "Erro ao atualizar gênero: %s\n", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return 0;
    }

    sqlite3_finalize(stmt);
    return 1; 
}

// remove filme por id
int delete_movie(sqlite3 *db, int id){

    const char *sql = "DELETE FROM filmes WHERE id = ?;";
    sqlite3_stmt *stmt;

    if(sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK){
        fprintf(stderr, "Erro ao preparar DELETE: %s\n", sqlite3_errmsg(db));
        return 0;
    }

    // associa id
    sqlite3_bind_int(stmt, 1, id);

    // Executa o DELETE
    if(sqlite3_step(stmt) != SQLITE_DONE){
        fprintf(stderr, "Erro ao remover filme: %s\n", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return 0;
    }

    // verifica se algum registro foi afetado
    if(sqlite3_changes(db) == 0){
        printf("Filme com ID %d não encontrado.\n", id);
        sqlite3_finalize(stmt);
        return 0;
    }

    sqlite3_finalize(stmt);
    printf("Filme com ID %d removido com sucesso.\n", id);
    return 1;
}

// lista todos ids e títulos
int basic_list(sqlite3 *db){

    const char *sql = "SELECT id, titulo FROM filmes;";
    sqlite3_stmt *stmt;

    if(sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK){
        fprintf(stderr, "Erro ao preparar SELECT: %s\n", sqlite3_errmsg(db));
        return 0;
    }

    // itera sobre os resultados
    while(sqlite3_step(stmt) == SQLITE_ROW){
        int id = sqlite3_column_int(stmt, 0);
        const unsigned char *title = sqlite3_column_text(stmt, 1);

        printf("ID: %d\tTítulo: %s\n", id, title);
    }

    sqlite3_finalize(stmt);
    return 1; 
}

// lista todas informações
int all_list(sqlite3 *db){

    const char *sql = "SELECT id, titulo, genero, diretor, ano FROM filmes;";
    sqlite3_stmt *stmt;

    if(sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK){
        fprintf(stderr, "Erro ao preparar SELECT: %s\n", sqlite3_errmsg(db));
        return 0;
    }

    // executa a consulta linha por linha
    while(sqlite3_step(stmt) == SQLITE_ROW){
        int id = sqlite3_column_int(stmt, 0);
        const unsigned char *title  = sqlite3_column_text(stmt, 1);
        const unsigned char *genre  = sqlite3_column_text(stmt, 2);
        const unsigned char *director = sqlite3_column_text(stmt, 3);
        const unsigned char *year     = sqlite3_column_text(stmt, 4);

        printf("ID: %d | Título: %s | Gênero: %s | Diretor: %s | Ano: %s\n",
               id, title, genre, director, year);
    }

    sqlite3_finalize(stmt);
    return 1;
}

// lista informações de filme por id
int id_list(sqlite3 *db, int id){

    const char *sql = "SELECT id, titulo, genero, diretor, ano FROM filmes WHERE id = ?;";
    sqlite3_stmt *stmt;

    if(sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK){
        fprintf(stderr, "Erro ao preparar SELECT: %s\n", sqlite3_errmsg(db));
        return 0;
    }

    // associa o ID ao parâmetro ?
    sqlite3_bind_int(stmt, 1, id);

    // executa a consulta
    if(sqlite3_step(stmt) == SQLITE_ROW){
        int id_result = sqlite3_column_int(stmt, 0);
        const unsigned char *title  = sqlite3_column_text(stmt, 1);
        const unsigned char *genre  = sqlite3_column_text(stmt, 2);
        const unsigned char *director = sqlite3_column_text(stmt, 3);
        const unsigned char *year     = sqlite3_column_text(stmt, 4);

        printf("ID: %d | Título: %s | Gênero: %s | Diretor: %s | Ano: %s\n",
               id_result, title, genre, director, year);

        sqlite3_finalize(stmt);
        return 1;
    } 
    else{
        printf("Filme com ID %d não encontrado.\n", id);
        sqlite3_finalize(stmt);
        return 0;
    }
}

// lista filmes por gênero
int genre_list(sqlite3 *db, const char *genre_search){

    const char *sql = "SELECT id, titulo, genero, diretor, ano FROM filmes WHERE genero = ?;";
    sqlite3_stmt *stmt;

    if(sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK){
        fprintf(stderr, "Erro ao preparar SELECT: %s\n", sqlite3_errmsg(db));
        return 0;
    }

    // associa o valor do gênero ao ?
    sqlite3_bind_text(stmt, 1, genre_search, -1, SQLITE_STATIC);

    int result = 0;

    // itera sobre os resultados
    while(sqlite3_step(stmt) == SQLITE_ROW){
        result = 1;

        int id = sqlite3_column_int(stmt, 0);
        const unsigned char *title  = sqlite3_column_text(stmt, 1);
        const unsigned char *genre = sqlite3_column_text(stmt, 2);
        const unsigned char *director = sqlite3_column_text(stmt, 3);
        const unsigned char *year     = sqlite3_column_text(stmt, 4);

        printf("ID: %d | Título: %s | Gênero: %s | Diretor: %s | Ano: %s\n",
               id, title, genre, director, year);
    }

    if(!result){
        printf("Nenhum filme do gênero \"%s\" foi encontrado.\n", genre_search);
    }

    sqlite3_finalize(stmt);
    return 1;
}
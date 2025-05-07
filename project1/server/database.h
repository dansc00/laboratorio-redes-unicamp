#ifndef DATABASE_H
#define DATABASE_H

#include "sqlite3.h"

int initialize_database(sqlite3 **db);
void close_database(sqlite3 *db);
int is_database_empty(sqlite3 *db);
int add_movie(sqlite3 *db, int id, const char *title, const char *genre, const char *director, const char *year);
int genre_update(sqlite3 *db, int id, const char *new_genre);
int delete_movie(sqlite3 *db, int id);
int basic_list(sqlite3 *db, char *response, size_t size);
int all_list(sqlite3 *db, char *response, size_t size);
int id_list(sqlite3 *db, int id, char *response, size_t size);
int genre_list(sqlite3 *db, const char *genre_search, char *response, size_t size);

#endif
#ifndef DATABASE_H
#define DATABASE_H

#include "sqlite3.h"

int initialize_database(sqlite3 **db);
int add_movie(sqlite3 *db, int id, const char *title, const char *genre, const char *director, const char *year);
int genre_update(sqlite3 *db, int id, const char *new_genre);
int basic_list(sqlite3 *db);
int all_list(sqlite3 *db);
int id_list(sqlite3 *db, int id);
int genre_list(sqlite3 *db, const char *genre_search);

#endif
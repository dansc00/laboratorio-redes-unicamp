#!/bin/bash

gcc ./server/server.c ./server/database.c ./server/sqlite3.c -Wall -o ./server/server
gcc ./client/client.c -Wall  -o ./client/client -pthread

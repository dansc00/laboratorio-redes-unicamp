#!/bin/bash

# cria grupo docker e inclui usuário atual

user=$(whoami)
#groupadd docker # grupo docker geralmente já vem incluido por padrão, descomente se não vier
sudo usermod -aG docker $user
newgrp docker

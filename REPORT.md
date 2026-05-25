# Лабараторная работа по работе с docker

## Цель работы: работа посвящена изучению технологии работы с контейнерами.

## Предварительная подготовка

```bash 
$ sudo apt-get update
$ sudo apt-get install -y git
$ git --version

$ sudo apt-get install -y ca-certificates curl
$ sudo install -m 0755 -d /etc/apt/keyrings
$ sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
$ sudo chmod a+r /etc/apt/keyrings/docker.asc

$ echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
    https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

$ sudo apt-get update
$ sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
$ docker --version
$ docker compose version
$ sudo usermod -aG docker $USER
$ newgrp docker
```

## Ход работы

### Часть 1.

1. Поддключаем репозиторий, редактируем, создаем docker файл.

```bash
$ git clone https://github.com/<ВАШ_ЛОГИН>/lab_docker
$ cd lab_docker

$ cd app
$ cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
EOF

$ rm -rf LICENSE
$ rm -rf .git
```

2. Собираем образ.

```bash
$ docker build -t lab_docker .
[+] Building 2.1s (11/11) FINISHED                               docker:default
 => [internal] load build definition from Dockerfile                       0.0s
 => => transferring dockerfile: 349B                                       0.0s
 => [internal] load metadata for docker.io/library/python:3.9-slim         1.1s
 => [internal] load .dockerignore                                          0.0s
 => => transferring context: 2B                                            0.0s
 => [1/6] FROM docker.io/library/python:3.9-slim@sha256:2d97f6910b16bd338  0.1s
 => => resolve docker.io/library/python:3.9-slim@sha256:2d97f6910b16bd338  0.1s
 => [internal] load build context                                          0.1s
 => => transferring context: 2.06kB                                        0.0s
 => CACHED [2/6] WORKDIR /app                                              0.0s
 => CACHED [3/6] RUN apt-get update && apt-get install -y     build-essen  0.0s
 => CACHED [4/6] COPY requirements.txt .                                   0.0s
 => CACHED [5/6] RUN pip install --no-cache-dir -r requirements.txt        0.0s
 => CACHED [6/6] COPY . .                                                  0.0s
 => exporting to image                                                     0.4s
 => => exporting layers                                                    0.0s
 => => exporting manifest sha256:038ed9dbf55f1780de7eb9a22ba485682dbfe593  0.0s
 => => exporting config sha256:dc50ff18dc64396c4d7bc640cffefdd9d930557e58  0.0s
 => => exporting attestation manifest sha256:d235f2183a72b53ffc9d2429aca4  0.1s
 => => exporting manifest list sha256:760e1c43157eb24afeda349bc41bbbfd8bd  0.1s
 => => naming to docker.io/library/lab_docker:latest                       0.0s
 => => unpacking to docker.io/library/lab_docker:latest                    0.0s
```

3. Запускаем контейнер.

```bash
$ docker run -d --name my_app -p 5000:5000 lab_docker
925c02060e374fd97427f10f065e97571f052660181c268d92344bd42512259c
```

4. Проверяем логи.
   
```bash
$ docker logs my_app
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.2:5000
Press CTRL+C to quit
```

5. Копируем README.md в контейнер и подключаемся к терминалу контейнера для проверки.

```bash
$ cd ..
$ docker cp README.md my_app:/home/README.md
Successfully copied 4.44kB (transferred 6.14kB) to my_app:/home/README.md
$ docker exec -it my_app /bin/bash
root@925c02060e37:/app# ls /home/
README.md
root@925c02060e37:/app# exit
exit
```

7. Остановка контейнера.

```bash
$ docker stop my_app
$ docker rm my_app
```

### Часть 2.

1. Создаем docker-compose.yml + ```.env``` и ```.env.example``` для пользователей.

```bash
cat > .env << 'EOF'
DB_HOST=db
DB_USER=appuser
DB_PASS=apppassword
DB_NAME=tasksdb
MYSQL_ROOT_PASSWORD=rootpassword
EOF
```

```bash
cat > .env.example << 'EOF'
DB_HOST=db
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=tasksdb
MYSQL_ROOT_PASSWORD=your_root_password
EOF
```

```bash
$ cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build: ./app
    container_name: lab_docker_app
    ports:
      - "5000:5000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DB_HOST=${DB_HOST}
      - DB_USER=${DB_USER}
      - DB_PASS=${DB_PASS}
      - DB_NAME=${DB_NAME}
    restart: on-failure

  db:
    image: mysql:8.0
    container_name: mysql_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASS}
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

volumes:
  db_data:
EOF
```

2. Запустить приложение + база даных.

```bash
$ docker compose up --build
WARN[0000] /home/from1k/from1k/workspace/lab_docker/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
[+] Building 2.0s (13/13) FINISHED                                              
 => [internal] load local bake definitions                                 0.0s
 => => reading from stdin 534B                                             0.0s
 => [internal] load build definition from Dockerfile                       0.0s
 => => transferring dockerfile: 349B                                       0.0s
 => [internal] load metadata for docker.io/library/python:3.9-slim         0.9s
 => [internal] load .dockerignore                                          0.0s
 => => transferring context: 2B                                            0.0s
 => [1/6] FROM docker.io/library/python:3.9-slim@sha256:2d97f6910b16bd338  0.1s
 => => resolve docker.io/library/python:3.9-slim@sha256:2d97f6910b16bd338  0.1s
 => [internal] load build context                                          0.1s
 => => transferring context: 191B                                          0.0s
 => CACHED [2/6] WORKDIR /app                                              0.0s
 => CACHED [3/6] RUN apt-get update && apt-get install -y     build-essen  0.0s
 => CACHED [4/6] COPY requirements.txt .                                   0.0s
 => CACHED [5/6] RUN pip install --no-cache-dir -r requirements.txt        0.0s
 => CACHED [6/6] COPY . .                                                  0.0s
 => exporting to image                                                     0.3s
 => => exporting layers                                                    0.0s
 => => exporting manifest sha256:f37bcb9c3a383791f3ab878490f65bb190f56bdd  0.0s
 => => exporting config sha256:d1e020babc709f6bd4c9c2749c02eb9bdfba82a055  0.0s
 => => exporting attestation manifest sha256:b5bdffb968a74010bee228256247  0.1s
 => => exporting manifest list sha256:968f5a0b7bed4fa8d625c64f919d72aae4f  0.1s
 => => naming to docker.io/library/lab_docker-app:latest                   0.0s
 => => unpacking to docker.io/library/lab_docker-app:latest                0.0s
 => resolving provenance for metadata file                                 0.0s
[+] up 4/4
 ✔ Image lab_docker-app       Built                                         2.0s
 ✔ Network lab_docker_default Created                                       0.1s
 ✔ Container mysql_db         Created                                       0.2s
 ✔ Container lab_docker_app   Created                                       0.2s
Attaching to lab_docker_app, mysql_db
Container mysql_db Waiting 
mysql_db  | 2026-05-24 17:40:44+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 8.0.46-1.el9 started.
mysql_db  | 2026-05-24 17:40:44+00:00 [Note] [Entrypoint]: Switching to dedicated user 'mysql'
mysql_db  | 2026-05-24 17:40:44+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 8.0.46-1.el9 started.
mysql_db  | '/var/lib/mysql/mysql.sock' -> '/var/run/mysqld/mysqld.sock'
mysql_db  | 2026-05-24T17:40:45.062699Z 0 [Warning] [MY-011068] [Server] The syntax '--skip-host-cache' is deprecated and will be removed in a future release. Please use SET GLOBAL host_cache_size=0 instead.
mysql_db  | 2026-05-24T17:40:45.063907Z 0 [System] [MY-010116] [Server] /usr/sbin/mysqld (mysqld 8.0.46) starting as process 1
mysql_db  | 2026-05-24T17:40:45.072209Z 1 [System] [MY-013576] [InnoDB] InnoDB initialization has started.
mysql_db  | 2026-05-24T17:40:46.329970Z 1 [System] [MY-013577] [InnoDB] InnoDB initialization has ended.
mysql_db  | 2026-05-24T17:40:46.883445Z 0 [Warning] [MY-010068] [Server] CA certificate ca.pem is self signed.
mysql_db  | 2026-05-24T17:40:46.883512Z 0 [System] [MY-013602] [Server] Channel mysql_main configured to support TLS. Encrypted connections are now supported for this channel.
mysql_db  | 2026-05-24T17:40:46.896587Z 0 [Warning] [MY-011810] [Server] Insecure configuration for --pid-file: Location '/var/run/mysqld' in the path is accessible to all OS users. Consider choosing a different directory.
mysql_db  | 2026-05-24T17:40:46.936005Z 0 [System] [MY-011323] [Server] X Plugin ready for connections. Bind-address: '::' port: 33060, socket: /var/run/mysqld/mysqlx.sock
mysql_db  | 2026-05-24T17:40:46.936475Z 0 [System] [MY-010931] [Server] /usr/sbin/mysqld: ready for connections. Version: '8.0.46'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server - GPL.
Container mysql_db Healthy 
lab_docker_app  |  * Serving Flask app 'app'
lab_docker_app  |  * Debug mode: off
lab_docker_app  | WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
lab_docker_app  |  * Running on all addresses (0.0.0.0)
lab_docker_app  |  * Running on http://127.0.0.1:5000
lab_docker_app  |  * Running on http://172.18.0.3:5000
lab_docker_app  | Press CTRL+C to quit
lab_docker_app  | 172.18.0.1 - - [24/May/2026 17:41:27] "GET / HTTP/1.1" 200 -
```
(Снимок экрана лежит в отдельном файле данного репозитория)

3. Остановка.

```bash
$ docker compose down -v
WARN[0000] /home/from1k/from1k/workspace/lab_docker/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
[+] down 4/4
 ✔ Container lab_docker_app   Removed                                      10.3s
 ✔ Container mysql_db         Removed                                       0.8s
 ✔ Network lab_docker_default Removed                                       0.1s
 ✔ Volume lab_docker_db_data  Removed                                       0.0s
```

4. Создаем коммиты, пушим, не забываем добавить ```.gitignore``` (.env не включаем в коммиты, он хранится локально с нашими реальными паролями)

```bash
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
*.pyo
.venv/
venv/
EOF
```

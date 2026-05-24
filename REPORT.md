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


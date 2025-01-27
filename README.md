# BD Malhas infra

Este repositório contém a configuração de uma infraestrutura básica usando Docker e Docker Compose.

## Pré-requisitos

Certifique-se de ter os seguintes componentes instalados em sua máquina:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Configurações Iniciais

Antes de iniciar a infraestrutura, siga os passos abaixo para configurar o ambiente:

1. Copie o arquivo de exemplo `.env.example` para `.env`:
   ```bash
   sudo cp .env.example .env
   ```

2. Inicie os contêineres com o comando abaixo, configurando 3 instâncias do serviço `spark-worker`:
   ```bash
   docker compose up -d --scale spark-worker=3
   ```

    - A flag `-d` executa os contêineres em segundo plano.
    - O parâmetro `--scale` especifica o número de réplicas para o serviço `spark-worker`.

## Comandos Úteis

### Parar a Infraestrutura

Para parar todos os contêineres e liberar recursos, execute:

```bash
docker compose down
```

### Reiniciar a Infraestrutura

Para reiniciar os contêineres em execução, use:

```bash
docker compose restart
```

## Estrutura do Repositório

- **`docker-compose.yml`**: Configura os serviços da infraestrutura.
- **`.env.example`**: Exemplo de arquivo de variáveis de ambiente.
- **`README.md`**: Documentação do projeto.

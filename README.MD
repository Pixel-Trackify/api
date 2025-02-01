# API de Autenticação e Gerenciamento de Usuários Django

Este projeto é uma API baseada em Django para autenticação e gerenciamento de usuários, com autenticação JWT, registro de usuários, login, logout e capacidades de filtragem de usuários.

## Funcionalidades

- Registro de usuários com validação de email e CPF
- Autenticação baseada em JWT (login e logout)
- Filtragem, busca e ordenação de usuários
- Modelo de usuário personalizado com rastreamento de tentativas de login e bloqueio de conta
- Interface administrativa para gerenciamento de usuários

## Requisitos

- Docker
- Docker Compose

## Configuração

1. **Clone o repositório:**
    ```sh
    git clone https://github.com/mmmatheus013/login_django.git
    cd login_django
    ```

2. **Crie e configure as variáveis de ambiente:**
    Copie o arquivo de exemplo de ambiente e atualize os valores conforme necessário.
    ```sh
    cp dotenv_files/.env-example dotenv_files/.env
    ```

3. **Construa e execute os containers Docker:**
    ```sh
    docker compose up -d --build
    ```

4. **Acesse a aplicação:**
    A API estará disponível em `http://0.0.0.0:8000`.

## Endpoints da API

### Autenticação

- `POST /api/v1/authentication/token/`: Obter par de tokens JWT
- `POST /api/v1/authentication/token/refresh/`: Atualizar token JWT
- `POST /api/v1/authentication/token/verify/`: Verificar token JWT

### Gerenciamento de Usuários

- `POST /api/v1/accounts/`: Registrar um novo usuário
- `GET /api/v1/users/`: Listar todos os usuários (somente admin)
- `GET /api/v1/accounts/<int:pk>`: Recuperar, atualizar ou excluir uma conta de usuário
- `POST /api/v1/login/`: Login do usuário
- `POST /api/v1/logout/`: Logout do usuário
- `GET /api/v1/filter-users/`: Filtrar, buscar e ordenar usuários

## Executando Testes

Para executar os testes, use o seguinte comando:
```sh
docker compose run django-command-runner python manage.py test
```

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou envie um pull request para quaisquer alterações.
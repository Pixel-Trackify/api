# API de Autenticação e Gerenciamento de Usuários Django

Este projeto é uma API baseada em Django para autenticação e gerenciamento de usuários, com autenticação JWT, registro de usuários, login, logout, gerenciamento de planos e capacidades de filtragem de usuários.

## Funcionalidades

- Registro de usuários com validação de email e CPF
- Autenticação baseada em JWT (login e logout)
- Filtragem, busca e ordenação de usuários
- Modelo de usuário personalizado com rastreamento de tentativas de login e bloqueio de conta
- Gerenciamento de planos de usuários
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
    docker compose up -d --build app
    ```

4. **Acesse a aplicação:**
    A API estará disponível em `http://127.0.0.1:8000`.

## Instruções para Importar a Coleção no Postman

- Abra o Postman.
- Clique no botão "Import" no canto superior esquerdo.
- Selecione a aba "Upload Files".
- Selecione o arquivo postman_collection.json do projeto.
- Clique no botão "Import".

## Endpoints da API

### Autenticação

- `POST /authentication/token/`: Obter par de tokens JWT
- `POST /authentication/token/refresh/`: Atualizar token JWT
- `POST /authentication/token/verify/`: Verificar token JWT

### Gerenciamento de Usuários

- `POST /auth/login/`: Login do usuário
- `POST /auth/logout/`: Logout do usuário
- `POST /auth/register-accounts/`: Registrar um novo usuário
- `GET /auth/users/`: Listar todos os usuários (somente admin)
- `GET /auth/profile/`: Visualizar perfil do usuário autenticado
- `PUT /auth/profile/`: Atualizar perfil do usuário autenticado
- `POST /auth/change-password/`: Alterar senha do usuário autenticado
- `POST /auth/update-plan/`: Atualizar plano do usuário
- `GET /auth/my-plan/`: Visualizar plano do usuário autenticado
- `GET /auth/subscription-history/`:  Retorna o histórico de assinaturas do usuário autenticado.

- `GET /auth/accounts/<int:pk>`: Recuperar, atualizar ou excluir uma conta de usuário
- `GET /auth/filter-users/`: Filtrar, buscar e ordenar usuários

### Gerenciamento de Planos

- `GET /plans/`: Listar todos os planos
- `POST /plans/`: Criar um novo plano (somente admin)
- `GET /plans/<int:pk>`: Recuperar, atualizar ou excluir um plano (somente admin)

### Gerenciamento de Tutoriais

- `GET /tutoriais/`: Lista todos os tutoriais disponíveis.
- `POST /tutoriais/`: Cria um novo tutorial (somente para administradores).
- `GET /tutoriais/<int:pk>/`: Recupera, atualiza ou exclui um tutorial específico (somente para administradores).

## Executando Testes

Para executar os testes, use o seguinte comando:
```sh
docker compose run django-command-runner python manage.py test
```

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou envie um pull request para quaisquer alterações.
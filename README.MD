# API de Autenticação e Gerenciamento de Usuários Django

Este projeto é uma aplicação Django que fornece uma API para gerenciar autenticação de usuários, campanhas publicitárias, integrações, planos e assinaturas.

## Funcionalidades

- Registro de usuários com validação de email e CPF
- Autenticação baseada em JWT (login e logout)
- Filtragem, busca e ordenação de usuários
- Modelo de usuário personalizado com rastreamento de tentativas de login e bloqueio de conta
- Gerenciamento de planos de usuários
- Interface administrativa para gerenciamento de usuários
- Criação e gerenciamento de campanhas publicitárias
- Integração com plataformas externas
- Gerenciamento de assinaturas e transações
- Processamento de webhooks

## Requisitos

- Docker
- Docker Compose

## Configuração

1. **Clone o repositório:**
    ```sh
    git clone https://TOKEN@github.com/Pixel-Trackify/api.git
    cd api
    ```

2. **Crie e configure as variáveis de ambiente:**
    Copie o arquivo de exemplo de ambiente e atualize os valores conforme necessário.
    ```sh
    cp dotenv_files/.env-example dotenv_files/.env
    ```

3. **Executando o Projeto:**

    Edite o arquivo `.env` e configure as variáveis de acordo com seu ambiente.
    ***Ambiente de Desenvolvimento:***
    ```sh
    docker compose up -d --scale app=3 --build local
    ```
    ***Ambiente de Produção:***
    ```sh
    docker compose up -d --scale app=3 --build production
    ```
4. **Acesse a aplicação:**
    A API estará disponível em `http://127.0.0.1:8000`.


## Executando Testes

Para executar os testes, use o seguinte comando:
```sh
docker compose run --rm django-command-runner python manage.py test
```

## Executando Migrações de Tabela

Para executar o migrate, use o seguinte comando:
```sh
docker compose run --rm django-command-runner python manage.py migrate
```

## Certbot SSL

Para obter e renovar certificados SSL usando Certbot, utilize o seguinte comando:

```sh
docker compose run --rm certbot certonly --webroot -w /app/data/certbot -d api.onetracking.io --non-interactive --agree-tos --email webmaster@onetracking.io
```

Este comando irá gerar certificados SSL para o domínio `api.onetracking.io` e armazená-los no diretório especificado.

## Instruções para Importar a Coleção no Postman

- Abra o Postman.
- Clique no botão "Import" no canto superior esquerdo.
- Selecione a aba "Upload Files".
- Selecione o arquivo postman_collection.json do projeto.
- Clique no botão "Import".

## Endpoints da API

## Endpoints de Autenticação
- **GET /auth/accounts/{uuid}**: Recuperar detalhes da conta do usuário pelo UUID.
- **POST /auth/register-accounts/**: Registrar uma nova conta de usuário.
- **POST /authentication/token/**: Obter um token JWT para autenticação.
- **POST /authentication/token/refresh/**: Atualizar o token JWT.
- **POST /authentication/token/verify/**: Verificar o token JWT.

## Endpoints de Gerenciamento de Usuários
- **GET /auth/users/**: Listar todos os usuários (acesso de administrador necessário).

## Endpoints de Assinatura
- **GET /auth/subscription-history/**: Recuperar o histórico de assinaturas do usuário autenticado.
- **POST /auth/update-plan/**: Atualizar o plano de assinatura do usuário.

## Endpoints de Campanhas
- **GET /campaigns/**: Listar todas as campanhas (acesso de administrador necessário).
- **POST /campaigns/**: Criar uma nova campanha (acesso de administrador necessário).
- **GET /campaigns/{id}/**: Recuperar detalhes de uma campanha específica.
- **PUT /campaigns/{id}/**: Atualizar uma campanha específica (acesso de administrador necessário).
- **PATCH /campaigns/{id}/**: Atualizar parcialmente uma campanha específica (acesso de administrador necessário).
- **DELETE /campaigns/{id}/**: Excluir uma campanha específica (acesso de administrador necessário).

## Endpoints de Integração
- **GET /integration/{uid}/**: Recuperar detalhes de uma integração específica (acesso de administrador necessário).
- **DELETE /integration/{uid}/**: Excluir uma integração específica (acesso de administrador necessário).
- **GET /integrations/**: Listar todas as integrações (acesso de administrador necessário).
- **POST /integrations/**: Criar uma nova integração (acesso de administrador necessário).
- **GET /integrations/{id}/**: Recuperar detalhes de uma integração específica.
- **PUT /integrations/{id}/**: Atualizar uma integração específica (acesso de administrador necessário).
- **PATCH /integrations/{id}/**: Atualizar parcialmente uma integração específica (acesso de administrador necessário).
- **DELETE /integrations/{id}/**: Excluir uma integração específica (acesso de administrador necessário).

## Endpoints de Planos
- **GET /plans/**: Listar todos os planos (acesso de administrador necessário).
- **POST /plans/**: Criar um novo plano (acesso de administrador necessário).
- **GET /plans/{id}/**: Recuperar detalhes de um plano específico.
- **PUT /plans/{id}/**: Atualizar um plano específico (acesso de administrador necessário).
- **PATCH /plans/{id}/**: Atualizar parcialmente um plano específico (acesso de administrador necessário).
- **DELETE /plans/{id}/**: Excluir um plano específico (acesso de administrador necessário).

## Endpoints de Assinaturas
- **POST /subscriptions/**: Criar uma nova assinatura (requer autenticação JWT).

## Endpoints de Transações
- **GET /transactions/**: Listar todas as transações (acesso de administrador necessário).
- **GET /transactions/{transaction_id}/**: Recuperar detalhes de uma transação específica.

## Endpoints de Tutoriais
- **GET /tutoriais/**: Listar todos os tutoriais.
- **POST /tutoriais/**: Criar um novo tutorial.
- **GET /tutoriais/{id}/**: Recuperar detalhes de um tutorial específico.
- **PUT /tutoriais/{id}/**: Atualizar um tutorial específico.
- **PATCH /tutoriais/{id}/**: Atualizar parcialmente um tutorial específico.
- **DELETE /tutoriais/{id}/**: Excluir um tutorial específico.

## Endpoints de Webhooks
- **GET /webhook/kwai/{uid}/**: Recuperar detalhes do webhook KWAI.
- **POST /webhook/zeroone/{uid}/**: Processar uma requisição POST do webhook ZeroOne.


## Segurança

A API utiliza autenticação baseada em JWT (JSON Web Tokens) para proteger os endpoints. Certifique-se de incluir o token JWT no cabeçalho `Authorization` para todas as requisições que requerem autenticação.

## Contribuição

1. **Fork o repositório**
2. **Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)**
3. **Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)**
4. **Push para a branch (`git push origin feature/nova-feature`)**
5. **Abra um Pull Request**

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
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
    cp .env-example .env
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
docker compose run --rm django-command-runner python manage.py makemigrations
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


## Tarefas Automáticas: Expiração e Lembrete de Assinaturas

O sistema possui comandos automáticos para:

- **Expirar assinaturas vencidas:** Desativa assinaturas cujo campo `expiration` já passou, marcando-as como `is_active=False` e `status='expired'`.
- **Enviar lembretes de pagamento:** Envia e-mails para usuários cujas assinaturas estão próximas do vencimento, conforme o intervalo configurado em `days_to_reminder`. O envio é controlado para evitar duplicidade.

### Como executar manualmente

```sh
python manage.py expire_subscriptions
python manage.py send_payment_reminders
```

### Como agendar no cron (Linux)

Para rodar os comandos automaticamente todos os dias à meia-noite e ao meio-dia, adicione ao seu crontab (`crontab -e`):

```
0 0,12 * * * /caminho/para/seu/venv/bin/python /caminho/para/seu/projeto/manage.py expire_subscriptions >> /caminho/para/seu/cron_expire.log 2>&1
0 0,12 * * * /caminho/para/seu/venv/bin/python /caminho/para/seu/projeto/manage.py send_payment_reminders >> /caminho/para/seu/cron_reminder.log 2>&1
```

> **Dica:** Ajuste os caminhos conforme o local do seu projeto e virtualenv.

### Logs

A saída dos comandos será registrada nos arquivos de log definidos (`cron_expire.log` e `cron_reminder.log`).  
Você pode visualizar os logs com:

```sh
tail -n 50 /caminho/para/seu/cron_expire.log
tail -n 50 /caminho/para/seu/cron_reminder.log
```

---

Essas tarefas garantem que assinaturas sejam expiradas automaticamente e que os usuários recebam lembretes antes do vencimento, melhorando a experiência e reduzindo inadimplência.
## Endpoints da API

Desenvolvimento: 

`http://127.0.0.1:8000/api/docs/swagger/`

Produção: 

`https://api.onetracking.io/api/docs/swagger/`

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
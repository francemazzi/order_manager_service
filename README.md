# Order Manager Service

Un servizio di gestione ordini costruito con Flask, PostgreSQL e autenticazione JWT.
Il sistema è bassato su questo test task: https://docs.google.com/document/d/12SxnIHz93bQNMXlwbd7EaxczEhspK5mpir4fjGzYyN8/edit?usp=sharing

## Requisiti di Sistema

- Docker
- Docker Compose
- Git

## Installazione

1. Clona il repository:

```bash
git clone <repository-url>
cd order_manager_service
```

2. Crea il file `.env` (o usa quello esistente):

```bash
cp .env.example .env  # se non esiste già
```

3. Avvia i servizi con Docker Compose:

```bash
docker-compose up --build
```

L'applicazione sarà disponibile su:

- API: http://localhost:5000
- Documentazione Swagger: http://localhost:5000/api/docs
- MailHog (server email di test): http://localhost:8025

## Struttura del Progetto

```
order_manager_service/
├── app.py                 # Applicazione Flask principale
├── requirements.txt       # Dipendenze Python
├── Dockerfile            # Configurazione Docker
├── docker-compose.yml    # Configurazione Docker Compose
├── .env                  # Variabili d'ambiente
├── models/               # Modelli del database
│   └── user.py          # Modello Utente
├── routes/               # Route API
│   └── auth.py          # Route di autenticazione
├── utils/               # Utilità
│   └── email.py        # Gestione email
└── static/              # File statici
    └── swagger.json     # Documentazione API
```

## API Disponibili

### Autenticazione

#### Registrazione

```bash
curl -X POST http://localhost:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
           "email": "test@example.com",
           "password": "test123",
           "first_name": "Mario",
           "last_name": "Rossi"
         }'
```

#### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{
           "email": "test@example.com",
           "password": "test123"
         }'
```

#### Profilo Utente

```bash
curl -X GET http://localhost:5000/api/auth/me \
     -H "Authorization: Bearer <il-tuo-token>"
```

## Test Email

Il servizio utilizza MailHog per il testing delle email in ambiente di sviluppo. Tutte le email inviate dall'applicazione possono essere visualizzate nell'interfaccia web di MailHog:

http://localhost:8025

## Database

PostgreSQL è accessibile localmente sulla porta 5432:

- Host: localhost
- Porta: 5432
- Database: order_manager
- Utente: postgres
- Password: postgres

## Sviluppo

Per sviluppare localmente senza Docker:

1. Crea un ambiente virtuale:

Linux/Mac:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

3. Configura le variabili d'ambiente nel file `.env`

4. Avvia l'applicazione:

```bash
python app.py
```

## Aggiornamento docker

```bash
docker-compose down
docker-compose build
docker-compose up -d
docker-compose exec web flask db upgrade
```

Se è la prima attiviti il contianer è possibile effettuare il seeding dei dati con il comando:

```bash
docker-compose exec web python seeds.py
```

## Note di Sicurezza

In produzione:

- Cambia tutte le password e le chiavi segrete nel file `.env`
- Configura un vero server SMTP invece di MailHog
- Utilizza HTTPS
- Implementa rate limiting e altre misure di sicurezza

## Supporto

Per problemi o domande, apri una issue nel repository.

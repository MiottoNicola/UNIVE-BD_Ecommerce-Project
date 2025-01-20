##### Base di Dati 2023/2024 - Università Ca' FOscari Venezia

# Informazioni progetto

**Categoria sito:** piattaforma di E-commerce

### Tema
1. **Gestione degli utenti:** Implementare funzionalità di autenticazione e autorizzazione degli utenti. Gli
utenti dovrebbero poter registrarsi, accedere e gestire i propri profili. Inoltre, dovrebbero esserci ruoli
utente differenti come acquirenti e venditori, ognuno con il proprio insieme di permessi.
2. **Gestione dei prodotti:** Creare un database per memorizzare informazioni sui prodotti, inclusi nome,
descrizione, categoria, prezzo, disponibilità, ecc. I venditori dovrebbero poter aggiungere, modificare
ed eliminare i propri prodotti.
3. **Ricerca e Filtri:** Implementare una funzionalità di ricerca che permetta agli utenti di cercare prodotti
basati su parole chiave, categorie o altri attributi. Inoltre, fornire opzioni di filtro per affinare i risultati
della ricerca basati su intervallo di prezzo, marca, ecc.
4. **Carrello della spesa:** Implementare una funzionalità di carrello della spesa che permetta agli utenti di
aggiungere prodotti al proprio carrello, aggiornare le quantità e procedere al pagamento. Il sistema
dovrebbe gestire i livelli di inventario e aggiornare la disponibilità dei prodotti di conseguenza.
5. **Gestione degli ordini:** Sviluppare un sistema per gestire gli ordini effettuati dagli utenti. Gli utenti
dovrebbero poter visualizzare la loro cronologia degli ordini, monitorare lo stato dei propri ordini e
ricevere notifiche sugli aggiornamenti degli ordini. I venditori dovrebbero anche avere accesso ai dettagli
degli ordini per i prodotti che hanno venduto e poterne aggiornare lo stato.
6. **Recensioni e Valutazioni** (Opzionale se meno di tre persone): Consentire agli utenti di lasciare recensioni
e valutazioni per i prodotti che hanno acquistato. Visualizzare le valutazioni medie e fornire opzioni
di ordinamento basate sulle valutazioni per aiutare gli utenti a prendere decisioni informate.

### Requisiti
Il progetto richiede come minimo lo svolgimento dei seguenti punti:
1. Progettazione concettuale e logica dello schema della base di dati su cui si appogger`a all’applicazione,
opportunamente commentata e documentata secondo la notazione introdotta nel Modulo 1 del corso.
2. Creazione di un database, anche artificiale, tramite l’utilizzo di uno specifico DBMS. La creazione delle
tabelle e l’inserimento dei dati pu`o essere effettuato anche con uno script esterno al progetto.
3. Implementazione di un front-end minimale basato su HTML e CSS. E’ possibile utilizzare framework
CSS esistenti come W3.CSS, Bootstrap o altri. E’ inoltre possibile fare uso di JavaScript per migliorare
l’esperienza utente, ma non è richiesto e non influirà sulla valutazione finale.
4. Implementazione di un back-end basato su Flask e SQLAlchemy (o Flask-SQLAlchemy).

Per migliorare il progetto e la relativa valutazione è raccomandato gestire anche i seguenti aspetti:
1. Integrità dei dati: definizione di vincoli, trigger, transazioni per garantire l’integrità dei dati gestiti
dall’applicazione.
2. Sicurezza: definizione di opportuni ruoli e politiche di autorizzazione, oltre che di ulteriori meccanismi
atti a migliorare il livello di sicurezza dell’applicazione (es. difese contro XSS e SQL injection).
2
3. Performance: definizione di indici o viste materializzate sulla base delle query pi`u frequenti previste.
4. Astrazione dal DBMS sottostante: uso di Expression Language o ORM per astrarre dal dialetto SQL.
E’ possibile focalizzarsi solo su un sottoinsieme di questi aspetti, ma i progetti eccellenti cercheranno di
coprirli tutti ad un qualche livello di dettaglio. E’ meglio approfondire adeguatamente solo alcuni di questi
aspetti piuttosto che coprirli tutti in modo insoddisfacente.

## Descrizione delle Cartelle

- **Lezioni_python/**: contiene tutti i file utilizzati per studiare i linguaggi e librerie necessarie per la realizzazione.
- **project_files/**: contiene tutti i file del progetto, compreso un dumb del database con alcune query di popolamento già pronte.

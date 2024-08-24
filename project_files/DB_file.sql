--creazione del database in cui salvare i prodotti
--drop database if exists ecommerce;
--create database ecommerce;

--ricarica del db
drop table if exists recensioni;
drop table if exists carrello;
drop table if exists dettagliordine;
drop table if exists ordini;
drop table if exists prodotti;
drop table if exists utenti;

--creazione tabelle del database
create table utenti(
    IDUtente serial primary key,
    nome varchar not null,
    cognome varchar not null,
    email varchar not null unique,
    password varchar not null,
    ruolo integer not null,

    constraint check_ruolo check ( ruolo=1 or ruolo=10 )
);

create table prodotti(
    IDProdotto serial primary key,
    IDVenditore integer,
    titolo varchar not null,
    autore varchar not null,
    editore varchar not null,
    annoPubblicazione int not null,
    descrizione varchar not null,
    prezzo float not null,
    quantità integer not null,
    categoria varchar not null,

    foreign key(IDVenditore) references utenti(IDUtente) ON DELETE CASCADE ON UPDATE CASCADE,
    constraint check_categoria_prodotti check (categoria='Romanzi e Classici' or categoria='Fantasy e Horror' or categoria='Amore e Passione' or categoria='Thriller' or categoria='Gialli' or categoria='Saggistica' or categoria='Bambini' or categoria='Fumetti e Manga' or categoria='Scuola' or categoria='Altro'),
    constraint check_quantità_prodotti check (quantità>=0),
    constraint check_prezzo_prodotti check (prezzo>=0)
);

create table ordini(
    IDOrdine serial primary key,
    IDUtente integer,
    destinatario varchar not null,
    data date not null default current_date,
    indirizzo varchar not null,
    città varchar not null,
    provincia varchar not null,
    cap varchar not null,
    totale float not null,
    stato integer not null default 1,

    foreign key(IDUtente) references utenti(IDUtente) ON DELETE SET NULL ON UPDATE CASCADE,
    constraint check_stato_ordini check (stato=1 or stato=2 or stato=3),
    constraint check_totale_ordini check (totale>=0),
    constraint check_cap_ordini check (length(cap)<=5)
);

create table dettagliordine(
    IDOrdine integer,
    IDProdotto integer,
    titolo varchar not null,
    quantità integer not null,
    prezzo float not null,

    foreign key(IDOrdine) references ordini(IDOrdine) ON DELETE CASCADE ON UPDATE CASCADE,
    foreign key(IDProdotto) references prodotti(IDProdotto) ON DELETE SET NULL ON UPDATE CASCADE,
    constraint check_prezzo_dettagli check (prezzo>=0),
    constraint check_quantità_dettagli check (quantità>0),
    constraint check_dettagli_univoci unique(IDOrdine, IDProdotto)
);

create table carrello(
    IDCarrello serial primary key,
    IDUtente integer,
    IDProdotto integer,
    quantità integer not null,

    foreign key(IDUtente) references utenti(IDUtente) ON DELETE CASCADE ON UPDATE CASCADE,
    foreign key(IDProdotto) references prodotti(IDProdotto) ON DELETE CASCADE ON UPDATE CASCADE,
    constraint check_quantità_carrello check (quantità>0)
);

create table recensioni(
    IDRecensione serial primary key,
    IDUtente integer,
    IDProdotto integer,
    voto integer not null,
    titolo varchar not null,
    testo varchar not null,
    data date not null default current_date,

    foreign key(IDUtente) references utenti(IDUtente) ON DELETE CASCADE ON UPDATE CASCADE,
    foreign key(IDProdotto) references prodotti(IDProdotto) ON DELETE CASCADE ON UPDATE CASCADE,
    constraint check_voto_recensioni check (voto>=1 and voto<=5),
    constraint check_recensioni_univoca unique(IDUtente, IDProdotto)
);


--inserimento dei valori nel database
--acquirenti
insert into utenti (nome, cognome, email, password, ruolo)values('Matteo', 'Montessori', 'matteo.montessori@gmail.com', 'c1327iwNcYru', 1);
insert into utenti (nome, cognome, email, password, ruolo)values('Francesca', 'Brambilla', 'brambifrancy@gmail.com', '43765ouy', 1);
insert into utenti (nome, cognome, email, password, ruolo)values('Simone', 'Dei Meneghetti', 'deimeneghetti97simone@gmail.com', '3k6j3n4k635', 1);
insert into utenti (nome, cognome, email, password, ruolo)values('Marta', 'Rossi', 'rossi.marta@gmail.com', 'ieurieur8743', 1);
insert into utenti (nome, cognome, email, password, ruolo)values('Luciano', 'Dalla Lana', 'luciano.dalla.lana@libero.it', 'b8y45t7834y7', 1);
--venditori
insert into utenti (nome, cognome, email, password, ruolo)values('Charles', 'Matinous', 'charles.mat@webmail.free.fr', 'n458y98nv3yt', 10);
insert into utenti (nome, cognome, email, password, ruolo)values('Andrèe', 'Martinez', 'andree.martinez@gmx.ch', 'vm3597yt3f44', 10);
insert into utenti (nome, cognome, email, password, ruolo)values('Matheus', 'Bechenbauer', 'matheus.bech@junico.de', '945ntv4589', 10);
insert into utenti (nome, cognome, email, password, ruolo)values('Silvia', 'Salentina', 'silviasalentina93@gmail.com', 'MjehfHh4587', 10);

--libri
insert into prodotti (IDVenditore, titolo, autore, editore, annoPubblicazione, descrizione, prezzo, quantità, categoria)values(6, 'Come una notte a Bali', 'Gianluca Gotto', 'Mondadori', 2019,
                            'Romanzo sul lasciare tutto e vivere la vita seguendo la felicità.', 12.00, 3, 'Romanzi e Classici');
insert into prodotti (IDVenditore, titolo, autore, editore, annoPubblicazione, descrizione, prezzo, quantità, categoria)values(6, 'My soul mate', 'Wah Kee', 'Toshokan', 2022,
                            'Manga su un rapporto di amicizia particolare.', 7.90, 2, 'Fumetti e Manga');
insert into prodotti (IDVenditore, titolo, autore, editore, annoPubblicazione, descrizione, prezzo, quantità, categoria)values(7, 'Come scrivere in cinese', 'Wang Dongdong', 'Feltrinelli', 2018,
                            'Una guida alla calligrafia cinese e alla sua storia millenaria.', 12.90, 4, 'Scuola');
insert into prodotti (IDVenditore, titolo, autore, editore, annoPubblicazione, descrizione, prezzo, quantità, categoria)values(7, 'I salici ciechi e la donna addormentata', 'Murakami Haruki', 'Mondadori', 2010,
                            'Una raccolta di racconti che racconta le atmosfere del Giappone.', 14.00, 2, 'Romanzi e Classici');
insert into prodotti (IDVenditore, titolo, autore, editore, annoPubblicazione, descrizione, prezzo, quantità, categoria)values(8, 'Profondo come il mare, leggero come il cielo', 'Gianluca Gotto', 'Mondadori', 2023,
                            'Un insieme di riflessioni sulla sfera spirituale della vita e il legame con il buddhismo.', 19.50, 1, 'Saggistica');
insert into prodotti (IDVenditore, titolo, autore, editore, annoPubblicazione, descrizione, prezzo, quantità, categoria)values(9, 'Il piccolo principe', 'Antoine de Saint-Exupéry', 'Gallucci Editore', 2023,
                            'Un viaggio memorabile attraverso vari pianeti alla scoperta dei valori della vita.', 3.22, 5, 'Bambini');
insert into prodotti (IDVenditore, titolo, autore, editore, annoPubblicazione, descrizione, prezzo, quantità, categoria)values(9, 'Assassinio sull Orient Express', 'Agatha Christie', 'Giunti', 2017,
                            'Un viaggio molto particolare e misterioso, alla ricerca del colpevole di un omicidio', 20.00, 3, 'Gialli');

--ordini
insert into ordini (IDUtente, destinatario,  indirizzo, città, provincia, cap, totale, stato)values(1, 'Matteo Montessori', 'Via Roma 12', 'Milano', 'Milano', '20100', 12.00, 1);
insert into ordini (IDUtente, destinatario, indirizzo, città, provincia, cap, totale, stato)values(1, 'Matteo Montessori', 'Via Roma 12', 'Milano', 'Milano', '20100', 7.90, 1);
insert into ordini (IDUtente, destinatario, indirizzo, città, provincia, cap, totale, stato)values(2, 'Lucia Bocca ', 'Via Garibaldi 23', 'Roma', 'Roma', '00100', 12.90, 1);
insert into ordini (IDUtente, destinatario, indirizzo, città, provincia, cap, totale, stato)values(2, 'Lucia Bocca', 'Via Garibaldi 23', 'Roma', 'Roma', '00100', 14.00, 1);
insert into ordini (IDUtente, destinatario, indirizzo, città, provincia, cap, totale, stato)values(3, 'Simone Dei Meneghetti', 'Via dei Mille 45', 'Torino', 'Torino', '10100', 19.50, 1);
insert into ordini (IDUtente, destinatario, indirizzo, città, provincia, cap, totale, stato)values(4, 'Marta Rossi', 'Via dei Mille 45', 'Torino', 'Torino', '10100', 3.22, 1);
insert into ordini (IDUtente, destinatario, indirizzo, città, provincia, cap, totale, stato)values(4, 'Luca Bibi', 'Via dei Mille 45', 'Torino', 'Torino', '10100', 20.00, 1);

--dettagli ordine
insert into dettagliordine (IDOrdine, IDProdotto, titolo, quantità, prezzo)values(1, 1, 'Come una notte a Bali', 1, 12.00);
insert into dettagliordine (IDOrdine, IDProdotto, titolo, quantità, prezzo)values(1, 4, 'I salici ciechi e la donna addormentata', 1, 14.00);
insert into dettagliordine (IDOrdine, IDProdotto, titolo, quantità, prezzo)values(2, 2, 'My soul mate', 1, 7.90);
insert into dettagliordine (IDOrdine, IDProdotto, titolo, quantità, prezzo)values(3, 3, 'Come scrivere in cinese', 1, 12.90);
insert into dettagliordine (IDOrdine, IDProdotto, titolo, quantità, prezzo)values(4, 4, 'I salici ciechi e la donna addormentata', 1, 14.00);
insert into dettagliordine (IDOrdine, IDProdotto, titolo, quantità, prezzo)values(5, 5, 'Profondo come il mare, leggero come il cielo', 1, 19.50);
insert into dettagliordine (IDOrdine, IDProdotto, titolo, quantità, prezzo)values(6, 6, 'Il piccolo principe', 1, 3.22);
insert into dettagliordine (IDOrdine, IDProdotto, titolo, quantità, prezzo)values(7, 7, 'Assassinio sull Orient Express', 1, 20.00);

--carrello
insert into carrello (IDUtente, IDProdotto, quantità)values(1, 1, 1);
insert into carrello (IDUtente, IDProdotto, quantità)values(1, 2, 1);
insert into carrello (IDUtente, IDProdotto, quantità)values(2, 3, 1);
insert into carrello (IDUtente, IDProdotto, quantità)values(2, 4, 1);
insert into carrello (IDUtente, IDProdotto, quantità)values(3, 5, 1);
insert into carrello (IDUtente, IDProdotto, quantità)values(4, 6, 1);
insert into carrello (IDUtente, IDProdotto, quantità)values(4, 7, 1);

--recensioni
insert into recensioni (IDUtente, IDProdotto, voto, titolo, testo)values(1, 1, 5, 'Bellissimo', 'Un libro che ti fa riflettere sulla vita e sulle scelte che si fanno.');
insert into recensioni (IDUtente, IDProdotto, voto, titolo, testo)values(1, 2, 4, 'Interessante', 'Un manga che ti fa riflettere sulla vita e sulle scelte che si fanno.');
insert into recensioni (IDUtente, IDProdotto, voto, titolo, testo)values(2, 3, 5, 'Fantastico', 'Un libro che ti fa riflettere sulla vita e sulle scelte che si fanno.');
insert into recensioni (IDUtente, IDProdotto, voto, titolo, testo)values(2, 4, 4, 'Interessante', 'Un libro che ti fa riflettere sulla vita e sulle scelte che si fanno.');
insert into recensioni (IDUtente, IDProdotto, voto, titolo, testo)values(3, 5, 5, 'Fantastico', 'Un libro che ti fa riflettere sulla vita e sulle scelte che si fanno.');
insert into recensioni (IDUtente, IDProdotto, voto, titolo, testo)values(4, 6, 5, 'Bellissimo', 'Un libro che ti fa riflettere sulla vita e sulle scelte che si fanno.');
insert into recensioni (IDUtente, IDProdotto, voto, titolo, testo)values(4, 7, 4, 'Interessante', 'Un libro che ti fa riflettere sulla vita e sulle scelte che si fanno.');

-- creazione delle funzioni e dei trigger
--trigger per prevenire l'inserimento di utenti duplicati
CREATE OR REPLACE FUNCTION prevenire_utente_duplicato()
    RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1
               FROM utenti
               WHERE email = NEW.email) THEN
        RAISE EXCEPTION 'Utente duplicato non permesso.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevenire_utente_duplicato
    BEFORE INSERT OR UPDATE ON utenti
    FOR EACH ROW
EXECUTE FUNCTION prevenire_utente_duplicato();

--trigger per prevenire l'inserimento di recensioni duplicate
CREATE OR REPLACE FUNCTION prevenire_recensione_duplicata()
    RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1
               FROM recensioni
               WHERE idutente = NEW.idutente AND
                     idprodotto = NEW.idprodotto) THEN
        RAISE EXCEPTION
            'Recensione duplicata non permessa per lo stesso utente e prodotto.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevenire_recensione_duplicata
    BEFORE INSERT OR UPDATE ON recensioni
    FOR EACH ROW
EXECUTE FUNCTION prevenire_recensione_duplicata();


--trigger per aggiornare la quantità di prodotti in base agli ordini
CREATE OR REPLACE FUNCTION aggiornare_quantità_prodotto()
    RETURNS TRIGGER AS $$
BEGIN
    UPDATE prodotti
    SET quantità = quantità - NEW.quantità
    WHERE idprodotto = NEW.idprodotto;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_aggiornare_quantità_prodotto
    AFTER INSERT OR UPDATE ON dettagliordine
    FOR EACH ROW
EXECUTE FUNCTION aggiornare_quantità_prodotto();


--trigger per aggiornare il totale dell'ordine
CREATE OR REPLACE FUNCTION aggiornare_totale_ordine()
    RETURNS TRIGGER AS $$
BEGIN
    UPDATE ordini
    SET totale = (SELECT SUM(prezzo * quantità)
                  FROM dettagliordine
                  WHERE idordine = NEW.idordine)
    WHERE idordine = NEW.idordine;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_aggiornare_totale_ordine
    AFTER INSERT OR UPDATE ON dettagliordine
    FOR EACH ROW
EXECUTE FUNCTION aggiornare_totale_ordine();


-- trigger verifica quantità prodotti
CREATE OR REPLACE FUNCTION verifica_quantità_prodotto()
    RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantità > (SELECT quantità
                       FROM prodotti
                       WHERE idprodotto = NEW.idprodotto) THEN
        RAISE EXCEPTION 'Quantità non disponibile per il prodotto.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verifica_quantità_prodotto
    BEFORE INSERT OR UPDATE ON dettagliordine
    FOR EACH ROW
EXECUTE FUNCTION verifica_quantità_prodotto();


-- trigger verifica quantità carrello
CREATE OR REPLACE FUNCTION verifica_quantità_carrello()
    RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantità > (SELECT quantità
                       FROM prodotti
                       WHERE idprodotto = NEW.idprodotto) THEN
        RAISE EXCEPTION 'Quantità non disponibile per il prodotto.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verifica_quantità_carrello
    BEFORE INSERT OR UPDATE ON carrello
    FOR EACH ROW
EXECUTE FUNCTION verifica_quantità_carrello();


-- ruoli amministrazione del database
--ruolo amministratore
create role admin with login password 'admin';
grant all on all TABLES in schema public to admin;
grant all on all SEQUENCES in schema public to admin;
grant all on all FUNCTIONS in schema public to admin;
grant all on all ROUTINES in schema public to admin;

--ruolo utente
create role utente with login password 'utente';
grant select, insert, update, delete on all TABLES in schema public to utente;
grant select, usage on all SEQUENCES in schema public to utente;
grant execute on all FUNCTIONS in schema public to utente;
grant execute on all ROUTINES in schema public to utente;

--ruolo venditore
create role venditore with login password 'venditore';
grant select, insert, update, delete on all TABLES in schema public to venditore;
grant select, usage on all SEQUENCES in schema public to venditore;
grant execute on all FUNCTIONS in schema public to venditore;
grant execute on all ROUTINES in schema public to venditore;
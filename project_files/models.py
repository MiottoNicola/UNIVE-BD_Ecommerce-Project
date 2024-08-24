import sqlalchemy as sq
from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint, String, Integer
from sqlalchemy.orm import mapped_column, relationship
from config import db

# Definizione delle tabelle del database


# Tabella Utenti
class Utenti(db.Model):
    __tablename__ = 'utenti'

    # Campi
    idutente = mapped_column(Integer, primary_key=True)
    nome = mapped_column(String, nullable=False)
    cognome = mapped_column(String, nullable=False)
    email = mapped_column(String, nullable=False, unique=True)
    password = mapped_column(String, nullable=False)
    ruolo = mapped_column(Integer, nullable=False)

    # Check constraints
    __table_args__ = (
        CheckConstraint(sq.text("ruolo=0 OR ruolo=10"), name='check_role'),
    )

    def __repr__(self):
        return f"<Utenti(idutente={self.idutente}, nome={self.nome}, cognome={self.cognome}, email={self.email}, ruolo={self.ruolo})>"


# Tabella Prodotti
class Prodotti(db.Model):
    __tablename__ = 'prodotti'

    # Campi
    idprodotto = mapped_column(sq.Integer, primary_key=True, autoincrement=True)
    idvenditore = mapped_column(sq.Integer, ForeignKey(Utenti.idutente), nullable=False)
    titolo = mapped_column(sq.String, nullable=False)
    autore = mapped_column(sq.String, nullable=False)
    editore = mapped_column(sq.String, nullable=False)
    annopubblicazione = mapped_column(sq.Integer, nullable=False)
    descrizione = mapped_column(sq.String, nullable=False)
    prezzo = mapped_column(sq.Float, nullable=False)
    quantità = mapped_column(sq.Integer, nullable=False)
    categoria = mapped_column(sq.String, nullable=False)

    # Check constraints
    __table_args__ = (
        CheckConstraint(sq.text("prezzo>=0"), name='check_prezzo_prodotti'),
        CheckConstraint(sq.text("quantita>=0"), name='check_quantita_prodotti'),
        CheckConstraint("categoria IN ('Romanzi e Classici', 'Fantasy e Horror', 'Amore e Passione', 'Thriller', 'Gialli', 'Saggistica', 'Bambini', 'Fumetti e Manga', 'Scuola', 'Altro')", name='check_categoria_prodotti'),
    )

    # Foreign key
    venditore = relationship('Utenti')

    def __repr__(self):
        return f"<Prodotti(idprodotto={self.idprodotto}, titolo={self.titolo}, autore={self.autore}, editore={self.editore}, prezzo={self.prezzo}, quantità={self.quantità}, categoria={self.categoria})>"


# Tabella Ordini
class Ordini(db.Model):
    __tablename__ = 'ordini'

    # Campi
    idordine = mapped_column(sq.Integer, primary_key=True, autoincrement=True)
    idutente = mapped_column(sq.Integer, ForeignKey(Utenti.idutente), nullable=False)
    destinatario = mapped_column(sq.String, nullable=False)
    data = mapped_column(sq.Date, nullable=False, default=sq.func.now())
    indirizzo = mapped_column(sq.String, nullable=False)
    città = mapped_column(sq.String, nullable=False)
    provincia = mapped_column(sq.String, nullable=False)
    cap = mapped_column(sq.String, nullable=False)
    totale = mapped_column(sq.Float, nullable=False, default='0')
    stato = mapped_column(sq.Integer, nullable=False, default='1')

    # Check constraints
    __table_args__ = (
        CheckConstraint(sq.text("stato=1 OR stato=2 OR stato=3"), name='check_stato_ordini'),
        CheckConstraint(sq.text("totale>=0"), name='check_totale_ordini'),
        CheckConstraint(sq.text("length(cap)<=5"), name='check_cap_ordini'),
    )

    # Foreign key
    utente = relationship('Utenti')

    def __repr__(self):
        return f"<Ordini(idordine={self.idordine}, idutente={self.idutente}, data={self.data}, indirizzo={self.indirizzo}, citta={self.città}, cap={self.cap}, totale={self.totale}, stato={self.stato})>"


# Tabella DettagliOrdine
class DettagliOrdine(db.Model):
    __tablename__ = 'dettagliordine'

    # Campi
    idordine = mapped_column(sq.Integer, ForeignKey(Ordini.idordine), primary_key=True)
    idprodotto = mapped_column(sq.Integer, ForeignKey(Prodotti.idprodotto), primary_key=True)
    titolo = mapped_column(sq.String, nullable=False)
    quantità = mapped_column(sq.Integer, nullable=False)
    prezzo = mapped_column(sq.Float, nullable=False)

    # Check constraints
    __table_args__ = (
        CheckConstraint(sq.text("quantita>0"), name='check_quantita_dettagliordine'),
        CheckConstraint(sq.text("prezzo>=0"), name='check_prezzo_dettagliordine'),
    )

    # Unique constraint
    unique_constraint = UniqueConstraint('idordine', 'idprodotto', name='unique_dettagliordine')

    # Foreign key
    ordine = relationship('Ordini')
    prodotto = relationship('Prodotti')

    def __repr__(self):
        return f"<DettagliOrdine(idordine={self.idordine}, idprodotto={self.idprodotto}, quantità={self.quantità}, prezzo={self.prezzo})>"


# Tabella Carrello
class Carrello(db.Model):
    __tablename__ = 'carrello'

    # Campi
    idutente = mapped_column(sq.Integer, ForeignKey(Utenti.idutente), primary_key=True)
    idprodotto = mapped_column(sq.Integer, ForeignKey(Prodotti.idprodotto), primary_key=True)
    quantità = mapped_column(sq.Integer, nullable=False)

    # Check constraints
    __table_args__ = (
        CheckConstraint(sq.text("quantità>0"), name='check_quantita_carrello'),
    )

    # Foreign key
    utente = relationship('Utenti')
    prodotto = relationship('Prodotti')

    def __repr__(self):
        return f"<Carrello(idutente={self.idutente}, idprodotto={self.idprodotto}, quantità={self.quantità})>"


# Tabella Recensioni
class Recensioni(db.Model):
    __tablename__ = 'recensioni'

    # Campi
    idrecensione = mapped_column(sq.Integer, primary_key=True, autoincrement=True)
    idprodotto = mapped_column(sq.Integer, ForeignKey(Prodotti.idprodotto), nullable=False)
    idutente = mapped_column(sq.Integer, ForeignKey(Utenti.idutente), nullable=False)
    voto = mapped_column(sq.Integer, nullable=False)
    titolo = mapped_column(sq.String, nullable=False)
    testo = mapped_column(sq.String, nullable=False)
    data = mapped_column(sq.Date, nullable=False, default=sq.func.now())

    # Check constraints
    __table_args__ = (
        CheckConstraint(sq.text("voto>=0 AND voto<=5"), name='check_voto_recensioni'),
    )

    # Unique constraint
    unique_constraint = UniqueConstraint('idprodotto', 'idutente', name='unique_recensione')

    # Foreign key
    prodotto = relationship('Prodotti')
    utente = relationship('Utenti')

    def __repr__(self):
        return f"<Recensioni(idrecensione={self.idrecensione}, idutente={self.idutente}, idprodotto={self.idprodotto}, voto={self.voto}, titolo={self.titolo}, testo={self.testo}, data={self.data})>"


# Funzioni ausiliarie
def login(email: str, password: str):
    user = Utenti.query.filter_by(email=email, password=password).first()
    if user is None:
        return {'ok': False, 'idutente': -1}
    return {'ok': True, 'idutente': user.idutente}


def exist_user(email: str):
    user = Utenti.query.filter_by(email=email).first()
    return user is not None


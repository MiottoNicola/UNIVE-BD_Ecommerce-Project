import os
from flask import render_template, session as login_session, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from config import app, db
import models


# Funzione per controllare se l'utente è loggato
def check_cookie():
    if 'IDUtente' in login_session:
        user = models.Utenti.query.filter_by(idutente=login_session.get('IDUtente')).first()
        if user is not None:
            return user
        else:
            login_session.clear()
    return None


# Pagina principale
@app.route('/')
def index():
    user = check_cookie()
    return render_template('index.html', user=user)


# Pagina per visualizzare i prodotti e filtrarli
@app.route('/product', methods=['GET'])
def product():
    user = check_cookie()

    # Filtri
    title = request.args.get('name')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    category = request.args.get('category')

    # Query per i prodotti disponibili e filtrati
    query = models.Prodotti.query
    if title:
        query = query.filter(models.Prodotti.titolo.ilike(f'%{title}%'))
    if min_price:
        query = query.filter(models.Prodotti.prezzo >= float(min_price))
    if max_price:
        query = query.filter(models.Prodotti.prezzo <= float(max_price))
    if category:
        query = query.filter(models.Prodotti.categoria == category)

    query = query.filter(models.Prodotti.quantità > 0)
    products = query.all()
    categories = [prod.categoria for prod in
                  models.Prodotti.query.distinct(models.Prodotti.categoria).filter(models.Prodotti.quantità > 0).all()]

    return render_template('product.html', user=user, products=products, categories=categories)


# Pagina per visualizzare i dettagli di un prodotto
@app.route('/product_detail/<int:idprodotto>')
def product_detail(idprodotto):
    user = check_cookie()
    product = models.Prodotti.query.get(idprodotto)
    if product is None:
        return redirect(url_for('index'))

    # Recensioni del prodotto
    recensioni = models.Recensioni.query.filter_by(idprodotto=idprodotto).all()
    already_reviewed = False
    if recensioni:
        already_reviewed = False
        if user is not None and models.Recensioni.query.filter_by(idprodotto=idprodotto,
                                                                  idutente=user.idutente).first() is not None:
            already_reviewed = True
        recensioni = [
            {'utente': models.Utenti.query.get(r.idutente).nome, 'voto': r.voto, 'titolo': r.titolo, 'testo': r.testo,
             'data': r.data, } for r in recensioni]
    return render_template('product_detail.html', user=user, product=product, recensioni=recensioni,
                           already_reviewed=already_reviewed)


# Aggiunta di recensione ad un prodotto
@app.route('/add_review/<int:idprodotto>', methods=['POST'])
def add_review(idprodotto):
    user = check_cookie()
    if user is None:
        return redirect(url_for('login'))

    if models.Prodotti.query.get(idprodotto) is None:
        return redirect(url_for('index'))

    if models.Recensioni.query.filter_by(idprodotto=idprodotto, idutente=user.idutente).first() is not None:
        return redirect(url_for('product_detail', idprodotto=idprodotto))

    # Dati della recensione
    titolo = request.form['titolo']
    testo = request.form['testo']
    voto = int(request.form['voto'])

    # Nuova recensione
    new_review = models.Recensioni(
        idprodotto=idprodotto,
        idutente=user.idutente,
        titolo=titolo,
        testo=testo,
        voto=voto
    )
    db.session.add(new_review)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

    return redirect(url_for('product_detail', idprodotto=idprodotto))


# Pagina per visualizzare il carrello
@app.route('/cart')
def cart():
    user = check_cookie()
    if user is None:
        return redirect(url_for('login'))

    error = None
    cart = models.Carrello.query.filter_by(idutente=user.idutente).order_by(models.Carrello.idprodotto).all()
    product = []
    for c in cart:
        prod = models.Prodotti.query.get(c.idprodotto)
        if prod is not None:
            # Controllo disponibilità prodotti
            if prod.quantità == 0:
                db.session.delete(c)
                db.session.commit()
                error = "Alcuni prodotti non sono più disponibili e sono stati rimossi dal carrello"
            else:
                # Controllo quantità prodotti
                if c.quantità > prod.quantità:
                    c.quantità = prod.quantità
                    error = "Alcuni prodotti non sono più disponibili nella quantità richiesta"
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        error = str(e)
                product.append({'idprodotto': prod.idprodotto, 'titolo': prod.titolo, 'prezzo': prod.prezzo,
                                'quantità': c.quantità, 'disponibilità': prod.quantità})
        else:
            # Rimozione prodotti non più disponibili
            db.session.delete(c)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                error = str(e)

    if error is not None:
        return render_template('cart.html', user=user, carts=product, error=error)

    return render_template('cart.html', user=user, carts=product)


# Aggiunta di un prodotto al carrello
@app.route('/add_cart/<int:idprodotto>', methods=['POST'])
def add_to_cart(idprodotto):
    user = check_cookie()
    if user is None:
        return jsonify(
            {'success': False, 'message': 'Devi effetttuare l\'accesso prima di aggiungere prodotti al carrello.'})

    product = models.Prodotti.query.get(idprodotto)
    if product is None:
        return jsonify({'success': False, 'message': 'Prodotto non trovato.'})

    cart = models.Carrello.query.filter_by(idutente=user.idutente, idprodotto=idprodotto).first()
    if cart is not None: # Se il prodotto è già nel carrello, incremento la quantità
        # Controllo disponibilità prodotti
        if product.quantità < cart.quantità + 1:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': str(e)})
            return jsonify({'success': False, 'message': 'Quantità non disponibile.'})
        cart.quantità += 1
    else: # Se il prodotto non è già nel carrello, lo aggiungo
        new_cart = models.Carrello(idutente=user.idutente, idprodotto=idprodotto, quantità=1)
        db.session.add(new_cart)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    return jsonify({'success': True, 'message': 'Prodotto aggiunto al carrello con successo.'})


# Rimozione di un prodotto dal carrello
@app.route('/del_cart/<int:idprodotto>')
def remove_from_cart(idprodotto):
    user = check_cookie()
    if user is None:
        return redirect(url_for('login'))

    cart = models.Carrello.query.filter_by(idutente=user.idutente, idprodotto=idprodotto).first()
    if cart is not None:
        # Rimozione prodotto dal carrello
        db.session.delete(cart)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})

    return redirect(url_for('cart'))


# Aggiornamento della quantità di un prodotto nel carrello
@app.route('/update_cart_quantity', methods=['POST'])
def update_cart_quantity():
    user = check_cookie()
    if user is None:
        return jsonify({'success': False, 'message': 'Devi essere loggato per aggiornare il carrello.'})

    # Dati della richiesta
    data = request.get_json()
    product_id = data.get('product_id')
    new_quantity = int(data.get('quantity'))
    if new_quantity < 1:
        return jsonify({'success': False, 'message': 'Quantità non valida.'})

    cart_item = models.Carrello.query.filter_by(idprodotto=product_id, idutente=user.idutente).first()
    if cart_item:
        # Controllo disponibilità prodotti
        if new_quantity < 1:
            return jsonify({'success': False, 'message': 'Quantità non valida.'})
        if models.Prodotti.query.get(product_id).quantità < new_quantity:
            return jsonify({'success': False, 'message': 'Quantità non disponibile.'})

        cart_item.quantità = new_quantity
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
        return jsonify({'success': True, 'message': 'Quantità aggiornata con successo.'})
    else:
        return jsonify({'success': False, 'message': 'Prodotto non trovato nel carrello.'})


# Pagina per effettuare il checkout e completare l'ordine [TRASAZIONE]
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user = check_cookie()
    if user is None:
        return redirect(url_for('login'))

    user = models.Utenti.query.filter_by(idutente=login_session.get('IDUtente')).first()
    cart = models.Carrello.query.filter_by(idutente=user.idutente).order_by(models.Carrello.idprodotto).all()
    products = [
        {'prodotto': models.Prodotti.query.filter_by(idprodotto=p.idprodotto).first().titolo, 'quantità': p.quantità,
         'prezzo': models.Prodotti.query.filter_by(idprodotto=p.idprodotto).first().prezzo} for p in cart]
    totale = sum([models.Prodotti.query.get(p.idprodotto).prezzo * p.quantità for p in cart])

    if request.method == 'POST':
        # Dati dell'ordine
        destinatario = request.form['destinatario']
        email = request.form['email']
        indirizzo = request.form['indirizzo']
        città = request.form['città']
        provincia = request.form['provincia']
        cap = request.form['cap']

        card_number = request.form['ccnumber']
        card_name = request.form['ccname']
        card_expiry = request.form['ccexpiration']
        card_cvv = request.form['cccvv']

        # Controllo campi obbligatori e validità
        if destinatario == '' or email == '' or indirizzo == '' or città == '' or provincia == '' or cap == '' or card_number == '' or card_name == '' or card_expiry == '' or card_cvv == '':
            return render_template('checkout.html', user=user, products=products,
                                   total=sum([p['quantità'] * p['prezzo'] for p in products]),
                                   error="Obbligatorio compilare tutti i campi")

        if len(cap) != 5 or not cap.isdigit() or not cap.isnumeric():
            return render_template('checkout.html', user=user, products=products,
                                   total=sum([p['quantità'] * p['prezzo'] for p in products]), error="CAP non valido")

        if not card_number.isdigit() or not card_cvv.isdigit() or len(card_number) != 16 or len(card_cvv) != 3:
            return render_template('checkout.html', user=user, products=products,
                                   total=sum([p['quantità'] * p['prezzo'] for p in products]),
                                   error="Numero carta o CVV non validi")

        if not card_expiry or len(card_expiry) != 5 or not card_expiry[0:2].isdigit() or not card_expiry[
                                                                                             3:5].isdigit() or \
                card_expiry[2] != '/':
            return render_template('checkout.html', user=user, products=products,
                                   total=sum([p['quantità'] * p['prezzo'] for p in products]),
                                   error="Data di scadenza non valida")

        # Controllo disponibilità prodotti
        cart = models.Carrello.query.filter_by(idutente=user.idutente).order_by(models.Carrello.idprodotto).all()
        for c in cart:
            prod = models.Prodotti.query.get(c.idprodotto)
            if prod is not None:
                if c.quantità > prod.quantità:
                    return render_template('checkout.html', user=user, products=products,
                                           total=sum([p['quantità'] * p['prezzo'] for p in products]),
                                           error="Ordine non completato, quantità prodotti non disponibile")
            else:
                db.session.delete(c)
                db.session.commit()

        # Creazione dell'ordine
        new_order = models.Ordini(idutente=user.idutente, destinatario=destinatario, indirizzo=indirizzo, città=città,
                                  provincia=provincia, cap=cap)
        db.session.add(new_order)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template('checkout.html', user=user, products=products,
                                   total=sum([p['quantità'] * p['prezzo'] for p in products]), error=str(e))

        # Creazione dei dettagli dell'ordine
        for c in cart:
            prod = models.Prodotti.query.get(c.idprodotto)
            if prod is not None:
                new_detail = models.DettagliOrdine(idordine=new_order.idordine, idprodotto=prod.idprodotto,
                                                   titolo=prod.titolo, quantità=c.quantità, prezzo=prod.prezzo)
                db.session.add(new_detail)
                #prod.quantità -= c.quantità     #quantità prodotti modificata da un trigger
                db.session.delete(c)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return render_template('checkout.html', user=user, products=products,
                                           total=sum([p['quantità'] * p['prezzo'] for p in products]), error=str(e))

        return redirect(url_for('order_confirmation', idordine=new_order.idordine))

    return render_template('checkout.html', user=user, products=products,
                           total=sum([p['quantità'] * p['prezzo'] for p in products]))


# Pagina per visualizzare gli ordini effettuati
@app.route('/order_confirmation/<int:idordine>')
def order_confirmation(idordine):
    user = check_cookie()
    if user is None:
        return redirect(url_for('login'))

    # Controllo se l'ordine è dell'utente
    order = models.Ordini.query.get(idordine)
    if order is None or order.idutente != user.idutente:
        return redirect(url_for('profile'))

    products = models.DettagliOrdine.query.filter_by(idordine=idordine).order_by(models.DettagliOrdine.idprodotto).all()
    products = [{'prodotto': models.Prodotti.query.get(p.idprodotto), 'quantità': p.quantità} for p in products]
    return render_template('order_confirmation.html', user=user, order=order, products=products)


# Pagina per aggiungere un prodotto
@app.route('/add_product', methods=['POST', 'GET'])
def add_product():
    user = check_cookie()
    if user is None or user.ruolo != 10:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Dati del prodotto
        titolo = request.form['titolo']
        autore = request.form['autore']
        editore = request.form['editore']
        anno_pubblicazione = request.form['annoPubblicazione']
        descrizione = request.form['descrizione']
        prezzo = request.form['prezzo'].replace(',', '.')
        quantita = request.form['quantita']
        categoria = request.form['categoria']
        file = request.files['image']

        # Controllo campi obbligatori e validità
        if titolo == '' or autore == '' or editore == '' or anno_pubblicazione == '' or descrizione == '' or prezzo == '' or quantita == '' or categoria == '' or file.filename == '':
            return render_template('add_product.html', error="Obbligatorio compilare tutti i campi")

        if not prezzo.replace('.', '', 1).isdigit() or not quantita.isdigit():
            return render_template('add_product.html', error="Prezzo e quantità devono essere numeri")

        if float(prezzo) < 0 or int(quantita) < 0:
            return render_template('add_product.html', error="Prezzo e quantità devono essere maggiori di 0")

        if int(anno_pubblicazione) < 0:
            return render_template('add_product.html', error="Anno di pubblicazione non valido")

        # Nuovo prodotto
        prodotto = models.Prodotti(idvenditore=login_session.get('IDUtente'), titolo=titolo, autore=autore,
                                   editore=editore, annopubblicazione=anno_pubblicazione, descrizione=descrizione,
                                   prezzo=prezzo, quantità=quantita, categoria=categoria)
        db.session.add(prodotto)

        # Salvataggio del prodotto e dell'immagine
        try:
            db.session.commit()
            filename = secure_filename("prodotto_" + str(prodotto.idprodotto) + ".jpg")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except Exception as e:
            db.session.delete(prodotto)
            db.session.commit()
            return render_template('add_product.html', error=str(e))

        return render_template('add_product.html', succ="Prodotto aggiunto con successo")

    return render_template('add_product.html')


# Pagina per modificare un prodotto
@app.route('/edit_product/<int:idprodotto>', methods=['GET', 'POST'])
def edit_product(idprodotto):
    user = check_cookie()
    if user is None or user.ruolo != 10:
        return redirect(url_for('login'))

    # Controllo se il prodotto è del venditore
    product = models.Prodotti.query.get(idprodotto)
    if product is None or product.idvenditore != login_session.get('IDUtente'):
        return redirect(url_for('profile'))

    if request.method == 'POST':
        # Dati del prodotto
        prezzo = request.form['prezzo'].replace(',', '.')
        quantita = request.form['quantita']

        if not prezzo.replace('.', '', 1).isdigit() or not quantita.isdigit():
            return render_template('edit_product.html', error="Prezzo e quantità devono essere numeri", product=product)

        if float(prezzo) < 0 or int(quantita) < 0:
            return render_template('edit_product.html', error="Prezzo e quantità devono essere maggiori di 0",
                                   product=product)

        product.titolo = request.form['titolo']
        product.autore = request.form['autore']
        product.editore = request.form['editore']
        product.annopubblicazione = request.form['annoPubblicazione']
        product.descrizione = request.form['descrizione']
        product.prezzo = prezzo
        product.categoria = request.form['categoria']
        product.quantità = quantita

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template('edit_product.html', error=str(e), product=product)
        return redirect(url_for('profile') + '?edit=1')

    return render_template('edit_product.html', product=product)


# Eliminare un prodotto
@app.route('/delete_product/<int:idprodotto>')
def delete_product(idprodotto):
    user = check_cookie()
    if user is None or user.ruolo != 10:
        return redirect(url_for('login'))

    # Controllo se il prodotto è del venditore
    product = models.Prodotti.query.get(idprodotto)
    if product is None or product.idvenditore != login_session.get('IDUtente'):
        return redirect(url_for('profile'))

    # Eliminazione del prodotto e dell'immagine
    try:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'prodotto_{idprodotto}.jpg')
        if os.path.exists(image_path):
            os.remove(image_path)
    except Exception as e:
        return render_template('profile.html', error=str(e))

    # Eliminazione del prodotto
    db.session.delete(product)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return render_template('profile.html', error=str(e))
    return redirect(url_for('profile') + '?del=1')


#pagina per eliminare un account
@app.route('/delete_profile')
def delete_profile():
    user = check_cookie()
    if user is None:
        return redirect(url_for('login'))

    # Eliminazione dell'account - eliminazione di tutti i dati associati all'utente tramite politica di cascata
    db.session.delete(user)
    db.session.commit()

    login_session.clear()
    return render_template("login.html", succ="Account eliminato con successo")


# Pagina per visualizzare il profilo e ordini effettuati/ricevuti e prodotti in vendita
@app.route('/profile')
def profile():
    user = check_cookie()
    if user is None:
        return redirect(url_for('login'))

    # Ordini effettuati dall'utente e dati relativi
    orders = models.Ordini.query.filter_by(idutente=user.idutente).all()

    if user.ruolo == 10: # Venditore
        # Prodotti in vendita e ordini ricevuti
        products = models.Prodotti.query.filter_by(idvenditore=user.idutente).all()
        my_orders = db.session.query(
            models.Ordini.idordine,
            models.Ordini.data,
            models.Ordini.stato,
            models.DettagliOrdine.idprodotto,
            models.DettagliOrdine.quantità,
            models.DettagliOrdine.prezzo,
            models.Prodotti.titolo
        ).join(
            models.DettagliOrdine, models.Ordini.idordine == models.DettagliOrdine.idordine
        ).filter(
            models.DettagliOrdine.idprodotto.in_([p.idprodotto for p in products])
        ).join(
            models.Prodotti, models.DettagliOrdine.idprodotto == models.Prodotti.idprodotto
        ).order_by(models.Ordini.idordine).all()

        # Controllo se ci sono prodotti eliminati o modificati con successo
        if 'del' in request.args and request.args['del'] == '1':
            return render_template('profile.html', user=user, products=products, orders=orders, my_orders=my_orders,
                                   succ_product="Prodotto eliminato con successo")
        if 'edit' in request.args and request.args['edit'] == '1':
            return render_template('profile.html', user=user, products=products, orders=orders, my_orders=my_orders,
                                   succ_product="Prodotto modificato con successo")
        return render_template('profile.html', user=user, products=products, orders=orders, my_orders=my_orders)
    else:
        return render_template('profile.html', user=user, products=None, orders=orders, my_orders=None)


# Pagina per visualizzare i dettagli di un ordine
@app.route('/order/<int:idordine>')
def order(idordine):
    user = check_cookie()
    if user is None:
        return redirect(url_for('login'))

    # Controllo se l'ordine è dell'utente
    order = models.Ordini.query.get(idordine)
    if order is None or order.idutente != user.idutente:
        return redirect(url_for('profile'))

    # Dettagli dell'ordine
    products = models.DettagliOrdine.query.filter_by(idordine=idordine).order_by(models.DettagliOrdine.titolo).all()
    if not products:
        db.session.delete(order)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        return redirect(url_for('profile'))
    products = [{'titolo': p.titolo, 'quantità': p.quantità, 'prezzo': p.prezzo} for p in products]
    return render_template('order.html', user=user, order=order, products=products)


# Pagina per visualizzare i dettagli di un ordine per i venditori
@app.route('/seller_order/<int:idordine>')
def seller_order(idordine):
    user = check_cookie()
    if user is None or user.ruolo != 10:
        return redirect(url_for('login'))

    order = models.Ordini.query.get(idordine)
    if order is None:
        return redirect(url_for('profile'))

    # Dettagli dell'ordine per il venditore
    products = models.DettagliOrdine.query.filter_by(idordine=idordine).order_by(models.DettagliOrdine.idprodotto).all()
    if not products:
        db.session.delete(order)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        return redirect(url_for('profile'))
    products = [{'titolo': p.titolo, 'quantità': p.quantità, 'prezzo' : p.prezzo} for p in products]
    return render_template('seller_order.html', user=user, order=order, products=products,
                           order_user=models.Utenti.query.get(order.idutente))


# Modificare lo stato di un ordine
@app.route('/update_order_status/<int:idordine>', methods=['POST'])
def update_order_status(idordine):
    user = check_cookie()
    if user is None or user.ruolo != 10:
        return jsonify({'success': False, 'message': 'Non autorizzato'}), 401

    order = models.Ordini.query.get(idordine)
    if order is None:
        return jsonify({'success': False, 'message': 'Ordine non trovato'}), 404

    # Controllo se lo stato è valido e aggiornamento dello stato
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['1', '2', '3']:
        return jsonify({'success': False, 'message': 'Stato non valido'}), 400

    order.stato = int(new_status)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    return jsonify({'success': True, 'message': 'Stato aggiornato con successo'})


# Pagina per effettuare l'accesso
@app.route('/login', methods=['POST', 'GET'])
def login():
    user = check_cookie()
    if user is not None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Dati di accesso dell'utente e controllo validità
        if request.form['email'] != '' or request.form['password'] != '':
            email = request.form['email']
            password = request.form['password']

            # Controllo se l'utente esiste
            user_id = models.login(email, password)
            if user_id['ok'] is True:
                # Salvataggio dell'utente nella sessione e cookie
                login_session['IDUtente'] = user_id['idutente']
                login_session.permanent = True
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Email o password errati')

    return render_template('login.html')


# Pagina per effettuare il logout
@app.route('/logout')
def logout():
    login_session.clear()
    return redirect(url_for('index'))


# Pagina per registrare un nuovo utente
@app.route('/register', methods=['POST', 'GET'])
def register():
    user = check_cookie()
    if user is not None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Dati dell'utente
        nome = request.form['nome']
        cognome = request.form['cognome']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        ruolo = request.form['ruolo']

        # Controllo campi obbligatori e validità
        if nome == '' or cognome == '' or email == '' or password == '':
            return render_template('register.html', error="Obbligatorio compilare tutti i campi")

        if password != password2:
            return render_template('register.html', error="Le password non coincidono")

        if models.exist_user(email):
            return render_template('register.html', error="Utente già registrato")

        # Nuovo utente
        utente = models.Utenti(nome=nome, cognome=cognome, email=email, password=password, ruolo=ruolo)
        db.session.add(utente)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error=str(e))
        return render_template('login.html', succ="Registrazione completata con successo")

    return render_template('register.html')


# Pagina visualizzata in caso di errore 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Pagina visualizzata in caso di errore 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# Pagina visualizzata in caso di errore 405
@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405


# Avvio dell'applicazione
if __name__ == '__main__':
    app.run(debug=True)

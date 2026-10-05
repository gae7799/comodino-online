# -*- coding: utf-8 -*-
"""Comodino online: servizio separato da Sentinella, con la sua storia,
il suo repository e il suo indirizzo su Railway.

Non fa altro che agganciare le due parti gia' scritte:

    comodino.py         le due pagine pubbliche (home + privacy per Google)
    comodino_app.py      la cassaforte: accesso con Google, e il foglio
                         che il PC di casa deposita

Variabili d'ambiente da mettere nel servizio (mai qui dentro):

    COMODINO_CLIENT_ID       client OAuth "Applicazione web"
    COMODINO_CLIENT_SECRET   il suo segreto
    COMODINO_EMAIL           l'unica mail ammessa (tu)
    COMODINO_DEPOSITO        la parola con cui il PC deposita il foglio
    CHIAVE_SESSIONE          facoltativa: se manca, la chiave delle sessioni si
                             ricava dal segreto Google, cosi' resta la stessa
                             a ogni riavvio e l'accesso non si perde
"""

import datetime
import hashlib
import hmac
import os

from flask import Flask, redirect

import comodino
import comodino_app

def _chiave_di_sessione():
    """(chiave, stabile). La chiave firma il cookie dell'accesso: se cambia a
    ogni avvio, ogni riavvio del servizio ti riporta alla schermata di login.
    Per questo, se CHIAVE_SESSIONE non c'e', la si ricava (HMAC) da un segreto
    che sul servizio c'e' gia' e non cambia."""
    scelta = (os.environ.get('CHIAVE_SESSIONE') or '').strip()
    if scelta:
        return scelta, True
    base = (os.environ.get('COMODINO_CLIENT_SECRET')
            or os.environ.get('COMODINO_DEPOSITO') or '').strip()
    if base:
        return hmac.new(base.encode('utf-8'), b'comodino-sessione-v1',
                        hashlib.sha256).hexdigest(), True
    return os.urandom(24).hex(), False


AVVIATA = datetime.datetime.now(datetime.timezone.utc)
app = Flask(__name__)
app.secret_key, CHIAVE_STABILE = _chiave_di_sessione()

comodino.aggancia(app)
comodino_app.aggancia(app)

# Chi entra resta dentro un anno, non i 31 giorni predefiniti di Flask.
app.permanent_session_lifetime = datetime.timedelta(days=365)


@app.route('/')
def casa():
    return redirect('/comodino')


@app.route('/salute')
def salute():
    # Dice solo da quando e' acceso e se l'accesso sopravvive ai riavvii:
    # serve a vedere se il servizio si riavvia spesso.
    return ('viva - avviata %s UTC - accesso %s' % (
        AVVIATA.strftime('%Y-%m-%d %H:%M'),
        'stabile' if CHIAVE_STABILE else 'si perde a ogni riavvio')), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8772)))

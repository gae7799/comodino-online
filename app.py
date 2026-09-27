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
    CHIAVE_SESSIONE          facoltativa: se manca, se ne genera una ad ogni
                             riavvio e le sessioni aperte si perdono
"""

import datetime
import os

from flask import Flask, redirect

import comodino
import comodino_app

app = Flask(__name__)
app.secret_key = os.environ.get('CHIAVE_SESSIONE') or os.urandom(24).hex()

comodino.aggancia(app)
comodino_app.aggancia(app)

# Chi entra resta dentro un anno, non i 31 giorni predefiniti di Flask.
app.permanent_session_lifetime = datetime.timedelta(days=365)


@app.route('/')
def casa():
    return redirect('/comodino')


@app.route('/salute')
def salute():
    return 'viva', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8772)))

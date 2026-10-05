# -*- coding: utf-8 -*-
"""Comodino online: la cassaforte che mostra la pagina solo a chi la possiede.

**Questo servizio non calcola niente.** I conti li fa il PC di casa, che
disegna la pagina e la deposita qui. Qui dentro c'e' solo: chi sei, e l'ultimo
foglio che il PC ha mandato.

E' voluto. Un secondo programma che ricalcola gli stessi numeri sarebbe un
doppione da tenere allineato per sempre, e il giorno che i due non tornassero
non sapresti a quale credere.

    /comodino/app        la pagina (solo tu)
    /comodino/entra      "Accedi con Google"
    /comodino/entrato    dove Google ti riporta
    /comodino/esci       sloggati
    /comodino/deposita   il PC deposita (POST, con la sua parola)

**Niente disco.** Il foglio sta in memoria: se il servizio riparte, la pagina
resta vuota finche' il PC non ripubblica. Nessun dato di salute viene scritto
su nessun disco che non sia quello di casa.

Variabili d'ambiente:

    COMODINO_CLIENT_ID       client OAuth "Applicazione web"
    COMODINO_CLIENT_SECRET   il suo segreto
    COMODINO_EMAIL           l'unica mail ammessa
    COMODINO_DEPOSITO        la parola con cui il PC deposita
"""

import base64
import datetime
import hmac
import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request

from flask import redirect, request, session

import google_health

try:      # i conti sono gli stessi di casa: file copiati da sincronizza-online.py
    import lettura
    import modello
    CONTI_PRONTI = True
except ImportError:
    CONTI_PRONTI = False

AUTORIZZA = 'https://accounts.google.com/o/oauth2/v2/auth'
GETTONI = 'https://oauth2.googleapis.com/token'
ORE_DI_VITA_FOGLIO = 48          # oltre, il foglio e' vecchio e si dice

# L'ultimo foglio depositato dal PC. In memoria, e basta.
_foglio = {'html': None, 'quando': None}


def _serve(nome):
    return (os.environ.get(nome) or '').strip()


# L'ultima pagina disegnata coi dati letti da Google. In memoria, e basta.
_vivo = {'html': None, 'quando': None}


def _cache_secondi():
    try:
        return max(0, int(_serve('CACHE_SECONDI') or 120))
    except ValueError:
        return 120


def _configurato():
    return bool(_serve('COMODINO_CLIENT_ID') and _serve('COMODINO_CLIENT_SECRET')
                and _serve('COMODINO_EMAIL'))


def _indirizzo_di_ritorno():
    """Dove Google ti riporta. Si ricava dalla richiesta, cosi' funziona sia
    sul servizio vero sia in prova, senza una variabile in piu' da sbagliare."""
    radice = request.url_root.rstrip('/')
    if radice.startswith('http://') and 'localhost' not in radice and '127.0.0.1' not in radice:
        radice = 'https://' + radice[len('http://'):]      # Railway parla https
    return radice + '/comodino/entrato'


def _pezzo_del_gettone(id_token):
    """L'email sta dentro l'id_token. Non lo verifico con la firma: questo
    gettone non arriva dal browser, arriva da una chiamata diretta ai server
    di Google su TLS. Se quella e' compromessa, non c'e' firma che tenga."""
    try:
        corpo = id_token.split('.')[1]
        corpo += '=' * (-len(corpo) % 4)
        return json.loads(base64.urlsafe_b64decode(corpo).decode('utf-8'))
    except (IndexError, ValueError, UnicodeDecodeError):
        return {}


def _quanto_fa(quando):
    if not quando:
        return None
    minuti = int((datetime.datetime.now(datetime.timezone.utc) - quando).total_seconds() // 60)
    if minuti < 2:
        return 'adesso'
    if minuti < 60:
        return '%d minuti fa' % minuti
    ore = minuti // 60
    if ore < 24:
        return '%d or%s fa' % (ore, 'a' if ore == 1 else 'e')
    giorni = ore // 24
    return '%d giorn%s fa' % (giorni, 'o' if giorni == 1 else 'i')


def _vecchio():
    quando = _foglio['quando']
    if not quando:
        return True
    return (datetime.datetime.now(datetime.timezone.utc) - quando).total_seconds() > ORE_DI_VITA_FOGLIO * 3600


# ---------------------------------------------------------------- le schermate

_STILE = """
  :root{--fondo:#11151c;--testo:#e8e6e1;--spento:#7b8794;--accento:#c9a227;
        --riquadro:#171d26;--riga:#232b37;--rosso:#b5533f}
  *{box-sizing:border-box}
  body{margin:0;background:var(--fondo);color:var(--testo);
       font:16px/1.7 -apple-system,"Segoe UI",system-ui,sans-serif}
"""

_ENTRA = """<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Comodino</title><style>%s
  body{display:flex;min-height:100vh;align-items:center;justify-content:center;
       padding:24px;text-align:center}
  .dentro{width:min(340px,92vw)}
  svg{margin-bottom:22px}
  h1{font-size:14px;letter-spacing:.24em;text-transform:uppercase;
     color:var(--spento);font-weight:500;margin:0 0 30px}
  a.entra{display:block;padding:14px;background:var(--accento);color:#11151c;
     border-radius:3px;text-decoration:none;font-weight:600;font-size:16px}
  .no{color:var(--rosso);font-size:13.5px;margin-top:18px;line-height:1.6}
  .nota{color:var(--spento);font-size:12.5px;margin-top:22px;line-height:1.6}
</style></head><body><div class="dentro">
<svg width="56" height="56" viewBox="0 0 120 120"><circle cx="60" cy="50" r="28"
 fill="#c9a227"/><rect x="20" y="88" width="80" height="6" rx="3" fill="#c9a227"/></svg>
<h1>Comodino</h1>
%s
<p class="nota">Questa pagina la vede un solo account.
Nessun altro entra, nemmeno con il link.</p>
</div></body></html>"""

_CORNICE = """<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Comodino</title><style>%s
  .barra{position:sticky;top:0;z-index:9;display:flex;align-items:center;gap:12px;
         justify-content:space-between;padding:9px 16px;background:#0d1117;
         border-bottom:1px solid var(--riga);font-size:12.5px;color:var(--spento)}
  .barra a{color:var(--spento)}
  .fresco{color:var(--accento)} .stantio{color:var(--rosso)}
  iframe{display:block;width:100%%;height:calc(100vh - 41px);border:0;background:var(--fondo)}
  .vuoto{padding:60px 22px;text-align:center;color:var(--spento);line-height:1.8}
  .avviso{padding:10px 16px;background:#2a1f12;border-bottom:1px solid var(--riga);
          font-size:13.5px;line-height:1.6;color:#e0c48a}
  .avviso a,.barra a.tasto{color:var(--accento)}
  .barra form{display:inline;margin:0}
  .barra button{background:none;border:0;padding:0;font:inherit;color:var(--spento);
                text-decoration:underline;cursor:pointer}
</style></head><body>
<div class="barra">
  <span>%s <b class="%s">%s</b></span>
  <span>%s <a href="/comodino/esci">esci</a></span>
</div>
%s
%s
</body></html>"""


def _schermata_entra(guaio=None):
    if not _configurato():
        corpo = ('<p class="no">Il servizio non e ancora configurato.<br>'
                 'Mancano le variabili d ambiente di Comodino.</p>')
    elif guaio:
        corpo = ('<a class="entra" href="/comodino/entra">Accedi con Google</a>'
                 '<p class="no">%s</p>' % guaio)
    else:
        corpo = '<a class="entra" href="/comodino/entra">Accedi con Google</a>'
    return _ENTRA % (_STILE, corpo)


def _incornicia(html, quando, etichetta, extra='', avviso=''):
    if not html:
        dentro = ('<div class="vuoto">Il computer di casa non ha ancora depositato niente.<br>'
                  'La pagina compare al primo scarico, o lanciando <b>pubblica.bat</b>.</div>')
    else:
        dentro = '<iframe srcdoc="%s"></iframe>' % (
            html.replace('&', '&amp;').replace('"', '&quot;'))
    vecchio = (not quando) or (
        datetime.datetime.now(datetime.timezone.utc) - quando).total_seconds() > ORE_DI_VITA_FOGLIO * 3600
    return _CORNICE % (_STILE, etichetta, 'stantio' if vecchio else 'fresco',
                       _quanto_fa(quando) or 'mai', extra,
                       ('<div class="avviso">%s</div>' % avviso) if avviso else '', dentro)


def _schermata_app(avviso=''):
    """La pagina depositata dal PC. E' la riserva: serve quando Google non e
    collegato o non risponde."""
    return _incornicia(_foglio['html'], _foglio['quando'], 'foglio del PC, aggiornato', '', avviso)


def _disegna_dal_vivo():
    """Legge Google, fa i conti, disegna. Puo' alzare DaCollegare o NonRaggiungibile."""
    righe = google_health.righe_dal_vivo()
    conti = lettura.statistiche(lettura.notti(righe))
    return modello.disegna(conti, dal_vivo=True, per_online=True)


def _schermata_vivo(forza=False):
    ora = datetime.datetime.now(datetime.timezone.utc)
    if (not forza and _vivo['html'] and
            (ora - _vivo['quando']).total_seconds() < _cache_secondi()):
        return _incornicia(_vivo['html'], _vivo['quando'], 'letto da Google Health',
                           _tasto_scollega())
    try:
        html = _disegna_dal_vivo()
    except google_health.DaCollegare:
        return _schermata_app('Il permesso di Google Health non vale piu. '
                              '<a href="/comodino/collega">Collegalo di nuovo</a>.')
    except google_health.NonRaggiungibile as guaio:
        if _vivo['html']:
            return _incornicia(_vivo['html'], _vivo['quando'], 'ultima lettura da Google',
                               _tasto_scollega(),
                               'Google non risponde adesso (%s). Questa e l ultima lettura riuscita.' % guaio)
        return _schermata_app('Google non risponde adesso (%s). Ti mostro il foglio del PC.' % guaio)
    _vivo['html'], _vivo['quando'] = html, ora
    return _incornicia(html, ora, 'letto da Google Health', _tasto_scollega())


def _tasto_scollega():
    return ('<form method="post" action="/comodino/scollega">'
            '<button type="submit">scollega</button></form> &middot; '
            '<a href="/comodino/app?ricarica=1">ricarica</a>')


# ---------------------------------------------------------------- le rotte

def aggancia(app):

    def _e_lui():
        return session.get('comodino_email') and \
            session['comodino_email'].lower() == _serve('COMODINO_EMAIL').lower()

    @app.route('/comodino/app')
    def comodino_app():
        if not _e_lui():
            return _schermata_entra()
        if request.args.get('foglio') == 'pc':
            return _schermata_app()
        if CONTI_PRONTI and google_health.e_collegato():
            return _schermata_vivo(forza=(request.args.get('ricarica') == '1'))
        if not CONTI_PRONTI:
            return _schermata_app()
        return _schermata_app('Google Health non e ancora collegato: finche non lo colleghi '
                              'vedi il foglio depositato dal PC. '
                              '<a href="/comodino/collega">Collega Google Health</a>.')

    @app.route('/comodino/collega')
    def comodino_collega():
        if not _e_lui():
            return _schermata_entra()
        stato = secrets.token_urlsafe(24)
        session['comodino_stato'] = stato
        session['comodino_collega'] = True
        domanda = urllib.parse.urlencode({
            'client_id': _serve('COMODINO_CLIENT_ID'),
            'redirect_uri': _indirizzo_di_ritorno(),
            'response_type': 'code',
            'scope': 'openid email ' + google_health.SCOPE_SONNO,
            'state': stato,
            'access_type': 'offline',
            'prompt': 'consent',
            'login_hint': _serve('COMODINO_EMAIL'),
        })
        return redirect('%s?%s' % (AUTORIZZA, domanda))

    @app.route('/comodino/scollega', methods=['POST'])
    def comodino_scollega():
        if not _e_lui():
            return _schermata_entra(), 403
        google_health.dimentica()
        _vivo['html'] = _vivo['quando'] = None
        return redirect('/comodino/app')

    @app.route('/comodino/entra')
    def comodino_entra():
        if not _configurato():
            return _schermata_entra(), 503
        stato = secrets.token_urlsafe(24)
        session['comodino_stato'] = stato
        session.pop('comodino_collega', None)
        session.permanent = True
        domanda = urllib.parse.urlencode({
            'client_id': _serve('COMODINO_CLIENT_ID'),
            'redirect_uri': _indirizzo_di_ritorno(),
            'response_type': 'code',
            'scope': 'openid email',
            'state': stato,
            'prompt': 'select_account',
        })
        return redirect('%s?%s' % (AUTORIZZA, domanda))

    @app.route('/comodino/entrato')
    def comodino_entrato():
        atteso = session.pop('comodino_stato', None)
        collegando = session.pop('comodino_collega', False)
        if not atteso or request.args.get('state') != atteso:
            return _schermata_entra('La richiesta non combacia. Riprova.'), 400
        codice = request.args.get('code')
        if not codice:
            return _schermata_entra('Google non ha dato nessun codice.'), 400

        corpo = urllib.parse.urlencode({
            'code': codice,
            'client_id': _serve('COMODINO_CLIENT_ID'),
            'client_secret': _serve('COMODINO_CLIENT_SECRET'),
            'redirect_uri': _indirizzo_di_ritorno(),
            'grant_type': 'authorization_code',
        }).encode('ascii')
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(GETTONI, data=corpo, method='POST'),
                    timeout=20) as r:
                risposta = json.loads(r.read().decode('utf-8'))
        except (urllib.error.URLError, OSError, ValueError):
            return _schermata_entra('Non sono riuscito a parlare con Google. Riprova.'), 502

        email = (_pezzo_del_gettone(risposta.get('id_token') or '').get('email') or '').strip()
        if not email:
            return _schermata_entra('Google non ha detto chi sei.'), 400
        if email.lower() != _serve('COMODINO_EMAIL').lower():
            # Detto senza girarci intorno, e senza nominare la mail ammessa.
            return _schermata_entra('Questo account non e ammesso qui.'), 403

        if collegando:
            if 'googlehealth.sleep' not in (risposta.get('scope') or ''):
                return _schermata_entra('Il permesso sul sonno non e stato dato. '
                                        'Riprova e lascia la spunta sul sonno.'), 400
            rinnovo = risposta.get('refresh_token')
            if not rinnovo:
                return _schermata_entra('Google non ha dato il permesso duraturo. '
                                        'Riprova: se succede ancora, togli Comodino dai '
                                        'permessi del tuo account Google e ricollega.'), 400
            try:
                google_health.salva_collegamento(rinnovo)
            except OSError:
                return _schermata_entra('Non riesco a ricordare il permesso: manca il '
                                        'Volume su Railway (DATI_DIR).'), 500
            session['comodino_email'] = email
            session.permanent = True
            _vivo['html'] = _vivo['quando'] = None
            return redirect('/comodino/app')

        session['comodino_email'] = email
        session.permanent = True
        return redirect('/comodino/app')

    @app.route('/comodino/esci')
    def comodino_esci():
        session.pop('comodino_email', None)
        return redirect('/comodino/app')

    @app.route('/comodino/deposita', methods=['POST'])
    def comodino_deposita():
        """Il PC deposita il foglio. Risponde in JSON: e' un programma che
        chiama, non una persona."""
        parola = _serve('COMODINO_DEPOSITO')
        detta = (request.form.get('parola') or '').strip()
        if not parola or not hmac.compare_digest(detta, parola):
            return {'errore': 'parola'}, 403
        html = request.form.get('foglio') or ''
        if not html.strip():
            return {'errore': 'foglio vuoto'}, 400
        _foglio['html'] = html
        _foglio['quando'] = datetime.datetime.now(datetime.timezone.utc)
        return {'ricevuto': len(html), 'quando': _foglio['quando'].isoformat()}

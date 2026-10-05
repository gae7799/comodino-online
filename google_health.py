# -*- coding: utf-8 -*-
"""Il servizio legge il sonno da Google Health, direttamente, a ogni apertura.

Il permesso lo da' il titolare con un tasto ("Collega Google Health") e resta
in un file nella cartella dei dati del servizio (un Volume su Railway, vedi
DATI_DIR). In quel file c'e' solo il gettone di rinnovo: nessun dato di salute.

I dati di sonno letti NON si scrivono su nessun disco: si convertono in righe
(le stesse dei CSV di casa, tramite sonno_righe.py), si fanno i conti con lo
stesso lettura.py di casa, e restano in memoria per un paio di minuti.

Variabili d'ambiente:

    COMODINO_CLIENT_ID / COMODINO_CLIENT_SECRET   il client OAuth web, gia' esistente
    DATI_DIR      dove sta il permesso (default: /data se esiste, altrimenti ./dati)
    DATI_DAL      primo giorno da leggere (default 2026-09-20: il Fitbit parte li').
                  I cicli di 30 giorni si contano dalla prima notte, quindi la
                  data di partenza deve restare fissa e non scorrere.
    FUSO_ORARIO   default Europe/Rome
"""

import datetime
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from sonno_righe import righe_di_sonno

API = 'https://health.googleapis.com/v4'
GETTONI = 'https://oauth2.googleapis.com/token'
REVOCA = 'https://oauth2.googleapis.com/revoke'
# Preso dal codice di google-health-cli (Google-Health-API/google-health-cli)
SCOPE_SONNO = 'https://www.googleapis.com/auth/googlehealth.sleep.readonly'
FINESTRA = 90          # giorni per richiesta: come fa lo scarico di casa
PAGINE_MAX = 60


class DaCollegare(Exception):
    """Manca il permesso, o Google lo ha tolto."""


class NonRaggiungibile(Exception):
    """Google non risponde adesso. Il permesso, per quanto ne sappiamo, e' buono."""


def _serve(nome):
    return (os.environ.get(nome) or '').strip()


def fuso():
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(_serve('FUSO_ORARIO') or 'Europe/Rome')
    except Exception:
        return datetime.timezone.utc


# ------------------------------------------------------------ il permesso

def cartella_dati():
    scelta = _serve('DATI_DIR')
    if scelta:
        return scelta
    if os.path.isdir('/data') and os.access('/data', os.W_OK):
        return '/data'
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dati')


def _percorso():
    return os.path.join(cartella_dati(), 'google_salute.json')


_accesso = {}      # il gettone di accesso, a vita breve, solo in memoria


def collegamento():
    try:
        with open(_percorso(), encoding='utf-8') as f:
            dati = json.load(f)
    except (OSError, ValueError):
        return None
    return dati if dati.get('refresh_token') else None


def e_collegato():
    return collegamento() is not None


def salva_collegamento(refresh_token):
    """Scrive il permesso. Se la cartella non si puo' scrivere solleva OSError:
    di solito vuol dire che sul servizio manca il Volume."""
    cartella = cartella_dati()
    os.makedirs(cartella, exist_ok=True)
    percorso = _percorso()
    provvisorio = percorso + '.nuovo'
    fd = os.open(provvisorio, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump({'refresh_token': refresh_token,
                   'collegato_il': datetime.datetime.now(datetime.timezone.utc).isoformat()}, f)
    os.replace(provvisorio, percorso)
    _accesso.clear()


def dimentica():
    """Scollega: revoca il permesso presso Google, se riesce, e cancella il file.
    Restituisce True se Google ha confermato la revoca."""
    dati = collegamento()
    revocato = False
    if dati:
        try:
            _chiama(REVOCA, {'token': dati['refresh_token']})
            revocato = True
        except (DaCollegare, NonRaggiungibile):
            pass
    try:
        os.remove(_percorso())
    except OSError:
        pass
    _accesso.clear()
    return revocato


# ------------------------------------------------------------ parlare con Google

def _chiama(url, dati):
    """POST in forma di modulo. Restituisce il JSON, o {} se la risposta e' vuota."""
    corpo = urllib.parse.urlencode(dati).encode('ascii')
    try:
        with urllib.request.urlopen(
                urllib.request.Request(url, data=corpo, method='POST'), timeout=20) as r:
            testo = r.read().decode('utf-8')
    except urllib.error.HTTPError as guaio:
        dettaglio = ''
        try:
            dettaglio = guaio.read().decode('utf-8')
        except (OSError, UnicodeDecodeError):
            pass
        if guaio.code in (400, 401) and 'invalid_grant' in dettaglio:
            raise DaCollegare('scaduto')
        raise NonRaggiungibile('Google ha risposto %d' % guaio.code)
    except (urllib.error.URLError, OSError):
        raise NonRaggiungibile('non raggiungo Google')
    try:
        return json.loads(testo) if testo.strip() else {}
    except ValueError:
        raise NonRaggiungibile('risposta di Google illeggibile')


def token_di_accesso():
    dati = collegamento()
    if not dati:
        raise DaCollegare('non_collegato')
    if _accesso.get('tok') and _accesso.get('scade', 0) > time.time() + 60:
        return _accesso['tok']
    risposta = _chiama(GETTONI, {
        'client_id': _serve('COMODINO_CLIENT_ID'),
        'client_secret': _serve('COMODINO_CLIENT_SECRET'),
        'refresh_token': dati['refresh_token'],
        'grant_type': 'refresh_token',
    })
    if not risposta.get('access_token'):
        raise NonRaggiungibile('Google non ha dato il gettone')
    _accesso['tok'] = risposta['access_token']
    _accesso['scade'] = time.time() + int(risposta.get('expires_in') or 3600)
    return _accesso['tok']


def _leggi(percorso, parametri):
    url = '%s%s?%s' % (API, percorso, urllib.parse.urlencode(parametri))
    richiesta = urllib.request.Request(
        url, headers={'Authorization': 'Bearer ' + token_di_accesso()})
    try:
        with urllib.request.urlopen(richiesta, timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as guaio:
        if guaio.code == 401:
            _accesso.clear()
            raise DaCollegare('scaduto')
        raise NonRaggiungibile('Google ha risposto %d' % guaio.code)
    except (urllib.error.URLError, OSError):
        raise NonRaggiungibile('non raggiungo Google')
    except ValueError:
        raise NonRaggiungibile('risposta di Google illeggibile')


# ------------------------------------------------------------ il sonno

def sonno_grezzo(dal):
    """Tutte le sessioni di sonno dal giorno `dal` a oggi, a finestre di 90
    giorni. Il sonno esce a 25 righe per pagina: si seguono le pagine."""
    oggi = datetime.datetime.now(fuso()).date()
    limite = oggi + datetime.timedelta(days=1)          # estremo escluso
    punti, inizio = [], dal
    while inizio <= oggi:
        fine = min(inizio + datetime.timedelta(days=FINESTRA), limite)
        filtro = ('sleep.interval.civil_end_time >= "%sT00:00:00" AND '
                  'sleep.interval.civil_end_time < "%sT00:00:00"' % (inizio, fine))
        parametri = {'filter': filtro, 'pageSize': '25'}
        for _ in range(PAGINE_MAX):
            risposta = _leggi('/users/me/dataTypes/sleep/dataPoints', parametri)
            punti += risposta.get('dataPoints') or []
            gettone = risposta.get('nextPageToken')
            if not gettone:
                break
            parametri = dict(parametri, pageToken=gettone)
        inizio = fine
    return punti


def _num(valore):
    try:
        return int(float(valore))
    except (TypeError, ValueError):
        return 0


def _locale(intervallo, chiave, chiave_scarto):
    """L'istante UTC di Google, portato all'ora del posto: 08:29Z + 7200s ->
    10:29+02:00. Stesso criterio di ghealth."""
    istante = intervallo.get(chiave) or ''
    if not istante:
        return ''
    scarto = _num(str(intervallo.get(chiave_scarto) or '0').rstrip('s'))
    if scarto == 0:
        return istante
    try:
        t = datetime.datetime.fromisoformat(
            re.sub(r'(\.\d{6})\d+', r'\1', istante).replace('Z', '+00:00'))
    except ValueError:
        return istante
    return t.astimezone(datetime.timezone(datetime.timedelta(seconds=scarto))
                        ).isoformat(timespec='seconds')


def semplifica(punto):
    """Da una sessione come la manda Google alla forma che righe_di_sonno si
    aspetta, la stessa che lo scarico di casa riceve da ghealth."""
    sonno = punto.get('sleep') or {}
    intervallo = sonno.get('interval') or {}
    riassunto = sonno.get('summary') or {}
    fuori = {'start': _locale(intervallo, 'startTime', 'startUtcOffset'),
             'end': _locale(intervallo, 'endTime', 'endUtcOffset'),
             'source': ''}
    for da, a in (('minutesAsleep', 'minutesAsleep'), ('minutesAwake', 'minutesAwake'),
                  ('minutesInSleepPeriod', 'totalMinutes'),
                  ('minutesToFallAsleep', 'minutesToFallAsleep')):
        if da in riassunto:
            fuori[a] = _num(riassunto[da])
    fuori['stageMinutes'] = {f.get('type'): _num(f.get('minutes'))
                             for f in (riassunto.get('stagesSummary') or []) if f.get('type')}
    if 'type' in sonno:
        fuori['sleepType'] = sonno['type']
    if (sonno.get('metadata') or {}).get('nap') is not None:
        fuori['isNap'] = sonno['metadata']['nap']
    return fuori


def righe_dal_vivo():
    """Le righe di sonno, una per giorno, come quelle dei CSV di casa."""
    dal = datetime.date.fromisoformat(_serve('DATI_DAL') or '2026-09-20')
    return righe_di_sonno([semplifica(p) for p in sonno_grezzo(dal)])

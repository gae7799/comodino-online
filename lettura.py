# -*- coding: utf-8 -*-
"""I conti sul sonno. Solo libreria standard: niente Flask qui dentro.

Questo modulo si puo' far girare da solo (`python lettura.py`) e stampa il
rapporto a schermo. Se un giorno la pagina si rompe, i numeri restano
raggiungibili. E' la stessa regola della cartella: il formato sopravvive al
programma.

Il principio dei conti: **il metro sei tu.** Non esiste qui dentro un numero
di ore "giuste". Tutto e' misurato rispetto alla tua media del periodo.
Il programma conta, non da' voti.
"""

import csv
import datetime
import glob
import os

# Sotto questa soglia i conti non si fanno. Non e' prudenza: una media di
# tre notti non e' una media, e un "accumulo rispetto alla tua media" con la
# media costruita su quelle stesse tre notti e' un numero che finge.
#
# Ma **il numero lo scegli tu**, in configurazione.json ->
# "notti_perche_i_conti_abbiano_senso". Quattordici e' solo il valore di
# partenza: se lo metti a 3, i grafici compaiono con tre notti, e sono veri
# -- semplicemente non dicono ancora granche'.
def _soglia():
    import json
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'configurazione.json'), encoding='utf-8') as f:
            return int(json.load(f).get('notti_perche_i_conti_abbiano_senso') or 14)
    except (OSError, ValueError, TypeError):
        return 14

def _giorni_ciclo():
    """Quanto dura un ciclo. La media di riferimento si stabilisce a ciclo
    chiuso. Il numero e' tuo: configurazione.json -> "giorni_del_ciclo"."""
    import json
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'configurazione.json'), encoding='utf-8') as f:
            return max(7, int(json.load(f).get('giorni_del_ciclo') or 30))
    except (OSError, ValueError, TypeError):
        return 30


QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(os.path.dirname(QUI))          # secondo-cervello
SALUTE = os.path.join(RADICE, 'salute')
STORICO_SCANNER = os.path.join(RADICE, 'progetti', 'storico.csv')


# ============================================================  leggere i file

def _numero(valore, virgola=False):
    try:
        return float(valore) if virgola else int(float(valore))
    except (TypeError, ValueError):
        return None


def _ora(testo):
    try:
        ore, minuti = testo.strip().split(':')[:2]
        return int(ore) * 60 + int(minuti)
    except (AttributeError, ValueError):
        return None


def carica(ramo):
    """Tutti i CSV di un ramo (sonno, attivita), tutti gli anni, in ordine.

    Un file illeggibile non ferma gli altri: la pagina deve aprirsi anche
    quando un file e' a meta'."""
    righe = []
    for percorso in sorted(glob.glob(os.path.join(SALUTE, ramo, '*', '*.csv'))):
        try:
            with open(percorso, newline='', encoding='utf-8-sig') as f:
                for riga in csv.DictReader(f):
                    if riga.get('data'):
                        righe.append(riga)
        except (OSError, csv.Error):
            continue
    visti = {}
    for riga in righe:
        visti[riga['data']] = riga        # se una notte c'e' due volte, vince l'ultima
    return [visti[d] for d in sorted(visti)]


def notti(righe=None):
    """Le notti, dalle righe date o, se non ce ne sono, dai CSV di casa.
    Il servizio online passa qui le righe lette da Google Health."""
    fuori = []
    for riga in (carica('sonno') if righe is None else righe):
        minuti = _numero(riga.get('minuti_dormiti'))
        if not minuti:
            continue
        try:
            data = datetime.date.fromisoformat(riga['data'])
        except ValueError:
            continue
        fuori.append({
            'data': data,
            'minuti': minuti,
            'a_letto': _ora(riga.get('a_letto')),
            'sveglia': _ora(riga.get('sveglia')),
            'efficienza': _numero(riga.get('efficienza')),
            'profondo': _numero(riga.get('profondo_min')),
            'rem': _numero(riga.get('rem_min')),
            'risvegli': _numero(riga.get('risvegli')),
            'sessioni': _numero(riga.get('sessioni')) or 1,
            'festivo': data.weekday() >= 5,
        })
    return fuori


# ============================================================  dire le ore

def ore(minuti, segno=False):
    """6h 32m. Col segno quando e' uno scarto: +2h 10m, -11h 45m."""
    if minuti is None:
        return '--'
    minuti = int(round(minuti))
    if segno:
        davanti = '+' if minuti >= 0 else '-'
    else:
        davanti = '' if minuti >= 0 else '-'    # un meno non si perde mai per strada
    minuti = abs(minuti)
    return '%s%dh %02dm' % (davanti, minuti // 60, minuti % 60)


def orologio(minuti):
    """I minuti dalla mezzanotte tornano 23:40. Oltre le 24 rientrano."""
    if minuti is None:
        return '--'
    minuti = int(round(minuti)) % (24 * 60)
    return '%02d:%02d' % (minuti // 60, minuti % 60)


def _sposta_notte(minuti):
    """Per fare la media dell'ora in cui ti addormenti, le 23:50 e le 00:20
    devono stare vicine, non a 23 ore di distanza. Porto tutto su un asse
    che parte dalle 18:00: le 23:50 diventano 350, le 00:20 diventano 380."""
    if minuti is None:
        return None
    return minuti - 18 * 60 if minuti >= 12 * 60 else minuti + 6 * 60


def _media(elenco):
    puliti = [x for x in elenco if x is not None]
    return sum(puliti) / float(len(puliti)) if puliti else None


# ============================================================  le statistiche

def statistiche(elenco=None):
    elenco = elenco if elenco is not None else notti()
    if not elenco:
        return {'vuoto': True}

    minuti = [n['minuti'] for n in elenco]
    media = sum(minuti) / float(len(minuti))

    # --- l'accumulo, giorno per giorno. E' la curva principale.
    accumulo, somma = [], 0.0
    for n in elenco:
        somma += n['minuti'] - media
        accumulo.append({'data': n['data'].isoformat(),
                         'minuti': n['minuti'],
                         'scarto': n['minuti'] - media,
                         'accumulato': somma,
                         'festivo': n['festivo']})

    # --- media mobile a sette giorni: la linea che toglie il rumore
    for indice, voce in enumerate(accumulo):
        finestra = minuti[max(0, indice - 6):indice + 1]
        voce['mobile7'] = sum(finestra) / float(len(finestra))

    # --- le settimane, sommate. Una riga per settimana ISO.
    settimane = {}
    for n in elenco:
        anno, numero, _ = n['data'].isocalendar()
        chiave = '%d-W%02d' % (anno, numero)
        voce = settimane.setdefault(chiave, {'settimana': chiave, 'minuti': 0,
                                             'notti': 0, 'dal': n['data'], 'al': n['data']})
        voce['minuti'] += n['minuti']
        voce['notti'] += 1
        voce['dal'] = min(voce['dal'], n['data'])
        voce['al'] = max(voce['al'], n['data'])
    ordinate = [settimane[k] for k in sorted(settimane)]
    for indice, voce in enumerate(ordinate):
        voce['dal'] = voce['dal'].isoformat()
        voce['al'] = voce['al'].isoformat()
        voce['completa'] = voce['notti'] >= 7
        precedente = ordinate[indice - 1] if indice else None
        voce['differenza'] = (voce['minuti'] - precedente['minuti']) if precedente else None
        # a notte: quattro notti non si confrontano con sette, a notte si'
        voce['a_notte'] = voce['minuti'] / float(voce['notti'])
        voce['differenza_a_notte'] = (voce['a_notte'] - precedente['a_notte']) if precedente else None

    # --- le strisce: quante notti di fila sotto la tua media
    striscia, record_striscia, quando_record = 0, 0, None
    for n in elenco:
        if n['minuti'] < media:
            striscia += 1
            if striscia > record_striscia:
                record_striscia, quando_record = striscia, n['data']
        else:
            striscia = 0
    striscia_ora = 0
    for n in reversed(elenco):
        if n['minuti'] < media:
            striscia_ora += 1
        else:
            break

    # --- le notti che mancano: i buchi nel calendario, non i giorni brutti
    primo, ultimo = elenco[0]['data'], elenco[-1]['data']
    giorni_totali = (ultimo - primo).days + 1
    mancanti = giorni_totali - len(elenco)

    # --- a che ora ti addormenti, e di quanto slitta nel fine settimana
    spostate = [(_sposta_notte(n['a_letto']), n['festivo']) for n in elenco if n['a_letto'] is not None]
    feriali = [x for x, festivo in spostate if not festivo]
    festivi = [x for x, festivo in spostate if festivo]
    media_letto = _media([x for x, _ in spostate])
    media_feriale, media_festiva = _media(feriali), _media(festivi)
    irregolarita = _media([abs(x - media_letto) for x, _ in spostate]) if media_letto is not None else None

    # --- il punto piu' basso della curva. L'accumulo sull'INTERO periodo
    # vale sempre zero per costruzione (gli scarti da una media si annullano):
    # il numero che conta non e' dove finisce la curva, e' dove e' sprofondata
    # e quanto ne e' risalita.
    fondo = min(accumulo, key=lambda v: v['accumulato'])
    cima = max(accumulo, key=lambda v: v['accumulato'])

    # --- l'accumulo delle ultime quattro settimane: questo non si annulla,
    # e' il debito che ti porti addosso adesso.
    coda = accumulo[-28:]
    accumulo_recente = sum(v['scarto'] for v in coda)

    # --- quattro settimane contro le quattro di prima, in faccia
    confronto = None
    if len(elenco) >= 42:
        ultime = [n['minuti'] for n in elenco[-28:]]
        prima = [n['minuti'] for n in elenco[-56:-28]]
        if prima:
            a, b = sum(ultime) / float(len(ultime)), sum(prima) / float(len(prima))
            confronto = {'ora': a, 'prima': b, 'per_notte': a - b,
                         'notti_ora': len(ultime), 'notti_prima': len(prima),
                         'totale': (a - b) * len(ultime)}

    # --- quanto e' solida la media: errore standard, al 95%. Con poche notti
    # la media e' fatta di quelle stesse notti e puo' spostarsi di molto.
    dev = (sum((x - media) ** 2 for x in minuti) / float(len(minuti) - 1)) ** 0.5 if len(minuti) > 1 else 0.0
    incertezza = 1.96 * dev / (len(minuti) ** 0.5)

    # --- il ciclo. I cicli si contano dalla prima notte misurata, a blocchi
    # di `giorni_del_ciclo` giorni. La media di riferimento e' quella dell'ultimo
    # ciclo CHIUSO; finche' il primo non si chiude, e' la media del ciclo in
    # corso, e si dice che e' provvisoria.
    giorni_ciclo = _giorni_ciclo()
    primo_giorno = elenco[0]['data']

    def _ciclo_di(giorno):
        return (giorno - primo_giorno).days // giorni_ciclo

    per_ciclo = {}
    for n in elenco:
        per_ciclo.setdefault(_ciclo_di(n['data']), []).append(n)

    def _riassumi(indice):
        notti_c = per_ciclo[indice]
        dal_c = primo_giorno + datetime.timedelta(days=indice * giorni_ciclo)
        al_c = dal_c + datetime.timedelta(days=giorni_ciclo - 1)
        mm = [x['minuti'] for x in notti_c]
        m = sum(mm) / float(len(mm))
        d = (sum((x - m) ** 2 for x in mm) / float(len(mm) - 1)) ** 0.5 if len(mm) > 1 else 0.0
        return {'numero': indice + 1, 'dal': dal_c.isoformat(), 'al': al_c.isoformat(),
                'notti': len(mm), 'giorni': giorni_ciclo, 'media': m,
                'incertezza': 1.96 * d / (len(mm) ** 0.5),
                'chiuso': elenco[-1]['data'] >= al_c}

    indice_ora = _ciclo_di(elenco[-1]['data'])
    ciclo = _riassumi(indice_ora)
    cicli_chiusi = [_riassumi(i) for i in sorted(per_ciclo) if i < indice_ora]
    if ciclo['chiuso']:
        cicli_chiusi.append(ciclo)
    if cicli_chiusi:
        base = cicli_chiusi[-1]
        riferimento, riferimento_provvisorio = base['media'], False
        riferimento_incertezza, riferimento_notti = base['incertezza'], base['notti']
    else:
        riferimento, riferimento_provvisorio = ciclo['media'], True
        riferimento_incertezza, riferimento_notti = ciclo['incertezza'], ciclo['notti']

    # le settimane del ciclo in corso, ciascuna contro la media di riferimento
    sett_ciclo = {}
    for n in per_ciclo[indice_ora]:
        anno_c, num_c, _ = n['data'].isocalendar()
        v = sett_ciclo.setdefault('%d-W%02d' % (anno_c, num_c),
                                  {'settimana': '%d-W%02d' % (anno_c, num_c),
                                   'notti': 0, 'minuti': 0, 'dal': n['data'], 'al': n['data']})
        v['notti'] += 1
        v['minuti'] += n['minuti']
        v['dal'], v['al'] = min(v['dal'], n['data']), max(v['al'], n['data'])
    ciclo['settimane'] = []
    for chiave in sorted(sett_ciclo):
        v = sett_ciclo[chiave]
        a_notte = v['minuti'] / float(v['notti'])
        ciclo['settimane'].append({'settimana': v['settimana'], 'dal': v['dal'].isoformat(),
                                   'al': v['al'].isoformat(), 'notti': v['notti'],
                                   'a_notte': a_notte, 'scarto': a_notte - riferimento})
    ciclo['giorno'] = (elenco[-1]['data'] - datetime.date.fromisoformat(ciclo['dal'])).days + 1

    # --- la settimana in corso. Il metro e' sempre il tuo: la tua media
    # settimanale e' 7 notti x la tua media a notte. Quello che dice e' solo
    # aritmetica -- quanto manca alle notti che restano per arrivarci --
    # non un fabbisogno.
    corrente = None
    anno_o, num_o, _ = datetime.date.today().isocalendar()
    ultima_sett = ordinate[-1]
    if ultima_sett['settimana'] == '%d-W%02d' % (anno_o, num_o):
        rimanenti = max(0, 6 - elenco[-1]['data'].weekday())
        obiettivo = 7 * riferimento
        servono = obiettivo - ultima_sett['minuti']
        prec = ordinate[-2] if len(ordinate) > 1 else None
        corrente = {
            'settimana': ultima_sett['settimana'],
            'notti': ultima_sett['notti'],
            'minuti': ultima_sett['minuti'],
            'a_notte': ultima_sett['a_notte'],
            'rimanenti': rimanenti,
            'obiettivo': obiettivo,
            'servono_totale': max(0.0, servono),
            'servono_a_notte': (max(0.0, servono) / rimanenti) if rimanenti else None,
            'gia_sopra': servono <= 0,
            'precedente': ({'settimana': prec['settimana'], 'notti': prec['notti'],
                            'minuti': prec['minuti'], 'a_notte': prec['a_notte']}
                           if prec else None),
        }

    corta = min(elenco, key=lambda n: n['minuti'])
    lunga = max(elenco, key=lambda n: n['minuti'])
    sotto = [n for n in elenco if n['minuti'] < media]

    return {
        'vuoto': False,
        'poche': len(elenco) < _soglia(),
        'mancano': max(0, _soglia() - len(elenco)),
        'soglia': _soglia(),
        'elenco': [{'data': n['data'].isoformat(), 'minuti': n['minuti'],
                    'a_letto': n['a_letto'], 'sveglia': n['sveglia'],
                    'efficienza': n['efficienza'], 'profondo': n['profondo'],
                    'rem': n['rem'], 'sessioni': n['sessioni'],
                    'festivo': n['festivo']} for n in elenco],
        'notti': len(elenco),
        'dal': primo.isoformat(),
        'al': ultimo.isoformat(),
        'giorni_coperti': giorni_totali,
        'mancanti': mancanti,
        'totale_minuti': sum(minuti),
        'media': media,
        'dev_std': dev,
        'incertezza': incertezza,
        'corrente': corrente,
        'ciclo': ciclo,
        'cicli_chiusi': cicli_chiusi,
        'riferimento': riferimento,
        'riferimento_provvisorio': riferimento_provvisorio,
        'riferimento_incertezza': riferimento_incertezza,
        'riferimento_notti': riferimento_notti,
        'accumulato': accumulo[-1]['accumulato'],
        'ultima_notte': elenco[-1]['minuti'],
        'ultimo_scarto': elenco[-1]['minuti'] - media,
        'curva': accumulo,
        'fondo': {'data': fondo['data'], 'minuti': fondo['accumulato']},
        'cima': {'data': cima['data'], 'minuti': cima['accumulato']},
        'accumulo_recente': accumulo_recente,
        'notti_recenti': len(coda),
        'confronto': confronto,
        'settimane': ordinate,
        'striscia_ora': striscia_ora,
        'striscia_record': record_striscia,
        'striscia_record_finita': quando_record.isoformat() if quando_record else None,
        'notti_sotto': len(sotto),
        'corta': {'data': corta['data'].isoformat(), 'minuti': corta['minuti']},
        'lunga': {'data': lunga['data'].isoformat(), 'minuti': lunga['minuti']},
        'media_letto': (media_letto + 18 * 60) if media_letto is not None else None,
        'media_letto_feriale': (media_feriale + 18 * 60) if media_feriale is not None else None,
        'media_letto_festiva': (media_festiva + 18 * 60) if media_festiva is not None else None,
        'slittamento': (media_festiva - media_feriale) if (media_feriale is not None and media_festiva is not None) else None,
        'irregolarita': irregolarita,
        'efficienza': _media([n['efficienza'] for n in elenco]),
        'profondo': _media([n['profondo'] for n in elenco]),
        'rem': _media([n['rem'] for n in elenco]),
        'risvegli': _media([n['risvegli'] for n in elenco]),
    }


def dati_finti():
    return os.path.exists(os.path.join(SALUTE, 'sonno', 'FINTI-CANCELLAMI.txt'))


# ============================================================  il rapporto a schermo

def rapporto(s=None):
    s = s or statistiche()
    if s.get('vuoto'):
        return 'Nessuna notte in salute\\sonno\\. Non c e niente da contare.'
    fuori = []
    scrivi = fuori.append
    scrivi('SONNO  --  %s  ->  %s   (%d notti su %d giorni)'
           % (s['dal'], s['al'], s['notti'], s['giorni_coperti']))
    scrivi('')
    if s['poche']:
        scrivi('  Sono ancora poche. Le medie, l accumulo e le settimane')
        scrivi('  cominciano a voler dire qualcosa da %d notti in su:' % s['soglia'])
        scrivi('  ne mancano %d. Intanto, quello che c e:' % s['mancano'])
        scrivi('')
        for voce in s['elenco']:
            scrivi('    %s   %s   %s -> %s   profondo %s  rem %s'
                   % (voce['data'], ore(voce['minuti']),
                      orologio(voce['a_letto']), orologio(voce['sveglia']),
                      ore(voce['profondo']), ore(voce['rem'])))
        if dati_finti():
            scrivi('')
            scrivi('*** ATTENZIONE: questi sono DATI FINTI.')
        return '\n'.join(fuori)
    scrivi('  accumulo nelle ultime %2d notti       %s'
           % (s['notti_recenti'], ore(s['accumulo_recente'], segno=True)))
    scrivi('  il punto piu basso della curva      %s   il %s'
           % (ore(s['fondo']['minuti'], segno=True), s['fondo']['data']))
    scrivi('  la tua media                        %s a notte' % ore(s['media']))
    scrivi('  totale dormito nel periodo          %s' % ore(s['totale_minuti']))
    scrivi('  notti sotto la tua media            %d su %d' % (s['notti_sotto'], s['notti']))
    scrivi('  notti di fila sotto, adesso         %d   (record: %d)'
           % (s['striscia_ora'], s['striscia_record']))
    if s['mancanti']:
        scrivi('  notti non misurate                  %d' % s['mancanti'])
    if s['confronto']:
        c = s['confronto']
        scrivi('')
        scrivi('  ultime %d notti        %s a notte' % (c['notti_ora'], ore(c['ora'])))
        scrivi('  le %d di prima        %s a notte        %s a notte, %s in tutto'
               % (c['notti_prima'], ore(c['prima']), ore(c['per_notte'], segno=True),
                  ore(c['totale'], segno=True)))
    scrivi('')
    scrivi('  ti addormenti in media alle         %s' % orologio(s['media_letto']))
    if s['slittamento'] is not None:
        scrivi('  nel fine settimana slitta di        %s' % ore(s['slittamento'], segno=True))
    if s['irregolarita'] is not None:
        scrivi('  quanto sei irregolare               %s di scarto medio' % ore(s['irregolarita']))
    scrivi('')
    scrivi('  la notte piu corta   %s   %s' % (s['corta']['data'], ore(s['corta']['minuti'])))
    scrivi('  la notte piu lunga   %s   %s' % (s['lunga']['data'], ore(s['lunga']['minuti'])))
    scrivi('')
    scrivi('LE SETTIMANE, SOMMATE')
    for voce in s['settimane'][-8:]:
        differenza = '' if voce['differenza'] is None else ('   %s sulla precedente' % ore(voce['differenza'], segno=True))
        parziale = '' if voce['completa'] else '   (%d notti)' % voce['notti']
        scrivi('  %s   %s%s%s' % (voce['settimana'], ore(voce['minuti']), differenza, parziale))
    if dati_finti():
        scrivi('')
        scrivi('*** ATTENZIONE: questi sono DATI FINTI. Vedi salute\\sonno\\FINTI-CANCELLAMI.txt')
    return '\n'.join(fuori)


def scrivi_sintesi(s=None):
    """Poche righe in salute\\stato-salute.md, nella stessa forma di
    progetti\\stato-sintesi.md: cosi' il widget di Sentinella puo' pescarle
    domani senza che oggi si tocchi una riga di Sentinella."""
    s = s or statistiche()
    percorso = os.path.join(SALUTE, 'stato-salute.md')
    if s.get('vuoto'):
        testo = '# Salute\n\n    aggiornata: %s\n\nNessuna notte misurata.\n' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    else:
        if s['poche']:
            riga = 'sonno: %d notti misurate, ne mancano %d perche i conti abbiano senso' % (
                s['notti'], s['mancano'])
        else:
            riga = 'sonno: %s nelle ultime %d notti, %d di fila sotto la media' % (
                ore(s['accumulo_recente'], segno=True), s['notti_recenti'], s['striscia_ora'])
        if s['poche']:
            testo = (
                '# Salute\n\n'
                '    aggiornata: %s\n\n'
                '%d notti misurate, dal %s al %s.\n\n'
                'Ancora poche: medie e accumuli cominciano a voler dire qualcosa\n'
                'da %d notti in su. Ne mancano **%d**.\n\n'
                '## Una riga per il widget\n\n    %s\n'
                % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                   s['notti'], s['dal'], s['al'], s['soglia'], s['mancano'], riga))
            with open(percorso, 'w', encoding='utf-8') as f:
                f.write(testo)
            return percorso
        testo = (
            '# Salute\n\n'
            '    aggiornata: %s\n\n'
            '%d notti misurate, dal %s al %s.\n\n'
            '- accumulo nelle ultime %d notti: **%s**\n'
            '- la tua media: %s a notte\n'
            '- questa settimana finora: %s\n'
            '- notti di fila sotto la media: %d (record %d)\n\n'
            '## Una riga per il widget\n\n    %s\n'
            % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
               s['notti'], s['dal'], s['al'],
               s['notti_recenti'], ore(s['accumulo_recente'], segno=True), ore(s['media']),
               ore(s['settimane'][-1]['minuti']),
               s['striscia_ora'], s['striscia_record'], riga))
    with open(percorso, 'w', encoding='utf-8') as f:
        f.write(testo)
    return percorso


if __name__ == '__main__':
    conti = statistiche()
    print(rapporto(conti))
    print('\nscritto  %s' % scrivi_sintesi(conti))

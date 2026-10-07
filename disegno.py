# -*- coding: utf-8 -*-
"""I grafici, disegnati a mano in SVG.

Nessuna libreria: niente da scaricare, niente CDN, funziona col PC staccato
da internet. Un SVG e' testo: se apri la pagina e fai "salva", quello che
salvi si riapre da solo fra dieci anni.
"""

import datetime

import lettura


def _x(indice, quanti, larghezza, bordo):
    if quanti <= 1:
        return bordo
    return bordo + (larghezza - 2 * bordo) * indice / float(quanti - 1)


def curva_accumulo(curva, larghezza=980, altezza=260, colore='#c9a227', rosso='#b5533f'):
    """La curva del sonno accumulato: quanto sei sopra o sotto la tua media,
    sommato giorno per giorno. Sotto lo zero l'area si colora di rosso."""
    if len(curva) < 2:
        return '<p class="niente">Servono almeno due notti per disegnare una curva.</p>'
    bordo = 34
    valori = [v['accumulato'] for v in curva]
    alto, basso = max(valori + [0]), min(valori + [0])
    if alto == basso:
        alto, basso = alto + 60, basso - 60
    campo = float(alto - basso)

    def y(valore):
        return bordo + (altezza - 2 * bordo) * (alto - valore) / campo

    zero = y(0)
    punti = [(_x(i, len(curva), larghezza, bordo), y(v)) for i, v in enumerate(valori)]
    linea = ' '.join('%.1f,%.1f' % p for p in punti)
    area = '%.1f,%.1f %s %.1f,%.1f' % (punti[0][0], zero, linea, punti[-1][0], zero)

    fondo = min(range(len(valori)), key=lambda i: valori[i])
    pezzi = ['<svg viewBox="0 0 %d %d" class="grafico" preserveAspectRatio="none">' % (larghezza, altezza)]
    pezzi.append('<defs><linearGradient id="giu" x1="0" x2="0" y1="0" y2="1">'
                 '<stop offset="0" stop-color="%s" stop-opacity=".30"/>'
                 '<stop offset="1" stop-color="%s" stop-opacity=".02"/></linearGradient></defs>' % (rosso, rosso))
    pezzi.append('<polygon points="%s" fill="url(#giu)"/>' % area)
    pezzi.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" class="zero"/>'
                 % (bordo, larghezza - bordo, zero, zero))
    pezzi.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
                 'stroke-linejoin="round"/>' % (linea, colore))
    # il fondo, segnato
    fx, fy = punti[fondo]
    pezzi.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (fx, fy, rosso))
    # i punti invisibili che fanno comparire l'etichetta passandoci sopra
    for indice, (px, py) in enumerate(punti):
        voce = curva[indice]
        pezzi.append('<circle cx="%.1f" cy="%.1f" r="7" fill="transparent"><title>%s\n'
                     'quella notte: %s\naccumulato: %s</title></circle>'
                     % (px, py, voce['data'], lettura.ore(voce['minuti']),
                        lettura.ore(voce['accumulato'], segno=True)))
    pezzi.append('<text x="%d" y="%.1f" class="tacca">zero = la tua media</text>'
                 % (bordo + 4, zero - 7))
    pezzi.append('</svg>')
    return ''.join(pezzi)


def barre_settimane(settimane, larghezza=980, altezza=220,
                    colore='#c9a227', spento='#3a4150'):
    """Le ore sommate, una barra per settimana. Le settimane incomplete
    restano spente: una settimana con tre notti non si confronta con una
    che ne ha sette, e colorarla uguale sarebbe una bugia."""
    if not settimane:
        return '<p class="niente">Nessuna settimana.</p>'
    settimane = settimane[-14:]
    bordo_basso, bordo_alto = 42, 26
    massimo = max(v['minuti'] for v in settimane) or 1
    passo = (larghezza - 40) / float(len(settimane))
    largo = min(52, passo * 0.62)
    pezzi = ['<svg viewBox="0 0 %d %d" class="grafico">' % (larghezza, altezza)]
    for indice, voce in enumerate(settimane):
        alta = (altezza - bordo_basso - bordo_alto) * voce['minuti'] / float(massimo)
        cx = 20 + passo * (indice + 0.5)
        x = cx - largo / 2
        y = altezza - bordo_basso - alta
        tinta = colore if voce['completa'] else spento
        differenza = '' if voce['differenza'] is None else ('\n%s sulla precedente' % lettura.ore(voce['differenza'], segno=True))
        pezzi.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s">'
                     '<title>%s  (%s -> %s)\n%s in %d notti%s</title></rect>'
                     % (x, y, largo, max(1.0, alta), tinta, voce['settimana'], voce['dal'],
                        voce['al'], lettura.ore(voce['minuti']), voce['notti'], differenza))
        pezzi.append('<text x="%.1f" y="%.1f" class="sopra">%dh</text>'
                     % (cx, y - 7, int(round(voce['minuti'] / 60.0))))
        pezzi.append('<text x="%.1f" y="%.1f" class="sotto">%s</text>'
                     % (cx, altezza - bordo_basso + 18, voce['settimana'][-3:]))
        if not voce['completa']:
            pezzi.append('<text x="%.1f" y="%.1f" class="sotto piccolo">%d notti</text>'
                         % (cx, altezza - bordo_basso + 32, voce['notti']))
    pezzi.append('</svg>')
    return ''.join(pezzi)


def pettine_notti(curva, larghezza=980, altezza=150, colore='#c9a227', rosso='#b5533f'):
    """Una stanghetta per notte: sopra la media in oro, sotto in rosso.
    Serve a vedere le strisce -- il disegno che i numeri non fanno vedere."""
    if not curva:
        return ''
    curva = curva[-70:]
    meta = altezza / 2.0
    massimo = max(abs(v['scarto']) for v in curva) or 1
    passo = (larghezza - 40) / float(len(curva))
    largo = max(2.0, passo * 0.6)
    pezzi = ['<svg viewBox="0 0 %d %d" class="grafico">' % (larghezza, altezza)]
    pezzi.append('<line x1="20" x2="%d" y1="%.1f" y2="%.1f" class="zero"/>'
                 % (larghezza - 20, meta, meta))
    for indice, voce in enumerate(curva):
        alta = (meta - 12) * abs(voce['scarto']) / float(massimo)
        cx = 20 + passo * (indice + 0.5)
        su = voce['scarto'] >= 0
        y = meta - alta if su else meta
        pezzi.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="%s">'
                     '<title>%s\n%s   (%s sulla tua media)</title></rect>'
                     % (cx - largo / 2, y, largo, max(1.0, alta), colore if su else rosso,
                        '.9' if not voce['festivo'] else '.55',
                        voce['data'], lettura.ore(voce['minuti']),
                        lettura.ore(voce['scarto'], segno=True)))
    pezzi.append('</svg>')
    return ''.join(pezzi)


# ======================================================  la pagina nuova (7 ottobre)
# Colori e scale. Le soglie sono tue: configurazione.json (vedi lettura.impostazione).
# Un solo vocabolario per tutta la pagina: oro = sul metro, verde = vicino,
# rosso = sotto, nero = molto sotto, viola = troppo sopra.

MESI = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic']
GIORNI = ['lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom']


def breve(minuti, segno=False):
    """8h10. Con segno: +2h05, −1h11."""
    minuti = int(round(minuti))
    meno = minuti < 0
    minuti = abs(minuti)
    testo = '%dh%02d' % (minuti // 60, minuti % 60)
    if not segno:
        return ('−' if meno else '') + testo
    return ('−' if meno else '+') + testo


def scarto_testo(scarto):
    """−19 min sotto l'ora, 2h05 oltre."""
    if abs(scarto) < 60:
        return '%s%d min' % ('−' if scarto < 0 else '+', abs(int(round(scarto))))
    return breve(scarto, segno=True)


def giorno(data):
    return '%s %d %s' % (GIORNI[data.weekday()], data.day, MESI[data.month - 1])


def giorno_corto(data):
    return '%d %s' % (data.day, MESI[data.month - 1])


def _soglie():
    return (lettura.impostazione('colore_oro_entro_min', 30),
            lettura.impostazione('colore_verde_entro_min', 60),
            lettura.impostazione('colore_rosso_entro_min', 120))


def colore_scarto(scarto):
    """Il nome della variabile CSS per uno scarto (in minuti) dal metro."""
    oro, verde, rosso = _soglie()
    if scarto > verde:
        return 'viola'
    if -oro <= scarto <= oro:
        return 'oro'
    if scarto >= -verde:
        return 'verde'
    if scarto >= -rosso:
        return 'rosso'
    return 'nero'


def scala(riferimento, valore=None, fascia=None, ore_max=12):
    """La barra a colori da 0 a 12 ore, col metro, e (se c'e') un indicatore
    sul valore e una cornice sulla fascia (basso, alto), tutto in minuti."""
    oro, verde, rosso = _soglie()
    m = riferimento
    zone = [(0, m - rosso, 'nero'), (m - rosso, m - verde, 'rosso'), (m - verde, m - oro, 'verde'),
            (m - oro, m + oro, 'oro'), (m + oro, m + verde, 'verde'), (m + verde, ore_max * 60, 'viola')]
    totale = float(ore_max * 60)
    pezzi = ['<div class="wrap"><div class="scala">']
    for a, b, nome in zone:
        a, b = max(0, a), min(totale, b)
        if b > a:
            pezzi.append('<i style="width:%.2f%%;background:var(--%s)"></i>' % ((b - a) / totale * 100, nome))
    pezzi.append('</div>')
    pezzi.append('<div class="linea" style="left:calc(%.2f%% - 1px)"></div>' % (m / totale * 100))
    if valore is not None:
        pezzi.append('<div class="spilla" style="left:calc(%.2f%% - 2px)"></div>'
                     % (max(0, min(totale, valore)) / totale * 100))
    if fascia:
        basso, alto = min(fascia), max(fascia)
        pezzi.append('<div class="cornice" style="left:%.2f%%;width:%.2f%%;min-width:10px"></div>'
                     % (basso / totale * 100, (alto - basso) / totale * 100))
    pezzi.append('<div class="tacche">')
    for h in range(0, ore_max + 1, 3):
        pezzi.append('<span style="left:%.2f%%">%dh</span>' % (h * 60 / totale * 100, h))
    pezzi.append('</div></div>')
    return ''.join(pezzi)


def legenda():
    voci = (('nero', 'male'), ('rosso', 'sotto'), ('verde', 'vicino'), ('oro', 'sul metro'), ('viola', 'troppo'))
    return '<div class="legenda">%s</div>' % ''.join(
        '<span><i style="background:var(--%s)"></i>%s</span>' % v for v in voci)


def stanghette(elenco, dal, giorni, riferimento):
    """Una riga per notte del ciclo, con la data. Le notti non ancora
    arrivate restano righe vuote: il ciclo si vede riempirsi."""
    per_data = {n['data']: n['minuti'] for n in elenco}
    inizio = datetime.date.fromisoformat(dal)
    righe = []
    for i in range(giorni):
        d = inizio + datetime.timedelta(days=i)
        lun = ' lun' if d.weekday() == 0 and i > 0 else ''
        minuti = per_data.get(d)
        if minuti is None:
            righe.append('<div class="r vuoto%s"><div>%s</div><div class="barra"></div><span></span></div>'
                         % (lun, giorno(d)))
            continue
        scarto = minuti - riferimento
        largo = min(50.0, abs(scarto) / 300.0 * 50)
        pos = 'left:50%%;width:%.2f%%' % largo if scarto >= 0 else 'left:%.2f%%;width:%.2f%%' % (50 - largo, largo)
        righe.append('<div class="r%s"><div>%s</div><div class="barra"><u style="%s;background:var(--%s)"></u></div>'
                     '<span>%s</span></div>' % (lun, giorno(d), pos, colore_scarto(scarto), breve(minuti)))
    return ''.join(righe)


def _etichetta_settimana(a, b):
    if a == b:
        return giorno_corto(a)
    if a.month == b.month:
        return '%d–%d %s' % (a.day, b.day, MESI[a.month - 1])
    return '%s–%s' % (giorno_corto(a), giorno_corto(b))


def colonne_settimane(elenco, dal, giorni, riferimento, larghezza=356, altezza=170):
    """Le ore sommate, una colonna per settimana del ciclo. Quelle incomplete
    restano grigie: tre notti non si confrontano con sette."""
    inizio = datetime.date.fromisoformat(dal)
    fine = inizio + datetime.timedelta(days=giorni - 1)
    per_data = {n['data']: n['minuti'] for n in elenco}
    gruppi, d = [], inizio
    while d <= fine:
        lunedi = d - datetime.timedelta(days=d.weekday())
        domenica = min(lunedi + datetime.timedelta(days=6), fine)
        gruppi.append((d, domenica))
        d = domenica + datetime.timedelta(days=1)
    totali = []
    for a, b in gruppi:
        notti = [per_data[a + datetime.timedelta(days=k)]
                 for k in range((b - a).days + 1)
                 if a + datetime.timedelta(days=k) in per_data]
        totali.append((a, b, notti))
    obiettivo = 7 * riferimento
    massimo = max([obiettivo] + [sum(t[2]) for t in totali])
    tetto = -(-int(massimo) // 600) * 600           # su al multiplo di 10 ore
    bordo = 26
    larg_c = min(48, larghezza / (len(totali) * 1.5))
    vuoto = (larghezza - larg_c * len(totali)) / (len(totali) + 1.0)

    def y(v):
        return bordo + (altezza - bordo) * (1 - v / float(tetto))

    p = ['<svg viewBox="0 0 %d %d" width="100%%">' % (larghezza, altezza + 36)]
    p.append('<line x1="0" x2="%d" y1="%.1f" y2="%.1f" stroke="#12303a" stroke-dasharray="4 4" opacity=".6"/>'
             % (larghezza, y(obiettivo), y(obiettivo)))
    p.append('<text x="%d" y="%.1f" font-size="10" fill="#5d7a82" text-anchor="end">7 × metro = %s</text>'
             % (larghezza, y(obiettivo) - 4, breve(obiettivo)))
    for i, (a, b, notti) in enumerate(totali):
        x = vuoto + i * (larg_c + vuoto)
        centro = x + larg_c / 2
        p.append('<text x="%.1f" y="%d" font-size="9.5" fill="#5d7a82" text-anchor="middle">%s</text>'
                 % (centro, altezza + 14, _etichetta_settimana(a, b)))
        if not notti:
            p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="3" rx="1.5" fill="#e1ebea"/>' % (x, y(0) - 3, larg_c))
            p.append('<text x="%.1f" y="%d" font-size="9.5" fill="#9bb0b5" text-anchor="middle">–</text>'
                     % (centro, altezza + 27))
            continue
        somma = sum(notti)
        completa = len(notti) == 7
        colore = 'var(--%s)' % colore_scarto(somma / float(len(notti)) - riferimento) if completa else '#c9d8dc'
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="%s"/>'
                 % (x, y(somma), larg_c, y(0) - y(somma), colore))
        p.append('<text x="%.1f" y="%.1f" font-size="11" font-weight="700" fill="#12303a" text-anchor="middle">%s</text>'
                 % (centro, y(somma) - 5, breve(somma)))
        p.append('<text x="%.1f" y="%d" font-size="9.5" fill="#5d7a82" text-anchor="middle">%d %s</text>'
                 % (centro, altezza + 27, len(notti), 'notte' if len(notti) == 1 else 'notti'))
    p.append('</svg>')
    return ''.join(p)


def accumulo_ciclo(elenco, dal, giorni, riferimento, larghezza=356, altezza=200):
    """Quanto sei sopra o sotto il metro, notte dopo notte, lungo tutto il
    ciclo. Dopo l'ultima notte misurata la linea resta tratteggiata."""
    inizio = datetime.date.fromisoformat(dal)
    notti = [n for n in elenco if 0 <= (n['data'] - inizio).days < giorni]
    if len(notti) < 2:
        return '<p class="piccolo">Servono almeno due notti.</p>'
    somma, punti = 0.0, []
    for n in notti:
        somma += n['minuti'] - riferimento
        punti.append(((n['data'] - inizio).days, somma))
    valori = [v for _, v in punti]
    alto, basso = max(max(valori), 60) + 40, min(min(valori), -60) - 40

    def x(i):
        return 10 + (larghezza - 20) * i / float(max(1, giorni - 1))

    def y(v):
        return 12 + (altezza - 52) * (1 - (v - basso) / float(alto - basso))

    linea = ' '.join('%.1f,%.1f' % (x(i), y(v)) for i, v in punti)
    ultimo_i, ultimo_v = punti[-1]
    p = ['<svg viewBox="0 0 %d %d" width="100%%">' % (larghezza, altezza)]
    p.append('<line x1="10" x2="%d" y1="%.1f" y2="%.1f" stroke="#12303a" opacity=".5"/>' % (larghezza - 10, y(0), y(0)))
    p.append('<line x1="%.1f" x2="%.1f" y1="6" y2="%d" stroke="#9bb0b5" stroke-dasharray="3 4"/>'
             % (x(ultimo_i), x(ultimo_i), altezza - 26))
    p.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#2f6fcb" stroke-dasharray="2 5" opacity=".7"/>'
             % (x(ultimo_i), x(giorni - 1), y(ultimo_v), y(ultimo_v)))
    p.append('<polygon points="%.1f,%.1f %s %.1f,%.1f" fill="#2f6fcb" opacity=".10"/>'
             % (x(punti[0][0]), y(0), linea, x(ultimo_i), y(0)))
    p.append('<polyline points="%s" fill="none" stroke="#2f6fcb" stroke-width="2.4" stroke-linejoin="round"/>' % linea)
    i_max = max(range(len(punti)), key=lambda k: punti[k][1])
    i_min = min(range(len(punti)), key=lambda k: punti[k][1])
    gm, gn = punti[i_max], punti[i_min]
    p.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#d9a21b"/><text x="%.1f" y="%.1f" font-size="10" fill="#12303a">%s · %s</text>'
             % (x(gm[0]), y(gm[1]), x(gm[0]) + 6, y(gm[1]) - 6, breve(gm[1], True),
                giorno_corto(inizio + datetime.timedelta(days=gm[0]))))
    p.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#d64545"/><text x="%.1f" y="%.1f" font-size="10" fill="#12303a">%s · %s</text>'
             % (x(gn[0]), y(gn[1]), x(gn[0]) + 9, y(gn[1]) + 4, breve(gn[1], True),
                giorno_corto(inizio + datetime.timedelta(days=gn[0]))))
    p.append('<text x="%d" y="%.1f" font-size="9.5" fill="#5d7a82" text-anchor="end">0 = il tuo metro</text>'
             % (larghezza - 10, y(0) - 5))
    for i in sorted(set([0, giorni // 3, 2 * giorni // 3, giorni - 1])):
        ancora = 'start' if i == 0 else 'end' if i == giorni - 1 else 'middle'
        p.append('<text x="%.1f" y="%d" font-size="9.5" fill="#5d7a82" text-anchor="%s">%s</text>'
                 % (x(i), altezza - 8, ancora, giorno_corto(inizio + datetime.timedelta(days=i))))
    p.append('</svg>')
    return ''.join(p)

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

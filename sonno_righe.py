# -*- coding: utf-8 -*-
"""Da come Google Health racconta le sessioni di sonno a una riga per giorno.

Sta qui, e non dentro scarica.py, perche' lo usano due posti: lo scarico di
casa (scarica.py) e il servizio online, che ne tiene una copia sincronizzata
(sincronizza-online.py). Cosi' un giorno si conta allo stesso modo ovunque.
"""

COLONNE_SONNO = ['data', 'a_letto', 'sveglia', 'minuti_dormiti', 'sessioni',
                 'sessione_piu_lunga_min', 'efficienza',
                 'profondo_min', 'rem_min', 'leggero_min', 'sveglio_min',
                 'minuti_a_letto', 'minuti_per_addormentarsi',
                 'tipo', 'sorgente']


def _ora(momento):
    """2026-09-21T23:48:00+02:00 -> 23:48"""
    return momento[11:16] if momento and len(momento) >= 16 else ''


def righe_di_sonno(grezze):
    """Una riga per giorno.

    Se in un giorno ci sono piu' sessioni -- il sonno spezzato in due, o un
    pisolino -- **`minuti_dormiti` e' il totale di tutte**, e le fasi sono
    sommate allo stesso modo. Gli orari sono quelli della sessione piu'
    lunga, perche' un "a letto" e uno "sveglia" per una giornata spezzata
    non esistono, e inventarne uno medio sarebbe peggio.

    `sessioni` dice in quanti pezzi. `sessione_piu_lunga_min` dice quanto
    pesa il pezzo grosso: se e' molto meno del totale, quel giorno il sonno
    era sparso, e la riga va letta sapendolo.

    La prima versione teneva come "notte" solo la sessione piu' lunga. Il 23
    settembre 2026 ha mostrato che era sbagliato: 193 + 234 minuti erano
    diventati "3h54 dormite" invece di 7h07.
    """
    per_giorno = {}
    for punto in grezze:
        fine = (punto.get('end') or '')[:10]
        if not fine:
            continue
        per_giorno.setdefault(fine, []).append(punto)

    def somma(sessioni, chiave):
        return sum(p.get(chiave) or 0 for p in sessioni)

    def somma_fase(sessioni, fase):
        return sum((p.get('stageMinutes') or {}).get(fase, 0) for p in sessioni)

    righe = []
    for giorno, sessioni in sorted(per_giorno.items()):
        sessioni.sort(key=lambda p: p.get('minutesAsleep') or 0, reverse=True)
        piu_lunga = sessioni[0]
        dormiti = somma(sessioni, 'minutesAsleep')
        a_letto = somma(sessioni, 'totalMinutes')
        righe.append({
            'data': giorno,
            'a_letto': _ora(piu_lunga.get('start')),
            'sveglia': _ora(piu_lunga.get('end')),
            'minuti_dormiti': dormiti,
            'sessioni': len(sessioni),
            'sessione_piu_lunga_min': piu_lunga.get('minutesAsleep') or 0,
            'efficienza': int(round(100.0 * dormiti / a_letto)) if a_letto else '',
            'profondo_min': somma_fase(sessioni, 'DEEP'),
            'rem_min': somma_fase(sessioni, 'REM'),
            'leggero_min': somma_fase(sessioni, 'LIGHT'),
            'sveglio_min': somma_fase(sessioni, 'AWAKE') or somma(sessioni, 'minutesAwake'),
            'minuti_a_letto': a_letto,
            'minuti_per_addormentarsi': piu_lunga.get('minutesToFallAsleep', ''),
            'tipo': piu_lunga.get('sleepType', ''),
            'sorgente': piu_lunga.get('source', ''),
        })
    return righe

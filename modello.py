# -*- coding: utf-8 -*-
"""Il modello della pagina di Comodino.

Lo usano due posti: la pagina di casa (app.py) e il servizio online, che ne
tiene una copia sincronizzata (sincronizza-online.py). Cosi' i numeri sono gli
stessi dappertutto, e non ci sono due programmi da tenere allineati a mano.

Pagina del 7 ottobre 2026: bianco, verde e blu; un titolo e una riga per ogni
statistica; il ciclo di 30 notti disegnato per intero. La dieta e il lavoro
dei progetti non ci sono: si riaggiungono nei prossimi giorni, nello stesso
stile (i parametri restano nella firma di `disegna` perche' app.py li passa).
"""

import datetime

from flask import render_template_string

import disegno
import lettura

PAGINA = """<!doctype html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Comodino</title>
<style>
  :root{--fondo:#f4f9f8;--inchiostro:#12303a;--spento:#5d7a82;--riga:#e1ebea;
        --blu:#2f6fcb;--blu-c:#dce8f9;--verde:#2e9e6b;--verde-c:#d9f0e5;
        --oro:#d9a21b;--rosso:#d64545;--nero:#15191d;--viola:#6b34d9}
  *{box-sizing:border-box}
  body{margin:0;background:var(--fondo);color:var(--inchiostro);
       font:15px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif;
       padding:18px 16px 28px}
  .dentro{max-width:520px;margin:0 auto}
  h1{font-size:22px;margin:0 0 14px}
  .card{background:#fff;border-radius:16px;padding:16px;margin-bottom:12px;border:1px solid var(--riga)}
  h2{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--blu);margin:0 0 8px;font-weight:700}
  .kick{font-size:12px;color:var(--spento)}
  .grosso{font-size:30px;font-weight:700;line-height:1.1}
  .grosso small,.eroe small{font-size:14px;font-weight:500;color:var(--spento)}
  .eroe{font-size:46px;font-weight:800;line-height:1;margin:4px 0 8px}
  .pillola{display:inline-block;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700;color:#fff}
  p{margin:8px 0 0;color:var(--spento);font-size:12.5px}
  .wrap{position:relative}
  .scala{position:relative;height:22px;border-radius:11px;overflow:hidden;margin:16px 0 4px;display:flex}
  .scala i{display:block;height:100%}
  .spilla{position:absolute;top:-7px;width:4px;height:36px;border-radius:2px;background:#fff;box-shadow:0 0 0 2px var(--inchiostro)}
  .linea{position:absolute;top:-3px;width:2px;height:28px;background:var(--inchiostro)}
  .cornice{position:absolute;top:-6px;height:34px;border:3px solid var(--inchiostro);border-radius:9px;background:rgba(255,255,255,.18)}
  .tacche{position:relative;height:14px;font-size:10px;color:var(--spento)}
  .tacche span{position:absolute;transform:translateX(-50%)}
  .legenda{display:flex;flex-wrap:wrap;gap:6px 12px;font-size:11px;color:var(--spento);margin-top:6px}
  .legenda i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:4px;vertical-align:-1px}
  .due{display:flex;gap:10px;margin-top:12px}
  .due div{flex:1;border-radius:12px;padding:10px;background:var(--fondo);border:1px solid var(--riga)}
  .due b{display:block;font-size:20px}.due span{font-size:11px;color:var(--spento)}
  .q{display:grid;grid-template-columns:84px 1fr 40px;gap:6px 10px;align-items:center;font-size:12px;margin-top:6px}
  .q .barra{height:10px;border-radius:5px;background:#e8f0f2;position:relative}
  .q .barra u{position:absolute;left:0;top:0;bottom:0;border-radius:5px;text-decoration:none}
  .q b{font-weight:600}.q span{text-align:right;font-weight:600}
  .r{display:grid;grid-template-columns:78px 1fr 46px;align-items:center;height:17px;font-size:11px;color:var(--spento)}
  .r.lun{border-top:1px solid var(--riga);margin-top:3px;padding-top:3px;height:20px}
  .r .barra{position:relative;height:11px}
  .r .barra:before{content:"";position:absolute;left:50%;top:-3px;bottom:-3px;width:1px;background:var(--inchiostro);opacity:.5}
  .r .barra u{position:absolute;top:0;bottom:0;border-radius:3px;text-decoration:none}
  .r.vuoto .barra{background:repeating-linear-gradient(90deg,#e1ebea 0 4px,transparent 4px 8px);height:2px;margin-top:0}
  .r.vuoto .barra:before{display:none}
  .r span{text-align:right;font-weight:600;color:var(--inchiostro)}
  svg{display:block}
  .fine{color:#8fa5aa;font-size:11px;margin-top:18px}
  .piccolo{font-size:12px;color:var(--spento)}
</style></head><body><div class="dentro">

<h1>Comodino</h1>
{% if s.vuoto %}
<div class="card"><p>Non c'e' ancora nessuna notte. Quando arrivano i dati, questa pagina si riempie da sola.</p></div>
{% else %}

{% if finti %}<div class="card" style="border-color:var(--rosso)"><p style="color:var(--rosso);margin:0"><b>Dati finti.</b>
  Cancella i CSV in <code>salute\\sonno\\</code> e questa riga sparisce.</p></div>{% endif %}

<div class="card"><h2>Il tuo metro</h2>
  <div class="grosso">{{ breve(s.riferimento) }} <small>a notte</small></div>
  <p>Media di {{ s.riferimento_notti }} notti{% if s.riferimento_provvisorio %} &middot; provvisoria{% endif %}.</p></div>

<div class="card"><h2>Notte per notte</h2>
  <div class="kick">Questa settimana &middot; {{ ultima.notti }} {{ 'notte' if ultima.notti == 1 else 'notti' }} su 7</div>
  <div class="eroe" style="color:var(--{{ col_sett }})">{{ breve(ultima.a_notte) }} <small>a notte</small></div>
  <span class="pillola" style="background:var(--{{ col_sett }})">{{ giudizio }} &middot; {{ scarto_sett }}</span>
  {{ scala_sett|safe }}
  {{ legenda|safe }}
  <p>Settimana intera: {{ breve(7 * s.riferimento) }} &middot; fatte {{ breve(ultima.minuti) }}</p></div>

{% if mancano %}
<div class="card"><h2>Le notti che mancano</h2>
  <div class="kick">{{ mancano.quante }} {{ 'notte' if mancano.quante == 1 else 'notti' }} &middot; da {{ mancano.dal }} a {{ mancano.al }}</div>
  {% if mancano.suggerite is not none %}
  <div class="grosso" style="color:var(--verde)">{{ breve(mancano.suggerite) }} <small>a notte, suggerite</small></div>
  {{ mancano.scala|safe }}
  <div class="due">
    <div><b>{{ breve(mancano.servono) if mancano.servono is not none else '--' }}</b><span>per chiudere la settimana</span></div>
    <div><b>{{ breve(mancano.buone) if mancano.buone is not none else '--' }}</b><span>nelle tue notti buone</span></div>
  </div>
  <p>{% if mancano.buone is not none and mancano.servono is not none and not mancano.gia_sopra %}Il suggerito sta a met&agrave; fra i due.{% elif mancano.gia_sopra %}La settimana &egrave; gi&agrave; al metro: il suggerito &egrave; quanto dormi nelle notti buone.{% endif %}</p>
  {% else %}
  <div class="grosso">{{ breve(mancano.servono) }} <small>a notte, per chiudere la settimana</small></div>
  {% endif %}
</div>
{% endif %}

{% if fasce %}
<div class="card"><h2>Quando dormi bene</h2>
  <div class="kick">Efficienza e risvegli, per durata della notte</div>
  <div class="q">
  {% for f in fasce %}<b>{{ f.nome }}</b><div class="barra"><u style="width:{{ '%.0f'|format(f.efficienza) }}%;background:var(--{{ f.colore }})"></u></div><span>{{ '%.0f'|format(f.efficienza) }}%</span>{% endfor %}
  </div>
  <div class="q" style="margin-top:10px">
  {% for f in fasce %}<b>{{ 'Svegli di notte' if loop.first else '' }}</b><div class="barra"><u style="width:{{ [f.sveglio, 100]|min }}%;background:{{ f.fondo_sveglio }};border:1px solid var(--{{ f.bordo }})"></u></div><span>{{ '%.0f'|format(f.sveglio) }}'</span>{% endfor %}
  </div>
  {% if frase_fasce %}<p>{{ frase_fasce }}</p>{% endif %}</div>
{% endif %}

<div class="card"><h2>Trenta notti</h2>
  <div class="kick">{{ ciclo_notti }} di {{ s.ciclo.giorni }} &middot; fine ciclo {{ fine_ciclo }}</div>
  <div style="margin-top:8px">{{ stanghette|safe }}</div>
  <p>Sopra la linea hai dormito pi&ugrave; del metro, sotto meno.</p></div>

<div class="card"><h2>Ore sommate, settimana per settimana</h2>
  {{ colonne|safe }}
  <p>Le settimane incomplete restano spente.</p></div>

<div class="card"><h2>Accumulo</h2>
  <div class="kick">Quanto sei sopra o sotto il metro, notte dopo notte</div>
  {{ accumulo|safe }}</div>
{% endif %}

<p class="fine">{% if dal_vivo %}Dati letti da Google Health a ogni apertura.{% elif per_online %}Copia depositata dal computer di casa.{% else %}Gira solo su questo PC &middot; i dati stanno in <code>salute\\</code>.{% endif %}</p>
</div></body></html>"""

_COLORI_FASCE = (('verde', 'var(--verde-c)', 'verde'), ('oro', 'var(--verde-c)', 'verde'),
                 ('viola', '#e6dcfa', 'viola'))


def _contesto(conti):
    """Tutto quello che la pagina mostra e che non e' gia' in `conti`."""
    ciclo = conti['ciclo']
    rif = conti['riferimento']
    elenco = [{'data': datetime.date.fromisoformat(n['data']), 'minuti': n['minuti']}
              for n in conti['elenco']]
    ultima = conti['settimane'][-1]
    scarto = ultima['a_notte'] - rif
    colore = disegno.colore_scarto(scarto)
    oro = lettura.impostazione('colore_oro_entro_min', 30)
    giudizio = ('Sul metro' if abs(scarto) <= oro else
                'Sopra il metro' if scarto > 0 else 'Sotto il metro')

    mancano = None
    cor = conti.get('corrente')
    if cor and cor['rimanenti']:
        dal = datetime.date.fromisoformat(cor['dal'])
        al = datetime.date.fromisoformat(cor['al'])
        suggerite = cor.get('suggerite')
        servono = cor['servono_a_notte']
        buone = cor.get('buone')
        fascia = [x for x in (servono if not cor['gia_sopra'] else None, buone) if x is not None]
        mancano = {
            'quante': cor['rimanenti'], 'dal': disegno.giorno(dal), 'al': disegno.giorno(al),
            'suggerite': suggerite, 'servono': servono, 'buone': buone,
            'gia_sopra': cor['gia_sopra'],
            'scala': disegno.scala(rif, fascia=fascia) if (suggerite is not None and fascia) else '',
        }

    fasce = []
    piene = [f for f in conti['fasce'] if f['notti'] and f['efficienza'] is not None and f['sveglio'] is not None]
    if len(piene) >= 2:
        for f, (colore_f, fondo, bordo) in zip(conti['fasce'], _COLORI_FASCE):
            if f in piene:
                fasce.append(dict(f, colore=colore_f if colore_f != 'verde' else 'verde',
                                  fondo_sveglio=fondo, bordo=bordo))
        for f in fasce:
            f['colore'] = {'Sotto 7h': 'verde', 'Oltre 9h': 'viola'}.get(f['nome'], 'oro')
    frase = ''
    by = {f['nome']: f for f in piene}
    if 'Oltre 9h' in by and '7–9h' in by and by['7–9h']['sveglio'] and \
            by['Oltre 9h']['sveglio'] >= 1.8 * by['7–9h']['sveglio']:
        frase = 'Oltre 9 ore i risvegli di notte raddoppiano.'

    dal_ciclo = datetime.date.fromisoformat(ciclo['dal'])
    notti_ciclo = len([n for n in elenco if 0 <= (n['data'] - dal_ciclo).days < ciclo['giorni']])
    return dict(
        ultima=ultima, col_sett=colore, giudizio=giudizio,
        scarto_sett=disegno.scarto_testo(scarto),
        scala_sett=disegno.scala(rif, valore=ultima['a_notte']),
        legenda=disegno.legenda(),
        mancano=mancano, fasce=fasce, frase_fasce=frase,
        ciclo_notti=notti_ciclo,
        fine_ciclo='%d %s' % (datetime.date.fromisoformat(ciclo['al']).day,
                              ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto',
                               'settembre', 'ottobre', 'novembre', 'dicembre'][datetime.date.fromisoformat(ciclo['al']).month - 1]),
        stanghette=disegno.stanghette(elenco, ciclo['dal'], ciclo['giorni'], rif),
        colonne=disegno.colonne_settimane(elenco, ciclo['dal'], ciclo['giorni'], rif),
        accumulo=disegno.accumulo_ciclo(elenco, ciclo['dal'], ciclo['giorni'], rif),
    )


def disegna(conti, comunque=False, per_online=False, finti=False, dal_vivo=False,
            settimana=None, settimane_dieta=(), in_arrivo=(), scanner=''):
    pieno = not conti.get('vuoto')
    extra = _contesto(conti) if pieno else {}
    return render_template_string(
        PAGINA,
        s=conti,
        per_online=per_online,
        dal_vivo=dal_vivo,
        finti=finti,
        breve=disegno.breve,
        **extra,
    )

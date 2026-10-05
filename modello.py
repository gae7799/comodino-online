# -*- coding: utf-8 -*-
"""Il modello della pagina di Comodino.

Lo usano due posti: la pagina di casa (app.py) e il servizio online, che ne
tiene una copia sincronizzata (sincronizza-online.py). Cosi' i numeri sono gli
stessi dappertutto, e non ci sono due programmi da tenere allineati a mano.

`dal_vivo=True` lo accende solo il servizio online: li' la dieta e il lavoro
dei progetti non ci sono, e la riga in fondo lo dice.
"""

from flask import render_template_string

import disegno
import lettura

PAGINA = """<!doctype html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Comodino</title>
<style>
  :root{
    --fondo:#11151c; --testo:#e8e6e1; --spento:#7b8794;
    --accento:#c9a227; --rosso:#b5533f; --riquadro:#171d26; --riga:#232b37;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--fondo);color:var(--testo);
       font:16px/1.5 "Iosevka","Consolas",ui-monospace,monospace;
       padding:28px 22px 60px}
  .dentro{max-width:1040px;margin:0 auto}
  h1{font-size:15px;letter-spacing:.22em;text-transform:uppercase;
     color:var(--spento);font-weight:500;margin:0 0 4px}
  .periodo{color:var(--spento);font-size:13px;margin-bottom:22px}
  .avviso{background:rgba(181,83,63,.14);border-left:3px solid var(--rosso);
          padding:10px 14px;margin:0 0 22px;font-size:13px;color:#e9c7bd}
  .tessere{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
           margin-bottom:26px}
  .tessera{background:var(--riquadro);border:1px solid var(--riga);border-radius:3px;
           padding:14px 16px}
  .tessera .etichetta{font-size:11px;letter-spacing:.14em;text-transform:uppercase;
                      color:var(--spento);margin-bottom:8px}
  .tessera .grosso{font-size:30px;line-height:1.1;font-weight:600;letter-spacing:-.01em}
  .tessera .coda{font-size:12px;color:var(--spento);margin-top:6px}
  .oro{color:var(--accento)} .rosso{color:var(--rosso)}
  h2{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--spento);
     font-weight:500;margin:30px 0 4px;border-top:1px solid var(--riga);padding-top:18px}
  .spiega{color:var(--spento);font-size:12.5px;margin:0 0 12px}
  .grafico{width:100%;height:auto;display:block}
  .zero{stroke:#39424f;stroke-width:1;stroke-dasharray:3 4}
  .tacca{fill:#5b6675;font-size:10px;letter-spacing:.1em}
  .sopra{fill:#c8ccd2;font-size:11px;text-anchor:middle}
  .sotto{fill:#6c7686;font-size:10.5px;text-anchor:middle}
  .piccolo{font-size:9px}
  .niente{color:var(--spento);font-size:13px}
  .spezzata{color:var(--spento);font-size:11px;font-weight:400;margin-left:7px;
            white-space:nowrap}
  .piccolino{color:var(--spento);font-size:12px}
  .presto{background:var(--riquadro);border-left:3px solid var(--accento);
          padding:14px 18px;margin-bottom:24px;font-size:14px;line-height:1.7}
  .due{display:grid;gap:18px;grid-template-columns:1.3fr 1fr;align-items:start}
  @media(max-width:820px){.due{grid-template-columns:1fr}}
  .foglio{background:var(--riquadro);border:1px solid var(--riga);border-radius:3px;
          padding:16px 18px;font-size:13.5px;max-height:460px;overflow:auto}
  .foglio .testo{white-space:pre-wrap;margin:0}
  .foglio h3{margin:0 0 10px;font-size:13px;color:var(--accento);letter-spacing:.1em}
  table{border-collapse:collapse;width:100%;font-size:13px}
  td,th{text-align:left;padding:5px 10px 5px 0;border-bottom:1px solid var(--riga)}
  th{color:var(--spento);font-weight:500;font-size:11px;letter-spacing:.12em;
     text-transform:uppercase}
  .fine{color:#4d5663;font-size:11.5px;margin-top:36px;border-top:1px solid var(--riga);
        padding-top:14px}
  a{color:var(--accento)}
</style></head><body><div class="dentro">

<h1>Comodino</h1>
{% if s.vuoto %}
  <p class="niente">In <code>salute\\sonno\\</code> non c'e' nessuna notte.
  Quando <code>ghealth</code> scrivera' i CSV, questa pagina si riempie da sola.</p>
{% else %}
<div class="periodo">{{ s.notti }} notti &nbsp;·&nbsp; dal {{ s.dal }} al {{ s.al }}
  {%- if s.mancanti %} &nbsp;·&nbsp; {{ s.mancanti }} notti non misurate{% endif %}</div>

{% if finti %}<div class="avviso"><b>Questi sono dati finti.</b>
  Inventati per vedere se la pagina ha la forma giusta. Quando arriva il Fitbit
  vero, cancelli i CSV in <code>salute\\sonno\\</code> e questa riga sparisce.</div>{% endif %}

{% if s.poche %}
<div class="presto">
  <b>{{ s.notti }} notti misurate. Sono ancora poche.</b><br>
  Medie, accumulo e confronti fra settimane cominciano a voler dire qualcosa
  da {{ s.soglia }} notti in su: ne mancano <b>{{ s.mancano }}</b>. Finche' non
  ci siamo questa pagina non calcola niente — ti mostra le notti come sono.
  Le curve compaiono da sole.
  {% if per_online %}<br><span class="piccolino">Sotto trovi anche i grafici:
  sono calcolati sui dati veri, ma con {{ s.notti }} notti la "tua media" e'
  fatta di quelle stesse {{ s.notti }} notti.</span>
  {% elif not comunque %}<br><a href="/?comunque=si">Mostramele lo stesso &rarr;</a>
  &nbsp;<span class="piccolino">(sono vere, solo non dicono ancora granche')</span>
  {% else %}<br><b>Stai guardando i grafici sotto soglia.</b> Sono calcolati sui
  dati veri, ma con {{ s.notti }} notti la "tua media" e' fatta di quelle stesse
  {{ s.notti }} notti: dice poco di piu' della tabella.
  <a href="/">Torna alla tabella &rarr;</a>{% endif %}
</div>

<h2>Le notti finora</h2>
<table>
  <tr><th>notte</th><th>dormito</th><th>a letto</th><th>sveglia</th>
      <th>efficienza</th><th>profondo</th><th>rem</th></tr>
  {% for n in s.elenco|reverse %}
  <tr><td>{{ n.data }}</td>
      <td><b>{{ o(n.minuti) }}</b>{% if n.sessioni > 1 %}
        <span class="spezzata">in {{ n.sessioni }} volte</span>{% endif %}</td>
      <td>{{ ora(n.a_letto) }}</td><td>{{ ora(n.sveglia) }}</td>
      <td>{{ n.efficienza or '--' }}%</td>
      <td>{{ o(n.profondo) }}</td><td>{{ o(n.rem) }}</td></tr>
  {% endfor %}
</table>
{% endif %}

{% if not s.poche or comunque or per_online %}

<div class="tessere">
  <div class="tessera">
    <div class="etichetta">accumulo, ultime {{ s.notti_recenti }} notti</div>
    <div class="grosso {{ 'rosso' if s.accumulo_recente < 0 else 'oro' }}">{{ o(s.accumulo_recente, 1) }}</div>
    <div class="coda">rispetto alla tua media di {{ o(s.media) }}</div>
  </div>
  <div class="tessera">
    <div class="etichetta">questa settimana, sommata</div>
    <div class="grosso">{{ o(ultima.minuti) }}</div>
    <div class="coda">{{ ultima.notti }} notti · {{ o(ultima.a_notte) }} a notte
      {%- if ultima.differenza_a_notte is not none %} · {{ o(ultima.differenza_a_notte, 1) }} a notte sulla precedente{% endif %}</div>
  </div>
  <div class="tessera">
    <div class="etichetta">notti di fila sotto la media</div>
    <div class="grosso {{ 'rosso' if s.striscia_ora >= 3 else '' }}">{{ s.striscia_ora }}</div>
    <div class="coda">record: {{ s.striscia_record }} · in tutto {{ s.notti_sotto }} su {{ s.notti }}</div>
  </div>
  <div class="tessera">
    <div class="etichetta">ti addormenti in media alle</div>
    <div class="grosso">{{ ora(s.media_letto) }}</div>
    <div class="coda">
      {%- if s.slittamento is not none %}nel fine settimana {{ o(s.slittamento, 1) }} ·{% endif %}
      scarto medio {{ o(s.irregolarita) }}</div>
  </div>
</div>

{% if s.ciclo %}
<h2>Il ciclo di {{ s.ciclo.giorni }} giorni</h2>
<p class="spiega">Ciclo {{ s.ciclo.numero }}: dal {{ s.ciclo.dal }} al {{ s.ciclo.al }},
  giorno {{ s.ciclo.giorno }} di {{ s.ciclo.giorni }}, {{ s.ciclo.notti }} notti misurate.
  {% if s.ciclo.chiuso %}Ciclo chiuso: la media e' <b>{{ o(s.ciclo.media) }}</b>
  (&plusmn;{{ o(s.ciclo.incertezza) }}).
  {%- else %}Il ciclo e' ancora aperto: la media di finora, <b>{{ o(s.ciclo.media) }}</b>
  (&plusmn;{{ o(s.ciclo.incertezza) }}), e' provvisoria. Diventa la tua media di
  riferimento il {{ s.ciclo.al }}.{% endif %}</p>
<table>
  <tr><th>settimana</th><th>notti</th><th>a notte</th><th>rispetto alla media</th></tr>
  {% for w in s.ciclo.settimane %}
  <tr><td>{{ w.dal }} &rarr; {{ w.al }}</td><td>{{ w.notti }}</td>
      <td><b>{{ o(w.a_notte) }}</b></td>
      <td class="{{ 'rosso' if w.scarto < 0 else 'oro' }}">{{ o(w.scarto, 1) }}</td></tr>
  {% endfor %}
</table>
{% if s.cicli_chiusi %}
<p class="spiega">Cicli chiusi:
  {% for c in s.cicli_chiusi %}ciclo {{ c.numero }} ({{ c.dal }} &rarr; {{ c.al }}):
  <b>{{ o(c.media) }}</b> a notte{% if not loop.last %} &nbsp;·&nbsp; {% endif %}{% endfor %}.</p>
{% endif %}
{% endif %}

{% if s.corrente %}
<h2>Questa settimana, e le notti che mancano</h2>
<table>
  <tr><th>settimana</th><th>notti</th><th>in tutto</th><th>a notte</th></tr>
  <tr><td><b>in corso</b></td><td>{{ s.corrente.notti }} su 7</td>
      <td>{{ o(s.corrente.minuti) }}</td><td><b>{{ o(s.corrente.a_notte) }}</b></td></tr>
  {% if s.corrente.precedente %}
  <tr><td>la precedente</td><td>{{ s.corrente.precedente.notti }} su 7</td>
      <td>{{ o(s.corrente.precedente.minuti) }}</td><td>{{ o(s.corrente.precedente.a_notte) }}</td></tr>
  {% endif %}
</table>
{% if s.corrente.rimanenti %}
<p class="spiega">La tua media settimanale e' 7 notti x {{ o(s.riferimento) }}{% if s.riferimento_provvisorio %} (provvisoria){% endif %} =
  <b>{{ o(s.corrente.obiettivo) }}</b>.
  {% if s.corrente.gia_sopra %}Questa settimana l'hai gia' raggiunta: le
  {{ s.corrente.rimanenti }} notti che mancano restano fuori dal conto.
  {%- else %}Per restarci servono ancora <b>{{ o(s.corrente.servono_totale) }}</b>
  nelle {{ s.corrente.rimanenti }} notti che mancano: circa
  <b class="oro">{{ o(s.corrente.servono_a_notte) }} a notte</b>.{% endif %}
  Non e' un fabbisogno: e' aritmetica sul tuo metro. Con {{ s.riferimento_notti }} notti
  la tua media ha ancora &plusmn;{{ o(s.riferimento_incertezza) }} di incertezza.</p>
{% endif %}
{% endif %}

<h2>L'accumulo, giorno per giorno</h2>
<p class="spiega">Ogni notte aggiunge o toglie rispetto alla tua media.
  Lo zero non e' un traguardo: e' la tua media del periodo.
  Sul giro intero la curva torna per forza a zero — quello che dice e' <b>dove</b>
  e' sprofondata e quanto c'e' voluto a risalire.
  Punto piu' basso: <b class="rosso">{{ o(s.fondo.minuti, 1) }}</b> il {{ s.fondo.data }}.</p>
{{ curva|safe }}

<h2>Una stanghetta per notte</h2>
<p class="spiega">Oro sopra la tua media, rosso sotto. Le notti del fine settimana
  sono piu' tenui. Ultime 70.</p>
{{ pettine|safe }}

<h2>Le ore sommate, settimana per settimana</h2>
<p class="spiega">Le settimane incomplete restano spente: tre notti non si
  confrontano con sette.</p>
{{ barre|safe }}

{% if s.confronto %}
<h2>Quattro settimane contro le quattro di prima</h2>
<table>
  <tr><th>periodo</th><th>a notte</th><th>in tutto</th></tr>
  <tr><td>ultime {{ s.confronto.notti_ora }} notti</td><td>{{ o(s.confronto.ora) }}</td>
      <td>{{ o(s.confronto.ora * s.confronto.notti_ora) }}</td></tr>
  <tr><td>le {{ s.confronto.notti_prima }} di prima</td><td>{{ o(s.confronto.prima) }}</td>
      <td>{{ o(s.confronto.prima * s.confronto.notti_prima) }}</td></tr>
  <tr><td><b>differenza</b></td>
      <td class="{{ 'rosso' if s.confronto.per_notte < 0 else 'oro' }}"><b>{{ o(s.confronto.per_notte, 1) }}</b></td>
      <td class="{{ 'rosso' if s.confronto.totale < 0 else 'oro' }}"><b>{{ o(s.confronto.totale, 1) }}</b></td></tr>
</table>
{% endif %}
{% endif %}
{% endif %}

{% if not dal_vivo -%}
<h2>La dieta, accanto</h2>
<div class="due">
  <div class="foglio">
    {% if settimana %}<h3>{{ settimana.settimana }}</h3><div class="testo">{{ settimana.testo }}</div>
    {% else %}<p class="niente">Nessuna settimana ancora scritta. Le foto vanno in
      <code>salute\\dieta\\in-arrivo\\</code>; il file della settimana nasce
      li' accanto, in <code>salute\\dieta\\2026\\</code>.</p>{% endif %}
  </div>
  <div>
    <div class="tessera">
      <div class="etichetta">foto ancora da leggere</div>
      <div class="grosso">{{ in_arrivo|length }}</div>
      <div class="coda">
        {%- for f in in_arrivo %}{{ f.nome }} ({{ f.quando }})<br>{% endfor %}
        {%- if not in_arrivo %}in-arrivo e' vuota{% endif %}</div>
    </div>
    {% if settimane_dieta|length > 1 %}
    <div class="tessera" style="margin-top:12px">
      <div class="etichetta">le settimane di prima</div>
      <div class="coda">{% for v in settimane_dieta[1:9] %}{{ v.settimana }}<br>{% endfor %}</div>
    </div>{% endif %}
  </div>
</div>

<h2>Il lavoro, per confronto</h2>
<p class="spiega">{{ scanner }}</p>{%- endif %}

<p class="fine">{% if dal_vivo %}Comodino &nbsp;·&nbsp; dati letti da Google Health a ogni apertura
  &nbsp;·&nbsp; i conti sono gli stessi del computer di casa{% elif per_online %}Comodino &nbsp;·&nbsp; i conti li ha fatti il
  computer di casa &nbsp;·&nbsp; questa pagina e' una copia depositata, e si
  aggiorna a ogni scarico{% else %}Comodino &nbsp;·&nbsp; gira solo su questo PC &nbsp;·&nbsp;
  i dati stanno in <code>salute\\</code> e si leggono col Blocco note anche
  senza questa pagina &nbsp;·&nbsp; gli stessi numeri a schermo nero:
  <code>python lettura.py</code>{% endif %}</p>
</div></body></html>"""


def disegna(conti, comunque=False, per_online=False, finti=False, dal_vivo=False,
            settimana=None, settimane_dieta=(), in_arrivo=(), scanner=''):
    pieno = not conti.get('vuoto')
    return render_template_string(
        PAGINA,
        s=conti,
        comunque=comunque,
        per_online=per_online,
        dal_vivo=dal_vivo,
        finti=finti,
        ultima=(conti['settimane'][-1] if pieno else None),
        curva=(disegno.curva_accumulo(conti['curva']) if pieno else ''),
        pettine=(disegno.pettine_notti(conti['curva']) if pieno else ''),
        barre=(disegno.barre_settimane(conti['settimane']) if pieno else ''),
        settimana=settimana,
        settimane_dieta=list(settimane_dieta),
        in_arrivo=list(in_arrivo),
        scanner=scanner,
        o=lettura.ore,
        ora=lettura.orologio,
    )

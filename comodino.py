# -*- coding: utf-8 -*-
"""La faccia pubblica di Comodino: due pagine, e nient'altro.

Comodino e' un programma che gira sul PC di casa. Non ha bisogno di un sito.
Queste due pagine esistono per una ragione sola: Google, per lasciar
pubblicare un'app OAuth, pretende l'indirizzo di una home page e quello di
un'informativa sulla privacy.

Allora invece di inventare un sito finto, le mettiamo qui -- dove un servizio
gia' acceso c'e' -- e diciamo la verita' su cosa fa quel programma.

**Queste pagine non leggono niente e non scrivono niente.** Non toccano la
cassetta, non toccano il repository, non hanno sessione e non chiedono la
parola: sono due fogli di testo con dentro delle informazioni vere.

    /comodino            la home page
    /comodino/privacy    l'informativa
"""

import datetime

AGGIORNATA = '5 ottobre 2026'
CHI = 'Gaetano D’Agostino'
POSTA = 'gae7799@gmail.com'

_STILE = """
  :root{--fondo:#11151c;--testo:#e8e6e1;--spento:#7b8794;--accento:#c9a227;
        --riquadro:#171d26;--riga:#232b37}
  *{box-sizing:border-box}
  body{margin:0;background:var(--fondo);color:var(--testo);
       font:16px/1.75 -apple-system,"Segoe UI",system-ui,sans-serif;
       padding:56px 20px 90px}
  .dentro{max-width:660px;margin:0 auto}
  .segno{display:block;margin-bottom:26px}
  h1{font-size:15px;letter-spacing:.24em;text-transform:uppercase;
     color:var(--spento);font-weight:500;margin:0 0 26px}
  h2{font-size:13px;letter-spacing:.16em;text-transform:uppercase;
     color:var(--spento);font-weight:500;margin:38px 0 10px;
     border-top:1px solid var(--riga);padding-top:22px}
  p{margin:0 0 16px}
  .grande{font-size:21px;line-height:1.6}
  ul{margin:0 0 16px;padding-left:20px}
  li{margin-bottom:8px}
  code{background:var(--riquadro);padding:2px 6px;border-radius:3px;
       font-size:13.5px;color:var(--accento)}
  a{color:var(--accento)}
  .fine{color:#4d5663;font-size:13px;margin-top:46px;
        border-top:1px solid var(--riga);padding-top:18px}
"""

# Il segno di Comodino, disegnato qui dentro: una lampada e il piano.
# In SVG e non come immagine, cosi' la pagina resta un file solo.
_SEGNO = """<svg class="segno" width="52" height="52" viewBox="0 0 120 120"
  role="img" aria-label="Comodino"><circle cx="60" cy="50" r="28" fill="#c9a227"/>
  <rect x="20" y="88" width="80" height="6" rx="3" fill="#c9a227"/></svg>"""


def _foglio(titolo, corpo):
    return ("""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><style>%s</style></head><body><div class="dentro">%s%s
<p class="fine">%s &nbsp;&middot;&nbsp; %s &nbsp;&middot;&nbsp;
aggiornata il %s</p></div></body></html>"""
            % (titolo, _STILE, _SEGNO, corpo, CHI, POSTA, AGGIORNATA))


CASA = _foglio('Comodino', """
<h1>Comodino</h1>

<p class="grande">Comodino &egrave; un programma personale che tiene insieme
due cose: <b>quanto dormo</b> e <b>la dieta della settimana</b>.</p>

<p>Non &egrave; un servizio e non &egrave; un prodotto. Gira sul computer di
casa di %s, non ha utenti, non ha registrazione, non ha un account da creare.
Chi lo usa &egrave; una persona sola, ed &egrave; la stessa che l'ha scritto.</p>

<h2>Cosa fa</h2>

<p>Legge dal proprio account Google, <b>in sola lettura</b>, i dati di sonno e
di attivit&agrave; misurati da un Fitbit, e li scrive in file di testo sul
disco di casa. Poi li mostra in una pagina che si apre solo su quel computer,
accanto al foglio della dieta della settimana.</p>

<p>Non d&agrave; consigli, non assegna punteggi e non giudica n&eacute; il
sonno n&eacute; quello che si mangia. Conta, e mostra quello che ha contato.</p>

<p>Il titolare pu&ograve; guardare i propri dati di sonno anche dal telefono.
Premendo &laquo;Collega Google Health&raquo;, questo servizio legge il sonno
direttamente da Google Health a ogni apertura della pagina, con il permesso di
sola lettura del titolare. Se il collegamento manca o Google non risponde,
mostra l'ultima pagina riassuntiva depositata dal computer di casa. La vede lui
e nessun altro: &egrave; protetta dall'accesso con Google e riservata a un solo
indirizzo.</p>

<h2>Cosa non fa</h2>

<ul>
  <li>su questo servizio i dati di sonno non vengono scritti su nessun disco:
      restano in memoria per un paio di minuti e poi si rileggono da Google.
      Sul disco del servizio c'&egrave; solo il permesso di lettura (un gettone
      di rinnovo), non i dati</li>
  <li>non condivide niente con nessuno, e non vende niente a nessuno</li>
  <li>non scrive nulla sull'account Google: i permessi che chiede sono
      entrambi di sola lettura</li>
  <li>non raccoglie dati di altre persone, perch&eacute; altre persone non
      lo usano</li>
</ul>

<p><a href="/comodino/privacy">Come vengono trattati i dati &rarr;</a></p>
""" % CHI)


PRIVACY = _foglio('Comodino &mdash; norme sulla privacy', """
<h1>Comodino &mdash; norme sulla privacy</h1>

<p class="grande">Comodino &egrave; usato da una persona sola. I conti si
fanno sul suo computer; questo servizio serve solo a fargli vedere il
risultato dal telefono, e non lo mostra a nessun altro.</p>

<h2>Chi tratta i dati</h2>
<p>%s &mdash; <a href="mailto:%s">%s</a>. Nessuna societ&agrave;, nessun
terzo, nessun responsabile esterno.</p>

<h2>Quali dati</h2>
<p>Tramite la Google Health API, e solo per l'account Google del titolare,
Comodino legge:</p>
<ul>
  <li><code>googlehealth.sleep.readonly</code> &mdash; le sessioni di sonno:
      ora di inizio e fine, minuti dormiti, fasi del sonno</li>
  <li><code>googlehealth.activity_and_fitness.readonly</code> &mdash;
      il conteggio dei passi</li>
</ul>
<p><b>Entrambi i permessi sono di sola lettura.</b> Comodino non ha, e non
chiede, la facolt&agrave; di scrivere, modificare o cancellare alcun dato
sull'account Google.</p>
<p>Per far entrare il titolare in questa pagina viene usato anche
&laquo;Accedi con Google&raquo;, che comunica <b>soltanto il suo indirizzo
email</b>, per verificare che sia lui e non un altro.</p>

<h2>Dove finiscono</h2>
<p>Lo storico completo &mdash; tutte le notti, tutti i giorni &mdash; sta in
file di testo <b>sul computer personale del titolare</b>, e non viene mai
trasmesso a nessuno.</p>
<p>Quel computer prepara una pagina riassuntiva dei propri dati e la deposita
su questo servizio, perch&eacute; il titolare possa guardarla dal telefono.
Quella pagina:</p>
<ul>
  <li><b>resta soltanto in memoria</b>: non viene scritta su nessun disco di
      questo servizio, e sparisce a ogni suo riavvio</li>
  <li>viene <b>sostituita</b> dalla successiva a ogni deposito</li>
  <li>&egrave; mostrata <b>solo dopo l'accesso con Google</b>, e solo a un
      unico indirizzo email stabilito. Chiunque altro apra il link non vede
      nulla, nemmeno conoscendolo</li>
</ul>
<p>Se il titolare collega Google Health a questo servizio:</p>
<ul>
  <li>i dati di sonno sono letti da Google a ogni apertura della pagina, ridotti
      a conti e grafici, e tenuti in memoria al massimo per un paio di minuti;
      non vengono scritti su nessun disco e spariscono a ogni riavvio</li>
  <li>l'unica cosa che il servizio ricorda &egrave; il gettone di rinnovo del
      permesso (sola lettura sul sonno), in un file riservato nel volume del
      servizio. Con quel gettone non si pu&ograve; scrivere n&eacute; cancellare
      nulla sull'account</li>
</ul>
<p>I dati non vengono venduti, ceduti, pubblicati, n&eacute; usati per
pubblicit&agrave;, profilazione o addestramento di modelli.</p>

<h2>Per quanto tempo</h2>
<p>Sul computer di casa: finch&eacute; il titolare tiene quei file. Si
cancellano cancellando i file. Su questo servizio: i dati di sonno al
massimo qualche minuto, in memoria; il gettone di rinnovo finch&eacute; il
titolare non preme &laquo;scollega&raquo; o non toglie il permesso dal proprio
account Google.</p>

<h2>Come si revoca l'accesso</h2>
<p>Da <a href="https://myaccount.google.com/permissions">
myaccount.google.com/permissions</a>, togliendo l'autorizzazione all'app
&laquo;Comodino&raquo;. Da quel momento il programma non legge pi&ugrave;
nulla e l'accesso a questa pagina non funziona pi&ugrave;. I file gi&agrave;
scritti sul disco di casa restano, e si cancellano a mano.</p>
<p>Dalla pagina riservata c'&egrave; anche il tasto &laquo;scollega&raquo;:
revoca il permesso presso Google e cancella il gettone da questo servizio.</p>

<h2>Questa pagina</h2>
<p>Non usa cookie, non ha strumenti di statistica e non registra chi la
visita. La pagina riservata usa un solo cookie tecnico, quello che tiene
l'accesso, e serve unicamente a non dover rifare l'accesso ogni volta.</p>
""" % (CHI, POSTA, POSTA))


def aggancia(app):
    """Due rotte in piu', e nessun effetto su quelle che c'erano gia'."""

    @app.route('/comodino')
    def comodino_casa():
        return CASA

    @app.route('/comodino/privacy')
    def comodino_privacy():
        return PRIVACY

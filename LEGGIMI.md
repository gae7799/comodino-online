# Comodino online

Servizio separato da Sentinella: repository proprio, dominio proprio su
Railway. Non calcola niente — mostra solo il foglio che il PC di casa
deposita su `/comodino/deposita`.

## Le 4 variabili da mettere su Railway

    COMODINO_CLIENT_ID       client OAuth "Applicazione web" (Google Cloud Console)
    COMODINO_CLIENT_SECRET   il suo segreto
    COMODINO_EMAIL           gae7799@gmail.com
    COMODINO_DEPOSITO        una parola a scelta — la stessa va in
                              motore/comodino/segreti.json come "parola_deposito"

## Il redirect URI da registrare sul client OAuth

    https://<dominio-di-questo-servizio>.up.railway.app/comodino/entrato

## Dopo il primo deploy

In `motore/comodino/configurazione.json`, cambiare `servizio_online` con
l'indirizzo di questo servizio, poi lanciare `pubblica.bat` una volta.

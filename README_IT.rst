====================================
Invio Email Contratti d'Acquisto
====================================

A cosa serve
============

Questo modulo aggiunge la possibilità di inviare un contratto d'acquisto
(Purchase Agreement / Accordo Quadro) direttamente via email al fornitore,
dalla scheda del contratto stesso.

Funzionalità
============

* Nuovo pulsante **"Send by Email"** nella scheda del contratto d'acquisto,
  in alto vicino agli altri pulsanti di stato (Conferma, Chiudi, Annulla...).
* Cliccando il pulsante si apre una finestra per comporre l'email, già
  precompilata con un modello (template) standard: oggetto e testo con nome
  del contratto e nome del fornitore. Il testo può comunque essere modificato
  prima dell'invio.
* Il destinatario predefinito è il fornitore indicato sul contratto.
* Dopo l'invio dell'email, il contratto passa automaticamente allo stato
  **"Sent" (Inviato)**, così è possibile distinguere a colpo d'occhio i
  contratti già inviati al fornitore da quelli ancora in bozza.
* Il numero/riferimento del contratto viene generato automaticamente alla
  creazione (sequenza numerica), come già avviene di norma per i documenti
  Odoo.

Come si usa
===========

1. Aprire un contratto d'acquisto (Acquisti > Ordini > Accordi Quadro).
2. Cliccare sul pulsante **"Send by Email"** in alto.
3. Verificare/modificare oggetto e testo dell'email nella finestra che si apre.
4. Inviare: il contratto passa in stato **"Sent"**.

Configurazione
==============

Nessuna configurazione aggiuntiva richiesta: il modulo funziona subito
dopo l'installazione.

# Copyright Mint System GmbH, Odoo Community Association (OCA)
# License AGPL-3
from odoo import Command
from odoo.tests import TransactionCase, tagged

MODELLO = 'purchase_requisition_send.email_template_purchase_requisition'


@tagged('post_install', '-at_install')
class TestInvioAccordoAcquisto(TransactionCase):
    """L'invio dell'accordo d'acquisto al fornitore."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fornitore = cls.env['res.partner'].create({
            'name': 'Fornitore accordo', 'email': 'fornitore@example.org'})
        cls.prodotto = cls.env['product.product'].create({
            'name': 'Prodotto accordo', 'is_storable': True})
        # una riga serve: il core rifiuta di confermare un accordo vuoto
        cls.accordo = cls.env['purchase.requisition'].create({
            'vendor_id': cls.fornitore.id,
            'line_ids': [Command.create({
                'product_id': cls.prodotto.id, 'product_qty': 10.0,
                'price_unit': 25.0})],
        })

    # ---------------------------------------------------------- lo stato

    def test_lo_stato_inviato_esiste_e_sta_prima_di_confermato(self):
        stati = [codice for codice, _etichetta
                 in self.env['purchase.requisition']._fields['state'].selection]
        self.assertIn('sent', stati)
        self.assertLess(stati.index('sent'), stati.index('confirmed'),
                        "«inviato» sta fra la bozza e la conferma")

    def test_gli_stati_rimossi_dalla_19_non_vengono_reintrodotti(self):
        stati = [codice for codice, _etichetta
                 in self.env['purchase.requisition']._fields['state'].selection]
        for morto in ('ongoing', 'in_progress', 'open'):
            self.assertNotIn(morto, stati,
                             "%s non è più uno stato di purchase.requisition" % morto)

    def test_state_blanket_order_non_viene_reintrodotto(self):
        self.assertNotIn('state_blanket_order',
                         self.env['purchase.requisition']._fields,
                         "il campo è stato rimosso da Odoo 19")

    # ---------------------------------------------------------- l'invio

    def test_l_azione_apre_la_composizione_col_modello(self):
        azione = self.accordo.action_order_send()
        self.assertEqual(azione['res_model'], 'mail.compose.message')
        contesto = azione['context']
        self.assertEqual(contesto['default_template_id'], self.env.ref(MODELLO).id)
        self.assertEqual(contesto['default_res_ids'], self.accordo.ids)
        self.assertTrue(contesto['mark_pr_as_sent'])

    def test_mandando_il_messaggio_l_accordo_passa_a_inviato(self):
        self.assertEqual(self.accordo.state, 'draft')

        self.accordo.with_context(mark_pr_as_sent=True).message_post(
            body="Accordo mandato al fornitore")

        self.assertEqual(self.accordo.state, 'sent')

    def test_un_messaggio_normale_non_cambia_lo_stato(self):
        self.accordo.message_post(body="Nota interna")
        self.assertEqual(self.accordo.state, 'draft',
                         "senza il contrassegno nel contesto lo stato non si tocca")

    def test_un_accordo_confermato_non_torna_a_inviato(self):
        self.accordo.action_confirm()
        stato = self.accordo.state

        self.accordo.with_context(mark_pr_as_sent=True).message_post(body="Ancora")

        self.assertEqual(self.accordo.state, stato,
                         "solo le bozze passano a «inviato»")

    # ------------------------------------------------- il modello di email

    def test_il_modello_usa_la_sintassi_qweb(self):
        """Il sorgente 17.0 era rimasto alla sintassi Jinja `${ }`, abbandonata da
        Odoo 16: su un'installazione nuova le email uscivano coi segnaposto
        scritti a lettere. Sul database del cliente il record era già stato
        convertito dall'aggiornamento, e `noupdate` lo aveva protetto."""
        modello = self.env.ref(MODELLO)
        for testo in (modello.subject, modello.email_from,
                      modello.partner_to, modello.lang,
                      modello.body_html or ''):
            self.assertNotIn('${', str(testo),
                             "sintassi Jinja rimasta: %s" % testo)
        self.assertIn('{{', modello.subject)
        self.assertIn('t-out', str(modello.body_html))

    def test_il_modello_si_rende_sul_fornitore(self):
        modello = self.env.ref(MODELLO)
        reso = modello._render_field('subject', self.accordo.ids)[self.accordo.id]
        self.assertIn(self.accordo.name, reso,
                      "l'oggetto deve contenere il numero dell'accordo")
        corpo = modello._render_field('body_html', self.accordo.ids)[self.accordo.id]
        self.assertIn('Fornitore accordo', corpo,
                      "e il corpo il nome del fornitore")

    # ------------------------------------------------------------ la vista

    def test_il_pulsante_e_nella_vista(self):
        arch = self.env['purchase.requisition'].get_views(
            [(False, 'form')])['views']['form']['arch']
        self.assertIn('action_order_send', arch)
        self.assertIn('draft,sent,confirmed,done', arch,
                      "la barra di stato deve mostrare anche «inviato»")

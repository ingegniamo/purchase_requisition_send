# Copyright Mint System GmbH, Odoo Community Association (OCA)
# License AGPL-3
from odoo import _, fields, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    # In 19.0 gli stati del core sono draft, confirmed, done, cancel: `ongoing`,
    # `in_progress` e `open`, su cui si appoggiava la versione 17.0, non esistono
    # più. `sent` si inserisce prima di `confirmed`, che è il posto che prima
    # occupava `ongoing`.
    state = fields.Selection(
        selection_add=[("sent", "Sent"), ("confirmed",)],
        ondelete={"sent": "cascade"},
    )

    # `state_blanket_order` non si estende più: in 19.0 quel campo non esiste.
    # `name` non si ridichiara più: il core ha già default=lambda self: _('New'),
    # mentre la versione 17.0 scriveva default=_('New') — valutato
    # all'importazione del modulo, quindi tradotto una volta sola nella lingua di
    # chi caricava il registro.
    #
    # Anche `create()` è stato rimosso: numerava l'accordo scegliendo fra due
    # sequenze in base a `purchase.requisition.type.quantity_copy`. In 19.0 il
    # modello `purchase.requisition.type` non esiste più e la numerazione la fa il
    # core, che sceglie fra le stesse due sequenze in base a `requisition_type`.

    def action_order_send(self):
        """Apre la finestra di composizione dell'email col modello del modulo."""
        self.ensure_one()
        modello = self.env.ref(
            "purchase_requisition_send.email_template_purchase_requisition"
        )
        modulo_composizione = self.env.ref("mail.email_compose_message_wizard_form")
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(modulo_composizione.id, "form")],
            "view_id": modulo_composizione.id,
            "target": "new",
            "context": {
                "default_model": "purchase.requisition",
                "default_res_ids": self.ids,
                "default_template_id": modello.id,
                "default_composition_mode": "comment",
                "mark_pr_as_sent": True,
                "force_email": True,
            },
        }

    # 19.0: `odoo.api.returns` non esiste più, e `message_post` del core non lo
    # usa (la sua firma è a soli argomenti nominali). L'override resta un
    # passthrough con **kwargs.
    def message_post(self, **kwargs):
        if self.env.context.get("mark_pr_as_sent"):
            # 17.0 filtrava su ['draft', 'in_progress']: `in_progress` non è più
            # uno stato, resta la bozza.
            self.filtered(lambda accordo: accordo.state == "draft").write(
                {"state": "sent"}
            )
        return super().message_post(**kwargs)

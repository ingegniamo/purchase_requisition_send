from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)
import mimetypes

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"
    
    name = fields.Char(default=_('New'))
    state = fields.Selection(selection_add=[
        ('sent', 'Sent'),
        ('ongoing',)
    ], ondelete={'sent': 'cascade'})
    state_blanket_order = fields.Selection(selection_add=[
        ('sent', 'Sent'),
        ('ongoing',)
    ], ondelete={'sent': 'cascade'})

    def get_attachment_ids_product(self):
        attachment_ids = self.env['ir.attachment']
        for line in self.line_ids:
            if line.product_id.design_file_download:
                name = ""
                name += "[" + line.product_id.barcode + "] " + "[Design File]" + line.product_id.name
                attachment_id= self.env['ir.attachment'].create({'name': name,
                                                                    'res_model': 'purchase.requisition',
                                                                    'datas': line.product_id.design_file_download,
                                                                    'type': 'binary',
                                                                    'res_id': self.id})
                extension = mimetypes.guess_extension(attachment_id.mimetype)
                attachment_id.name = '%s%s' % (attachment_id.name,extension)
                attachment_ids |=attachment_id
            if line.product_id.cable_length:
                name = ""
                name += "[" + line.product_id.barcode + "] " + "[Lunghezza Cavi]" + line.product_id.name
                attachment_id= self.env['ir.attachment'].create({'name': name,
                                                                    'res_model': 'purchase.requisition',
                                                                    'datas': line.product_id.cable_length,
                                                                    'type': 'binary',
                                                                    'res_id': self.id})
                extension = mimetypes.guess_extension(attachment_id.mimetype)
                attachment_id.name = '%s%s' % (attachment_id.name,extension)
                attachment_ids |=attachment_id
            if line.product_id.extra_file:
                name = ""

                name = line.product_id.extra_file_file_name or "[" + line.product_id.barcode + "] " + "[File extra]" + line.product_id.name
                attachment_id = self.env['ir.attachment'].create({'name': name,
                                                                  'res_model': 'purchase.requisition',
                                                                  'datas': line.product_id.extra_file,
                                                                  'type': 'binary',
                                                                  'res_id': self.id})
                # extension = mimetypes.guess_extension(attachment_id.mimetype)
                # attachment_id.name = '%s%s' % (attachment_id.name,extension)
                attachment_ids |= attachment_id

        return attachment_ids

    @api.model
    def create(self,vals):
        """Generate name from sequence on create"""
        # _logger.warning([_('New'), vals.get('name', _('New')), vals.get('type_id'), (vals.get('name', _('New')) ==  _('New')) and vals.get('type_id')])
        if (vals.get('name', _('New')) ==  _('New')) and vals.get('type_id'):
            type_id = self.env['purchase.requisition.type'].browse(vals['type_id'])
            if type_id.quantity_copy != 'none':
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.requisition.blanket.order')
        return super().create(vals)

    def action_order_send(self):
        """Opens a wizard to compose an email, with relevant mail template loaded by default"""
        self.ensure_one()
        
        lang = self.env.context.get('lang')
        template = self.env.ref('purchase_requisition_send.email_template_purchase_requisition')
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]

        compose_form = self.env.ref('mail.email_compose_message_wizard_form')

        attachment_ids_product = self.get_attachment_ids_product()

        ctx = {
            'default_model': 'purchase.requisition',
            'default_res_id': self.ids[0],
            'default_attachment_ids': attachment_ids_product.ids,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'mark_pr_as_sent': True,
            'force_email': True,
        }  
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_pr_as_sent'):
            self.filtered(lambda o: o.state in ['draft', 'in_progress']).write({'state': 'sent'})
        return super().message_post(**kwargs)

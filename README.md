# Purchase Requisition Send

[![License: AGPL-3](https://img.shields.io/badge/License-AGPL_3-orange.svg?color=F1972B)](https://www.gnu.org/licenses/agpl-3.0)
[![Odoo 19.0](https://img.shields.io/badge/Odoo-19.0-blue.svg?color=F1972B)](https://github.com/ingegniamo/purchase_requisition_send)

Send the purchase agreement to the vendor by email.

## What it does

The purchase agreement gets a **Send by Email** button: it opens the composer with
a template already addressed to the agreement's vendor.

Once sent, the agreement moves to the **Sent** state, which sits between draft and
confirmed — so it is obvious at a glance which agreements are already in the
vendor's hands.

## Changelog

### 19.0.1.0.0

Odoo 19 absorbed or removed half of what this module used to do.

- **Odoo 19 API, the states changed:** `purchase.requisition.state` is now
  `draft, confirmed, done, cancel`. The 17.0 values `ongoing`, `in_progress` and
  `open` are **gone**, and `selection_add` anchored on `ongoing`. `sent` is now
  inserted before `confirmed`. Three tests hold this down.
- **Odoo 19 API, `state_blanket_order` no longer exists** — that field extension
  is gone.
- **Odoo 19 API, `purchase.requisition.type` no longer exists.** The whole
  `create()` override — which picked between two sequences based on
  `type_id.quantity_copy` — is **removed**: Odoo 19 numbers the agreement itself,
  choosing between the same two sequences based on `requisition_type`.
- **Odoo 19 API:** `name` is no longer redeclared. The core already has
  `default=lambda self: _('New')`, while the 17.0 version wrote `default=_('New')`
  — evaluated at module import, so translated once, in whatever language happened
  to load the registry.
- **Odoo 19 API:** `odoo.api.returns` no longer exists, and the core's
  `message_post` does not use it.
- **Fixed, the emails went out broken:** the mail template still used the Jinja
  `${ }` syntax, which Odoo abandoned in 16.0. On a fresh install the placeholders
  came out as literal text. On the client's database the record had already been
  converted to `{{ }}` by Odoo's own upgrade, and `noupdate="1"` protected it — so
  the live emails were fine while the source was not. The source now carries the
  converted text, and a test asserts no `${` survives anywhere in the template.
- The `get_attachment_ids_product` block, commented out in 17.0, is not carried
  over: the attachments are built by `mail.compose.message` in
  `purchase_terzani_custom`.
- The Send button is hidden once the agreement leaves draft or sent.
- Add a test suite (10 tests) and this README.

## Credits

**Authors**

* Mint System GmbH, Odoo Community Association (OCA)

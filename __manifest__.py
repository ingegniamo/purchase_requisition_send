{
    "name": "Purchase Requisition Send",
    "summary": "Manda l'accordo d'acquisto al fornitore per email",

    "description": """
Purchase Requisition Send
=========================

Sull'accordo d'acquisto compare **Send by Email**: apre la composizione con un
modello già pronto, indirizzato al fornitore dell'accordo.

Mandandolo, l'accordo passa allo stato **Sent**, che si inserisce fra la bozza e la
conferma: si vede a colpo d'occhio quali accordi sono già in mano al fornitore e
quali no.
""",

    "author": "Mint System GmbH, Odoo Community Association (OCA)",
    "website": "https://www.mint-system.ch",
    "category": "Purchase",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",

    "depends": ["purchase_requisition"],

    "data": [
        "data/mail_data.xml",
        "views/purchase_requisition_views.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False,
}

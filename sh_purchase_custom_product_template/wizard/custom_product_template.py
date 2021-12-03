from odoo.exceptions import Warning
from odoo import models, fields, _

class CustomProductTemplateWizard(models.TransientModel):

    _name = 'custom.product.template.wizard'

    _description = 'Custom Product Template Wizard'

    message = fields.Text(string="Demandes de prix créées pour les différents fournisseurs", readonly=True, store=True)
# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api
from datetime import datetime


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_parent = fields.Many2many("mrp.bom", "mrp_bom_rel", "mrp_bom_rel_id",string="Nomenclatures parents")
    bom_parent_ids = fields.Char('Nomenclature parent', compute = "_compute_bom_parent_ids", store = True)

    @api.depends('bom_parent')
    def _compute_bom_parent_ids(self):
        for rec in self:
            if rec.bom_parent:
                bom_parent_ids = ','.join ([p.display_name for p in rec.bom_parent])
            else:
                bom_parent_ids = ''
            rec.bom_parent_ids = bom_parent_ids


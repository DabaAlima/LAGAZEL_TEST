# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api
from datetime import datetime


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mo_childs_done = fields.Boolean('MO children terminés', compute = "_compute_mo_childs_done")

    def _compute_mo_childs_done(self):
        if self.mrp_production_child_count > 0:
            mrp_production_ids = self.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids
            self.mo_childs_done = all(m.state =='done' for m in mrp_production_ids)
        else:
            self.mo_childs_done = False


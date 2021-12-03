# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api
from datetime import datetime


class PurchaseProductTemplateLine(models.Model):
    _name = 'purchase.product.template.line'
    _description = "Purchase Product Template Line"

    name = fields.Many2one("product.product", string="Product", required=True)
    description = fields.Char("Description")
    ordered_qty = fields.Float("Ordered Qty", digits='Ordered Qty')
    unit_price = fields.Float("Unit Price", digits='Unit Price')
    product_uom = fields.Many2one("uom.uom", string="Uom")
    purchase_template_id = fields.Many2one(
        "purchase.product.template", string="purchase Template Id")
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    supplier_id = fields.Many2one('res.partner', string="Fournisseur", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


    @api.onchange('name')
    def product_change(self):
        if self.name:
            product_obj = self.env['product.product'].search(
                [('id', '=', self.name.id), ('purchase_ok', '=', True)])
            if product_obj:
                self.description = product_obj.display_name
                self.ordered_qty = 1
                self.unit_price = product_obj.list_price
                self.product_uom = product_obj.uom_id.id
                self.default_qty = 1


class PurchaseProductTemplate(models.Model):
    _name = 'purchase.product.template'
    _description = "Purchase Product Template"

    name = fields.Char("Template", required=True)
    purchase_product_template_ids = fields.One2many(
        "purchase.product.template.line", "purchase_template_id", string="purchase Product Line")
    templ_active = fields.Boolean("Active", default=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    kit_id = fields.Many2many(
        "mrp.bom", string="Kits")
    product_template_qty = fields.Float("Quantité", required=True, default = 1)
    kit_number = fields.Integer("Nombre de kits", compute = "_compute_kit_number", store=True)

    def create_purchase_orders_by_vendor(self):
        if self.purchase_product_template_ids:
            products_purchase_order = []
            #Groupe les lignes par fournisseur
            groups = self.env['purchase.product.template.line'].read_group([('purchase_template_id', '=', self.id)], ['supplier_id'], ['supplier_id'])
            for group in groups:
                if group['supplier_id'][0]:
                    products = self.env['purchase.product.template.line'].search([('purchase_template_id', '=', self.id),('supplier_id', '=', group['supplier_id'][0])])
                    #Pour chaque fournisseur, crée une demande de prix avec les infos des produits
                    for product_line in products:
                        products_purchase_order.append((0, 0, {
                            'product_id' : product_line.name.id,
                            'name' : product_line.description if product_line.description else '',
                            'product_qty' : product_line.ordered_qty,
                            'product_uom' : product_line.product_uom.id,
                            'price_unit' : product_line.unit_price

                    }))
                    purchase_order = self.env['purchase.order'].create({
                        'partner_id': group['supplier_id'][0],
                        'order_line' : products_purchase_order,
                        'product_template_id': self.id,
                    })
                    products_purchase_order = []

            #Affichage du message qui confirme la création des demandes de prix
            return {
                'name': 'generation.purchase.order',
                'type': 'ir.actions.act_window',
                'res_model': 'custom.product.template.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new'

                  }

    @api.depends('kit_id')
    def _compute_kit_number(self):
        self.kit_number = 0
        if self.kit_id:
            self.kit_number = len(self.kit_id)

    @api.model
    @api.onchange('kit_number')
    def kit_id_change(self):
        if self.kit_id:
            real_object_list=[]
            real_object_list = self.mapped("kit_id").ids
            self.purchase_product_template_ids = False
            for kit_id in real_object_list:
                kit = self.env['mrp.bom'].search([('id', '=', kit_id)])
                product_template_line = []
                for record in kit.bom_line_ids:
                    supplier_id = False
                    unit_price = 0
                    if record.product_id.bom_count >0:
                        # Prend en compte la nomenclature de la variante d'article
                        bom_ids = self.env['mrp.bom'].search([('product_id', '=', record.product_id.id)])
                        if bom_ids.id == False:
                            #Si ce n'est pas la nomenclature d'une variante
                            bom_ids = record.product_id.bom_ids[0]
                        if bom_ids.bom_line_ids:
                            for rec in bom_ids.bom_line_ids:
                                if rec.product_id.purchase_ok:
                                    vals = {}
                                    if rec.product_id.seller_ids:
                                        supplier_id = rec.product_id.seller_ids[0].name
                                        unit_price = rec.product_id.seller_ids[0].price
                                    vals.update({'name': rec.product_id.id, 'ordered_qty': self.product_template_qty * rec.product_qty, 'product_uom': rec.product_uom_id.id, 'description': rec.product_id.display_name, 'supplier_id': supplier_id, 'unit_price': unit_price})
                                    product_template_line.append((0, 0, vals))
                    else:
                        if record.product_id.purchase_ok:
                            vals = {}
                            if record.product_id.seller_ids:
                                supplier_id = record.product_id.seller_ids[0].name
                                unit_price = record.product_id.seller_ids[0].price
                            vals.update({'name': record.product_id.id, 'ordered_qty': self.product_template_qty * record.product_qty, 'product_uom': record.product_uom_id.id, 'description': record.product_id.display_name, 'supplier_id': supplier_id, 'unit_price': unit_price})
                            product_template_line.append((0, 0, vals))
                self.purchase_product_template_ids = product_template_line
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    @api.onchange('product_template_qty')
    def product_template_qty_change(self):
        if self.purchase_product_template_ids:
            # Call onchange to update quantity for each product template line
            self.kit_id_change()
            #for product_template_line in self.purchase_product_template_ids:
                #product_template_line.ordered_qty = self.product_template_qty * product_template_line.ordered_qty




class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    product_template_id = fields.Many2one(
        "purchase.product.template", string="Product Template")

    #OLD
    # @api.model
    # @api.onchange('product_template_id')
    # def product_template_id_change(self):
    #     if self.product_template_id:
    #         self.order_line = False
    #         purchase_ordr_line = []
    #         for record in self.product_template_id.purchase_product_template_ids:
    #             vals = {}
    #             vals.update({'price_unit': record.unit_price,
    #                          'name': record.description, 'product_qty': record.ordered_qty, 'product_uom': record.product_uom.id, 'date_planned': datetime.now()})
    #             if record.name:
    #                 vals.update({'product_id': record.name.id})
    #             purchase_ordr_line.append((0, 0, vals))
    #         self.order_line = purchase_ordr_line
    #     return {'type': 'ir.actions.client', 'tag': 'reload'}

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    product_template_id = fields.Many2one(
        "purchase.product.template", string="Product Template")

    @api.model
    @api.onchange('product_template_id')
    def product_template_id_change(self):
        if self.product_template_id:
            self.line_ids = False
            purchase_req_line = []
            for record in self.product_template_id.purchase_product_template_ids:
                vals = {}
                vals.update({'price_unit': record.unit_price,
                             'display_name': record.description, 'product_qty': record.ordered_qty, 'product_uom_id': record.product_uom.id, 'schedule_date': datetime.now()})
                if record.name:
                    vals.update({'product_id': record.name.id})
                purchase_req_line.append((0, 0, vals))
            self.line_ids = purchase_req_line
        return {'type': 'ir.actions.client', 'tag': 'reload'}


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    product_template_id = fields.Many2one(
        "purchase.product.template", string="Product Template")


    @api.model
    @api.onchange('product_template_id')
    def product_template_id_change(self):
        if self.product_template_id:
            self.move_ids_without_package = False
            stock_picking_line = []
            for record in self.product_template_id.purchase_product_template_ids:
                vals = {}
                vals.update({'product_id': record.name.id,'product_uom_qty': record.ordered_qty, 'product_uom': record.product_uom.id, 'name': record.name.display_name})
                stock_picking_line.append((0, 0, vals))
            self.move_ids_without_package = stock_picking_line
        return {'type': 'ir.actions.client', 'tag': 'reload'}

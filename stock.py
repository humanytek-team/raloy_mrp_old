# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from openerp import api
from openerp.exceptions import UserError, RedirectWarning, ValidationError
from odoo.addons import decimal_precision as dp

from datetime import datetime
from dateutil import relativedelta
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_round, float_is_zero

class StockMove(models.Model):
    _inherit = 'stock.move'

    # def write(self,vals):
    #     print 'stock move vals: ',vals
    #     return super(StockMove,self).write(vals)

    @api.multi
    @api.depends('product_uom_qty')
    def _compute_unit_factor(self):
        print '_compute_unit_factor'
        for rec in self:
            original_quantity = rec.raw_material_production_id.product_qty - rec.raw_material_production_id.qty_produced
            if original_quantity > 0:
                print 'original_quantity: ',original_quantity
                print 'rec.product_uom_qty: ',rec.product_uom_qty
                rec.unit_factor = (rec.product_uom_qty / original_quantity)
                print 'rec.unit_factor: ',rec.unit_factor

    @api.multi
    @api.depends('densidad','product_uom_qty')
    def _compute_kg(self):
        for rec in self:
            if rec.densidad and rec.product_uom_qty:
               rec.kilos =  rec.densidad * rec.product_uom_qty

    #@api.depends('product_uom_qty',)
    @api.multi
    @api.depends('product_uom_qty','state')
    def _compute_percent(self):

        for rec in self:
            if rec.state in ('cancel',):
                rec.porcentaje = 0
            else:
                bom_total = rec.get_bom_total()
                if bom_total > 0 and rec.state not in ('cancel'):
                   rec.porcentaje = (rec.product_uom_qty * 100) / bom_total

    @api.multi
    def compute_bom_data(self):
        print 'compute_bom_data'
        for rec in self:
            if rec.bom_line_id and not rec.new_bom_line:
                print 'rec.bom_line_id.obligatorio: ',rec.bom_line_id.obligatorio
                print 'rec.bom_line_id.formula_p: ',rec.bom_line_id.formula_p
                rec.obligatorio = rec.bom_line_id.obligatorio
                rec.formula_p = rec.bom_line_id.formula_p
        return

    #@api.one
    def get_bom_total(self):
        """
        OBTIENE EL TOTAL DE MATERIALES DE LA LISTA DE MATERIALES ORIGINAL
        """
        bom_total = 0
        if self.raw_material_production_id and self.raw_material_production_id.bom_id \
         and self.raw_material_production_id.bom_id.bom_line_ids:
            bom_total = sum([((line.product_qty/self.raw_material_production_id.bom_id.product_qty)\
                *self.raw_material_production_id.product_qty )\
             for line in self.raw_material_production_id.bom_id.bom_line_ids])
        return bom_total


    quantity_done_store = fields.Float('Quantity', digits=dp.get_precision('Product Unit of Measure'))
    unit_factor = fields.Float('Unit Factor',compute='_compute_unit_factor',digits=dp.get_precision('Product Unit of Measure'))

    #obligatorio = fields.Boolean('Obligatorio', compute='compute_bom_data', store=True)
    #formula_p = fields.Float('% de Formula',digits=dp.get_precision('Product Unit of Measure'), compute='compute_bom_data', store=True)
    obligatorio = fields.Boolean('Obligatorio', compute='compute_bom_data')
    formula_p = fields.Float('% de Formula',digits=dp.get_precision('Product Unit of Measure'), compute='compute_bom_data')

    densidad = fields.Float('Densidad',digits=dp.get_precision('Product Unit of Measure'))
    kilos = fields.Float('Kilos', compute='_compute_kg', store=True, digits=dp.get_precision('Product Unit of Measure'))
    #produccion_p = fields.Boolean('%% de Produccion')
    #porcentaje = fields.Float('% de Produccion', compute='_compute_percent', store=True)
    porcentaje = fields.Float('% de Produccion',compute='_compute_percent',\
        digits=dp.get_precision('Product Unit of Measure'), store=True)


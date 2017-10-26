# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError

#PARA FECHAS
from datetime import datetime, timedelta

#OTROS
import openerp.addons.decimal_precision as dp

##### SOLUCIONA CUALQUIER ERROR DE ENCODING (CARACTERES ESPECIALES)
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

class StockMoveAdd(models.TransientModel):
    _inherit = "stock.move.add"

    routing_id = fields.Many2one('mrp.routing', 'Routing',required=True)
    operation_id = fields.Many2one('mrp.routing.workcenter', 'Consumido en operacion', required=True)
    mo_id = fields.Many2one('mrp.production', 'Manufacturing Order', required=True)


    @api.model
    def default_get(self, fields):
        #print fields
        res = super(StockMoveAdd, self).default_get(fields)
        if 'mo_id' in fields and not res.get('mo_id') and self._context.get('active_model') == 'mrp.production' and self._context.get('active_id'):
            res['mo_id'] = self._context['active_id']
            if 'routing_id' in fields and not res.get('routing_id') and self._context.get('active_model') == 'mrp.production' and self._context.get('active_id'):
                routing_id = self.env['mrp.production'].browse(res['mo_id']).routing_id.id
                res['routing_id'] = routing_id
        return res


    def add_production_consume_line(self, new_move, production):
        #print 'add_production_consume_line'
        move_id = super(StockMoveAdd,self).add_production_consume_line(new_move,production)
        #print 'move_id: ',move_id

        #SE AGREGA OPERACION
        #print 'self.operation_id.id: ',self.operation_id.id
        move_id.operation_id = self.operation_id.id
        #print 'move_id.operation_id: ',move_id.operation_id
        #CALCULA PORCENTAJE DEL TOTAL PARA NUEVO MATERIAL A CONSUMIR
        if move_id.state in ('cancel',):
            move_id.porcentaje = 0
        else:
            bom_total = move_id.get_bom_total()
            if bom_total > 0 and move_id.state not in ('cancel'):
               move_id.porcentaje = (move_id.product_uom_qty * 100) / bom_total

        #CALCULA UNIT FACTOR
        original_quantity = move_id.raw_material_production_id.product_qty - move_id.raw_material_production_id.qty_produced
        if original_quantity > 0:
            move_id.unit_factor = (move_id.product_uom_qty / original_quantity)
        return move_id


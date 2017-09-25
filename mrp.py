# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from openerp import api
from openerp.exceptions import UserError, RedirectWarning, ValidationError

from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp

_ALLOWED_DIFFERENCE = .0000001 #MARGEN PERMITIDO DE DIFERENCIA ENTRE 2 NUMEROS

# class MrpWorkorder(models.Model):
#     _inherit = 'mrp.workorder'

#     @api.multi
#     def record_production(self):
#         self.ensure_one()
#         if self.qty_producing <= 0:
#             raise UserError(_('Please set the quantity you produced in the Current Qty field. It can not be 0!'))

#         if (self.production_id.product_id.tracking != 'none') and not self.final_lot_id:
#             raise UserError(_('You should provide a lot for the final product'))

#         # Update quantities done on each raw material line
#         raw_moves = self.move_raw_ids.filtered(lambda x: (x.has_tracking == 'none') and (x.state not in ('done', 'cancel')) and x.bom_line_id)
#         for move in raw_moves:
#             if move.unit_factor:
#                 #rounding = move.product_uom.rounding
#                 #move.quantity_done += float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)
#                 move.quantity_done += (self.qty_producing * move.unit_factor)
#                 print 'move.product_id.name: ',move.product_id.name
#                 print 'move.quantity_done: ',move.quantity_done

#         # Transfer quantities from temporary to final move lots or make them final
#         for move_lot in self.active_move_lot_ids:
#             # Check if move_lot already exists
#             if move_lot.quantity_done <= 0:  # rounding...
#                 move_lot.sudo().unlink()
#                 continue
#             if not move_lot.lot_id:
#                 raise UserError(_('You should provide a lot for a component'))
#             # Search other move_lot where it could be added:
#             lots = self.move_lot_ids.filtered(lambda x: (x.lot_id.id == move_lot.lot_id.id) and (not x.lot_produced_id) and (not x.done_move))
#             if lots:
#                 lots[0].quantity_done += move_lot.quantity_done
#                 lots[0].lot_produced_id = self.final_lot_id.id
#                 move_lot.sudo().unlink()
#             else:
#                 move_lot.lot_produced_id = self.final_lot_id.id
#                 move_lot.done_wo = True

#         # One a piece is produced, you can launch the next work order
#         if self.next_work_order_id.state == 'pending':
#             self.next_work_order_id.state = 'ready'
#         if self.next_work_order_id and self.final_lot_id and not self.next_work_order_id.final_lot_id:
#             self.next_work_order_id.final_lot_id = self.final_lot_id.id

#         self.move_lot_ids.filtered(
#             lambda move_lot: not move_lot.done_move and not move_lot.lot_produced_id and move_lot.quantity_done > 0
#         ).write({
#             'lot_produced_id': self.final_lot_id.id,
#             'lot_produced_qty': self.qty_producing
#         })

#         # If last work order, then post lots used
#         # TODO: should be same as checking if for every workorder something has been done?
#         if not self.next_work_order_id:
#             production_move = self.production_id.move_finished_ids.filtered(lambda x: (x.product_id.id == self.production_id.product_id.id) and (x.state not in ('done', 'cancel')))
#             if production_move.product_id.tracking != 'none':
#                 move_lot = production_move.move_lot_ids.filtered(lambda x: x.lot_id.id == self.final_lot_id.id)
#                 if move_lot:
#                     move_lot.quantity += self.qty_producing
#                 else:
#                     move_lot.create({'move_id': production_move.id,
#                                      'lot_id': self.final_lot_id.id,
#                                      'quantity': self.qty_producing,
#                                      'quantity_done': self.qty_producing,
#                                      'workorder_id': self.id,
#                                      })
#             else:
#                 production_move.quantity_done += self.qty_producing  # TODO: UoM conversion?
#         # Update workorder quantity produced
#         self.qty_produced += self.qty_producing

#         # Set a qty producing
#         if self.qty_produced >= self.production_id.product_qty:
#             self.qty_producing = 0
#         elif self.production_id.product_id.tracking == 'serial':
#             self.qty_producing = 1.0
#             self._generate_lot_ids()
#         else:
#             self.qty_producing = self.production_id.product_qty - self.qty_produced
#             self._generate_lot_ids()

#         self.final_lot_id = False
#         if self.qty_produced >= self.production_id.product_qty:
#             self.button_finish()
#         return True


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    #bom_mod = fields.Boolean('bom_mod',related='product_id.categ_id.mrp_bom_modification')

    def check_move_line(self,move):
        if move.obligatorio:

            if move.bom_line_id and not move.new_bom_line and move.raw_material_production_id:
                bom_product_qty = move.bom_line_id.bom_id.product_qty
                bom_line_product_qty = move.bom_line_id.product_qty
                production_qty = move.raw_material_production_id.product_qty
                move_product_qty = move.product_uom_qty

                bom_qty = 0
                move_qty_percentage = 0

                if production_qty > 0: bom_qty = (bom_line_product_qty / bom_product_qty) * production_qty
                if bom_qty > 0: move_qty_percentage = (move_product_qty * 100 ) / bom_qty

                differencia = move_qty_percentage - move.formula_p
                if abs(differencia) > _ALLOWED_DIFFERENCE:
                    #if move_qty_percentage < move.formula_p:
                    if differencia < 0:
                        min_qty = (move.formula_p * bom_qty) / 100
                        move.product_uom_qty = min_qty
                        raise ValidationError(_('La cantidad minima permitida para '+move.product_id.name+\
                            ' es '+str(min_qty)))
                    #elif move_qty_percentage > 100:
                    elif differencia > 0:
                        max_qty = bom_qty
                        move.product_uom_qty = max_qty
                        raise ValidationError(_('La cantidad maxima permitida para '+move.product_id.name+\
                            ' es '+str(max_qty)))
        return


    @api.multi
    def check_percentage(self):
        """
        REVISA QUE SE CUMPLA LA CONDICION DE 100% DE LISTA DE MATERIALES
        """
        for production in self:
            if production.product_id.categ_id and production.product_id.categ_id.mrp_bom_modification:
                #SE OBTIENE EL 100% DE LA LISTA DE MATERIALES ORIGINAL (SUMA DEL TOTAL DE CANTIDADES)
                bom_total = 0
                if production.bom_id and production.bom_id.bom_line_ids:
                    bom_total = sum([( (line.product_qty/production.bom_id.product_qty)*production.product_qty )\
                     for line in production.bom_id.bom_line_ids])
                    #print 'BOM 100% = ',bom_total

                #SE OBTIENE EL 100% DE LOS MATERIALES A CONSUMIR
                production_total = 0
                if production.move_raw_ids:
                    for move in production.move_raw_ids:

                        self.check_move_line(move)

                    production_total = sum([move.product_uom_qty for move in production.move_raw_ids\
                     if move.state not in ('cancel')])
                    #print 'PRODUCTION 100% = ',production_total

                differencia = production_total - bom_total
                if abs(differencia) > _ALLOWED_DIFFERENCE:
                    #if production_total > bom_total:
                    if differencia > 0:
                        raise ValidationError(_('Esta sobrepasando el 100% de cantidad de material de produccion'\
                            +'\nTotal Lista de materiales = '+str(bom_total)+\
                            '\nTotal Materiales a consumir = '+str(production_total)\
                            +'\nDiferencia: '+str(abs(differencia))))
                    #elif production_total < bom_total:
                    elif differencia < 0:
                        raise ValidationError(_('No alcanza el 100% de cantidad de produccion necesario'\
                            +'\nTotal Lista de materiales = '+str(bom_total)+\
                            '\nTotal Materiales a consumir = '+str(production_total)\
                            +'\nDiferencia: '+str(abs(differencia))))


    #HEREDA METODOS EXISTENTES Y AGREGA CHECKEO DE PORCENTAGES
    @api.multi
    def button_plan(self):
        self.check_percentage()
        super(MrpProduction,self).button_plan()

    @api.multi
    def action_assign(self):
        self.check_percentage()
        super(MrpProduction,self).action_assign()


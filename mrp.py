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

#         print 'self.final_lot_id: ',self.final_lot_id
#         # Update quantities done on each raw material line
#         raw_moves = self.move_raw_ids.filtered(lambda x: (x.has_tracking == 'none') and (x.state not in ('done', 'cancel')) and x.bom_line_id)
#         for move in raw_moves:
#             if move.unit_factor:
#                 rounding = move.product_uom.rounding
#                 move.quantity_done += float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)
#                 print 'self.qty_producing: ',self.qty_producing
#                 print 'move.unit_factor: ',move.unit_factor
#                 print 'move.product_id.name: ',move.product_id.name
#                 print 'move.quantity_done: ',move.quantity_done
#                 print '-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*'

#         # Transfer quantities from temporary to final move lots or make them final
#         for move_lot in self.active_move_lot_ids:
#             # Check if move_lot already exists
#             print 'move_lot.lot_id.name: ',move_lot.lot_id.name
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
#             print 'production_move.product_id.name: ',production_move.product_id.name
#             if production_move.product_id.tracking != 'none':
#                 move_lot = production_move.move_lot_ids.filtered(lambda x: x.lot_id.id == self.final_lot_id.id)
#                 print 'move_lot: ',move_lot
#                 if move_lot:
#                     print 'move_lot.id: ',move_lot.id
#                     print 'move_lot.quantity: ',move_lot.quantity
#                     move_lot.quantity += self.qty_producing
#                     print 'move_lot.quantity: ',move_lot.quantity
#                 else:
#                     print 'else111'
#                     move_lot.create({'move_id': production_move.id,
#                                      'lot_id': self.final_lot_id.id,
#                                      'quantity': self.qty_producing,
#                                      'quantity_done': self.qty_producing,
#                                      'workorder_id': self.id,
#                                      })
#             else:
#                 print 'else222'
#                 production_move.quantity_done += self.qty_producing  # TODO: UoM conversion?
#                 print 'production_move.product_id.name: ',production_move.product_id.nam
#         # Update workorder quantity produced
#         print 'self.qty_produced: ',self.qty_produced
#         self.qty_produced += self.qty_producing
#         print 'self.qty_produced: ',self.qty_produced

#         # Set a qty producing
#         if self.qty_produced >= self.production_id.product_qty:
#             print '11111'
#             self.qty_producing = 0
#         elif self.production_id.product_id.tracking == 'serial':
#             print '222'
#             self.qty_producing = 1.0
#             self._generate_lot_ids()
#         else:
#             print '3333'
#             self.qty_producing = self.production_id.product_qty - self.qty_produced
#             self._generate_lot_ids()

#         self.final_lot_id = False
#         if self.qty_produced >= self.production_id.product_qty:
#             print '4444'
#             self.button_finish()
#         return True



#     @api.onchange('qty_producing')
#     def _onchange_qty_producing(self):
#         print '_onchange_qty_producing'
#         """ Update stock.move.lot records, according to the new qty currently
#         produced. """
#         moves = self.move_raw_ids.filtered(lambda move: move.state not in ('done', 'cancel') and move.product_id.tracking != 'none' and move.product_id.id != self.production_id.product_id.id)
#         for move in moves:
#             print 'move.name: ',move.name
#             print 'move.id: ',move.id
#             move_lots = self.active_move_lot_ids.filtered(lambda move_lot: move_lot.move_id == move)
#             if not move_lots:
#                 continue
#             new_qty = move.unit_factor * self.qty_producing
#             print 'move.unit_factor: ',move.unit_factor
#             print 'self.qty_producing: ',self.qty_producing
#             print 'new_qty: ',new_qty
#             if move.product_id.tracking == 'lot':
#                 print 'xxxxx'
#                 move_lots[0].quantity = new_qty
#                 move_lots[0].quantity_done = new_qty
#             elif move.product_id.tracking == 'serial':
#                 print '00000'
#                 # Create extra pseudo record
#                 qty_todo = new_qty - sum(move_lots.mapped('quantity'))


#                 for lot in move_lots:
#                     print 'lot.id: ',lot.id
#                     print 'lot.product_id: ',lot.product_id.name
#                     print 'lot.quantity: ',lot.quantity

#                 if float_compare(qty_todo, 0.0, precision_rounding=move.product_uom.rounding) > 0:
#                     print '1111'
#                     while float_compare(qty_todo, 0.0, precision_rounding=move.product_uom.rounding) > 0:
#                         print '2222'
#                         self.active_move_lot_ids += self.env['stock.move.lots'].new({
#                             'move_id': move.id,
#                             'product_id': move.product_id.id,
#                             'lot_id': False,
#                             'quantity': min(1.0, qty_todo),
#                             'quantity_done': min(1.0, qty_todo),
#                             'workorder_id': self.id,
#                             'done_wo': False
#                         })
#                         qty_todo -= 1
#                 elif float_compare(qty_todo, 0.0, precision_rounding=move.product_uom.rounding) < 0:
#                     print '3333'
#                     qty_todo = abs(qty_todo)
#                     for move_lot in move_lots:
#                         print '4444'
#                         if qty_todo <= 0:
#                             break
#                         if not move_lot.lot_id and qty_todo >= move_lot.quantity:
#                             qty_todo = qty_todo - move_lot.quantity
#                             self.active_move_lot_ids -= move_lot  # Difference operator
#                         else:
#                             move_lot.quantity = move_lot.quantity - qty_todo
#                             if move_lot.quantity_done - qty_todo > 0:
#                                 move_lot.quantity_done = move_lot.quantity_done - qty_todo
#                             else:
#                                 move_lot.quantity_done = 0
#                             qty_todo = 0

#     def _generate_lot_ids(self):
#         """ Generate stock move lots """
#         self.ensure_one()
#         MoveLot = self.env['stock.move.lots']
#         tracked_moves = self.move_raw_ids.filtered(
#             lambda move: move.state not in ('done', 'cancel') and move.product_id.tracking != 'none' and move.product_id != self.production_id.product_id)
#         for move in tracked_moves:
#             print '--------------------'
#             print 'move-product_id.name: ',move.product_id.name
#             print 'move.unit_factor: ',move.unit_factor
#             print 'self.qty_producing: ',self.qty_producing
#             qty = move.unit_factor * self.qty_producing
#             print 'qty: ',qty
#             if move.product_id.tracking == 'serial':
#                 while float_compare(qty, 0.0, precision_rounding=move.product_uom.rounding) > 0:
#                     MoveLot.create({
#                         'move_id': move.id,
#                         'quantity': min(1, qty),
#                         'quantity_done': min(1, qty),
#                         'production_id': self.production_id.id,
#                         'workorder_id': self.id,
#                         'product_id': move.product_id.id,
#                         'done_wo': False,
#                     })
#                     qty -= 1
#             else:
#                 MoveLot.create({
#                     'move_id': move.id,
#                     'quantity': qty,
#                     'quantity_done': qty,
#                     'product_id': move.product_id.id,
#                     'production_id': self.production_id.id,
#                     'workorder_id': self.id,
#                     'done_wo': False,
#                     })


# class MrpBomLine(models.Model):
#     _inherit = 'mrp.bom.line'

#     obligatorio = fields.Boolean('Obligatorio')
#     formula_p = fields.Float('% de Formula',digits=dp.get_precision('Product Unit of Measure'))


class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    # @api.multi
    # def button_mark_done(self):
    #     print 'button_mark_done'
    #     self.ensure_one()
    #     for wo in self.workorder_ids:
    #         if wo.time_ids.filtered(lambda x: (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
    #             raise UserError(_('Work order %s is still running') % wo.name)
    #     print '111111'
    #     self.post_inventory()
    #     print '22222'
    #     moves_to_cancel = (self.move_raw_ids | self.move_finished_ids).filtered(lambda x: x.state not in ('done', 'cancel'))
    #     moves_to_cancel.action_cancel()
    #     print '33333'
    #     self.write({'state': 'done', 'date_finished': fields.Datetime.now()})
    #     print '4444'
    #     self.env["procurement.order"].search([('production_id', 'in', self.ids)]).check()
    #     print '5555'
    #     return self.write({'state': 'done'})



    #bom_mod = fields.Boolean('bom_mod',related='product_id.categ_id.mrp_bom_modification')
    move_raw_ids = fields.One2many(
    'stock.move', 'raw_material_production_id', 'Raw Materials', oldname='move_lines',
    copy=False, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, 
    domain=[('scrapped', '=', False),('state', '!=', 'cancel')])

    @api.multi
    def _generate_moves(self):
        print '_generate_moves'
        res = super(MrpProduction,self)._generate_moves()
        for production in self:
            if production.move_raw_ids:
                for move in production.move_raw_ids:

                    #NEW###############
                    #CONTENDRA VALOR ORIGINAL A CONSUMIR (INFORMATIVO)
                    move.product_uom_qty_original = move.product_uom_qty 
                    ####################

                    #print 'move.product_id.name: ',move.product_id.name
                    if move.bom_line_id:
                        #print 'move.bom_line_id.bom_p: ',move.bom_line_id.bom_p
                        move.real_p = move.bom_line_id.bom_p

        return res

        # for production in self:
        #     production._generate_finished_moves()
        #     factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
        #     boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
        #     production._generate_raw_moves(lines)
        #     # Check for all draft moves whether they are mto or not
        #     production._adjust_procure_method()
        #     production.move_raw_ids.action_confirm()
        # return True


    # @api.multi
    # def _generate_moves(self):
    #     for production in self:
    #         production._generate_finished_moves()
    #         factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
    #         boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
    #         production._generate_raw_moves(lines)
    #         # Check for all draft moves whether they are mto or not
    #         production._adjust_procure_method()
    #         production.move_raw_ids.action_confirm()
    #     return True


    # def check_move_line(self,move):
    #     print 'check_move_line'
    #     if move.obligatorio:

    #         if move.bom_line_id and not move.new_bom_line and move.raw_material_production_id:
    #             bom_product_qty = move.bom_line_id.bom_id.product_qty
    #             bom_line_product_qty = move.bom_line_id.product_qty
    #             production_qty = move.raw_material_production_id.product_qty
    #             move_product_qty = move.product_uom_qty

    #             bom_qty = 0
    #             move_qty_percentage = 0

    #             if production_qty > 0:
    #                 bom_qty = (bom_line_product_qty / bom_product_qty) * production_qty
    #             if bom_qty > 0: 
    #                 move_qty_percentage = (move_product_qty * 100 ) / bom_qty

    #             print '-----------'
    #             print 'move.product_id.name: ',move.product_id.name
    #             print 'move_qty_percentage: ',move_qty_percentage
    #             print 'move.formula_p: ',move.formula_p
    #             differencia = move_qty_percentage - move.formula_p
    #             if abs(differencia) > _ALLOWED_DIFFERENCE:
    #                 #if move_qty_percentage < move.formula_p:
    #                 if differencia < 0:
    #                     min_qty = ((move.formula_p * bom_qty) / 100) or 0.0
    #                     move.product_uom_qty = min_qty


    #                     min_qty = str('{0:f}'.format(min_qty))
    #                     #print 'min_qty: ',min_qty
                        
    #                     raise ValidationError(_('La cantidad minima permitida para '+move.product_id.name+\
    #                         ' es '+str(min_qty)))
    #                 #elif move_qty_percentage > 100:
    #                 # elif differencia > 0:
    #                 #     max_qty = bom_qty
    #                 #     move.product_uom_qty = max_qty
    #                 #     raise ValidationError(_('La cantidad maxima permitida para '+move.product_id.name+\
    #                 #         ' es '+str(max_qty)))
    #     return

    def get_min_qty(self,move,production_qty):
        """
        OBTIENE EL % CORRESPONDIENTE A LA CANTIDAD ESTABLECIDA EN LA LISTA
        DE MATERIAL
        """
        print 'get_bom_line_percent'
        min_qty = 0
        bom_qty = move.bom_line_id.product_qty
        formula_p = move.formula_p
        qty = move.product_uom_qty
        min_qty = ((bom_qty * formula_p)/100)*production_qty
        print 'min_qty: ',min_qty
        return min_qty


    def check_move_line(self,move):
        print 'check_move_line'
        if move.obligatorio:
            if move.bom_line_id and not move.new_bom_line and move.raw_material_production_id:
                production_qty = move.raw_material_production_id.product_qty #100%
                product_uom_qty = move.product_uom_qty #?
                #min_qty = (move.formula_p * production_qty) / 100
                line_percent = 0

                min_qty = self.get_min_qty(move,production_qty)

                print 'production_qty: ',production_qty
                print 'move.product_id.name: ',move.product_id.name
                print 'product_uom_qty: ',product_uom_qty
                print '-------------------'

                if product_uom_qty < min_qty:
                    raise ValidationError(_('La cantidad minima permitida para '+move.product_id.name+\
                        ' es '+str(min_qty)))

                # if production_qty > 0:
                #     line_percent = (product_uom_qty * 100) / production_qty

                # if line_percent < move.formula_p:
                #     raise ValidationError(_('La cantidad minima permitida para '+move.product_id.name+\
                #         ' es '+str(min_qty)))
        return

    @api.multi
    def check_percentage(self):
        """
        REVISA QUE SE CUMPLA LA CONDICION DE 100% DE LISTA DE MATERIALES
        """
        print 'check_percentage'
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
                print 'differencia: ',differencia
                if abs(differencia) > _ALLOWED_DIFFERENCE:
                    #if production_total > bom_total:
                    if differencia < 0:
                        str_differencia = str('{0:f}'.format(differencia))
                        #print 'str_differencia: ',str_differencia
                        raise ValidationError(_('No alcanza el 100% de cantidad de produccion necesario'\
                            +'\nTotal Lista de materiales = '+str(bom_total)+\
                            '\nTotal Materiales a consumir = '+str(production_total)\
                            +'\nDiferencia: '+str(str_differencia)))
                    # if differencia > 0:
                    #     raise ValidationError(_('Esta sobrepasando el 100% de cantidad de material de produccion'\
                    #         +'\nTotal Lista de materiales = '+str(bom_total)+\
                    #         '\nTotal Materiales a consumir = '+str(production_total)\
                    #         +'\nDiferencia: '+str(abs(differencia))))
                    # #elif production_total < bom_total:
                    # elif differencia < 0:
                    #     raise ValidationError(_('No alcanza el 100% de cantidad de produccion necesario'\
                    #         +'\nTotal Lista de materiales = '+str(bom_total)+\
                    #         '\nTotal Materiales a consumir = '+str(production_total)\
                    #         +'\nDiferencia: '+str(abs(differencia))))


    #HEREDA METODOS EXISTENTES Y AGREGA CHECKEO DE PORCENTAGES
    @api.multi
    def button_plan(self):
        if self.state not in ('done','cancel','progress'):
            #print self.state
            self.check_percentage()
        super(MrpProduction,self).button_plan()

    @api.multi
    def action_assign(self):
        if self.state not in ('done','cancel','progress'):
            #print self.state
            self.check_percentage()
        super(MrpProduction,self).action_assign()


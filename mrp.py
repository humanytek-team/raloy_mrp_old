# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from openerp import api
from openerp.exceptions import UserError, RedirectWarning, ValidationError

from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp

_ALLOWED_DIFFERENCE = .0000001 #MARGEN PERMITIDO DE DIFERENCIA ENTRE 2 NUMEROS

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    obligatorio = fields.Boolean('Obligatorio')
    formula_p = fields.Float('% de Formula',digits=dp.get_precision('Product Unit of Measure'))


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
                    # elif differencia > 0:
                    #     max_qty = bom_qty
                    #     move.product_uom_qty = max_qty
                    #     raise ValidationError(_('La cantidad maxima permitida para '+move.product_id.name+\
                    #         ' es '+str(max_qty)))
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


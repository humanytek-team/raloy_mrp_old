# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from openerp import api

class ProductCategory(models.Model):
    _inherit = 'product.category'

    mrp_bom_modification = fields.Boolean('Modificacion de lista de materiales',\
    	help='Si la casilla es marcada\nperimite la modificacion de insumos en ordenes de produccion')
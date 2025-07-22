from odoo import models, api
from odoo.osv import expression

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not name:
            return super().name_search(name, args, operator, limit)

        domain = args or []
        products = self.browse()

        # 1. Coincidencia exacta con default_code
        products = self.search_fetch(expression.AND([domain, [('default_code', '=', name)]]), ['display_name'], limit=limit)
        
        # 2. Coincidencia exacta con name
        if not products:
            products = self.search_fetch(expression.AND([domain, [('name', '=', name)]]), ['display_name'], limit=limit)
        
        # 3. Búsqueda parcial si no hay coincidencia exacta
        if not products:
            products = self.search_fetch(expression.AND([domain, [('default_code', operator, name)]]), ['display_name'], limit=limit)
            limit_rest = limit and limit - len(products)
            if limit_rest is None or limit_rest > 0:
                products |= self.search_fetch(expression.AND([
                    domain,
                    [('id', 'not in', products.ids)],
                    [('name', operator, name)]
                ]), ['display_name'], limit=limit_rest)

        return [(product.id, product.display_name) for product in products.sudo()]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not name:
            return super().name_search(name, args, operator, limit)

        domain = args or []
        products = self.browse()

        # 1. Coincidencia exacta con default_code
        products = self.search_fetch(expression.AND([domain, [('default_code', '=', name)]]), ['display_name'], limit=limit)
        
        # 2. Coincidencia exacta con name
        if not products:
            products = self.search_fetch(expression.AND([domain, [('name', '=', name)]]), ['display_name'], limit=limit)
        
        # 3. Búsqueda parcial si no hay coincidencia exacta
        if not products:
            products = self.search_fetch(expression.AND([domain, [('default_code', operator, name)]]), ['display_name'], limit=limit)
            limit_rest = limit and limit - len(products)
            if limit_rest is None or limit_rest > 0:
                products |= self.search_fetch(expression.AND([
                    domain,
                    [('id', 'not in', products.ids)],
                    [('name', operator, name)]
                ]), ['display_name'], limit=limit_rest)

        return [(product.id, product.display_name) for product in products.sudo()]
from odoo import models, fields, api

class StockQuant(models.Model):
    _inherit = 'product.product'

    qty_available = fields.Float(
        'Количество в Наличии', compute='_compute_quantities', search='_search_qty_available',
        digits='Product Unit of Measure', compute_sudo=False, store=True,
        help="Текущее количество товаров на складе.")

    minimum_stock_config = fields.Float(
        store=True
    )


    def _check_low_stock(self):
        # Получаем минимальный запас из параметров системы
        minimum_stock = float(
            self.env['ir.config_parameter'].sudo().get_param('stock_attachment.minimum_stock', default=0.0))

        # Проверяем, что параметр настроен корректно
        if not minimum_stock or not isinstance(minimum_stock, float):
            raise ValueError("Параметр 'stock_attachment.minimum_stock' не настроен или имеет некорректное значение.")

        # Находим продукты с низким запасом
        low_stock_products = self.search([
            ('qty_available', '<', minimum_stock)
        ])

        # Получаем пользователей с группой base.group_user
        users = self.env['res.users'].search([('groups_id', '=', self.env.ref('stock_attachment.group_wood_receiver').id)])
        if not users:
            raise ValueError("Нет пользователей с группой base.group_user.")

        for product in low_stock_products:
            message_body = (
                f"Запасы продукта '{product.name}' на исходе! Текущий запас: {product.qty_available}, "
                f"минимальный запас: {minimum_stock}."
            )

            for user in users:
                print(f"User: {user.name}, Partner ID: {user.partner_id.id}")

                # Формируем уведомление
                notification = {
                    'type': 'warning',
                    'title': "Низкий запас!",
                    'message': message_body,
                    'sticky': True,
                }

                # Отправляем уведомление через bus.bus
                self.env['bus.bus']._sendone(user.partner_id, 'simple_notification', notification)

    @api.model
    def run_low_stock_check(self):
        products = self.search([])
        products._check_low_stock()

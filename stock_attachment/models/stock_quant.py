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

    # def _check_low_stock(self):
    #     minimum_stock = float(
    #         self.env['ir.config_parameter'].sudo().get_param('stock_attachment.minimum_stock', default=0.0))
    #     if not minimum_stock or not isinstance(minimum_stock, float):
    #         raise ValueError("Параметр 'stock_attachment.minimum_stock' не настроен или имеет некорректное значение.")
    #
    #     low_stock_products = self.search([
    #         ('qty_available', '<', minimum_stock)
    #     ])
    #
    #     system_partner_id = self.env.ref('base.partner_root')
    #
    #     stock_managers = self.env.ref('base.group_user').users
    #     if not stock_managers:
    #         raise ValueError("Нет пользователей с правами менеджера склада.")
    #
    #
    #
    #
    #     for product in low_stock_products:
    #         message_body = (
    #             f"Запасы продукта '{product.name}' на исходе! Текущий запас: {product.qty_available}, "
    #             f"минимальный запас: {minimum_stock}."
    #         )
    #         for manager in stock_managers:
    #             print(f"Manager: {manager.name}, Partner ID: {manager.partner_id.id}")
    #             manager.partner_id.sudo().message_post(
    #                 body=message_body,
    #                 author_id=self.env.user.partner_id.id,
    #                 message_type='notification',
    #                 subtype_xmlid='mail.mt_comment',
    #                 partner_ids=[manager.partner_id.id],# Используем 'mail.mt_comment' для видимости
    #             )

    from odoo.addons.bus.models.bus import dispatch

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
                    'type': 'simple_notification',
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

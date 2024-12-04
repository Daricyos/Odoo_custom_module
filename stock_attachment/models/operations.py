from itertools import product

from odoo import api, fields, models
import os
from odoo.exceptions import ValidationError


# //////////  Chop logs //////
class ChopLogs(models.Model):
    _name = "chop.logs"
    _description = "Chopping Logs"

    responsible = fields.Many2one('res.users', string='Відповідальний', default=lambda self: self.env.user)
    partner_id = fields.Many2one(
        'stock.warehouse',  # Модель складів в Odoo
        string='Отримати з',  # Назва поля
        required=True,  # Опційно: зробити обов'язковим
        default=lambda self: self.env['stock.warehouse'].search([('name', 'in',
              ['Прийом сировини'])], limit=1)  # Опційно: default перший склад
    )
    warehouse_to_id = fields.Many2one(
        'stock.warehouse',  # Модель складів в Odoo
        string='Відправити в',  # Назва поля
        required=True,  # Опційно: зробити обов'язковим
        default=lambda self: self.env['stock.warehouse'].search([('name', 'in',
              ['Біржа-1'])], limit=1)  # Опційно: default перший склад
    )
    invoice_number = fields.Integer('Номер накладної', required=True)

    move_ids_without_package = fields.One2many(
        'chop.logs.line', 'receiving_wood_id', string="Stock move")
    document_ids = fields.Many2many('ir.attachment', string='Завантажити документи')

    @api.model
    def default_get(self, fields_list):
        res = super(ChopLogs, self).default_get(fields_list)
        products = self.env['product.product'].search(
            [('name', 'in', ['Бук пропарений сорт A', 'Бук пропарений сорт B', 'Бук пропарений сорт C', 'Бук пропарений сорт D'])])
        move_lines = []
        for product in products:
            move_lines.append((0, 0, {'product_id': product.id, 'quantity': 0.0}))
        res['move_ids_without_package'] = move_lines
        return res

    # def action_create_operations(self):
    #     stock_picking_obj = self.env['stock.picking']
    #     stock_move_obj = self.env['stock.move']
    #
    #     for record in self:
    #
    #         valid_moves = record.move_ids_without_package.filtered(lambda line: line.quantity > 0)
    #         print(valid_moves)
    #
    #         if not valid_moves:
    #             raise ValidationError("Не знайдено продуктів з кількістю більше 0.")
    #
    #         picking_type = self.env['stock.picking.type'].search([('name', '=', 'Надходження')],
    #                                                              limit=1)
    #
    #         location_dest = self.env['stock.location'].search(
    #             [('name', '=', 'Запаси'), ('location_id', '=', 'СИРОВ')], limit=1)
    #
    #         if not location_dest:
    #             raise ValidationError("Не знайдено локації 'СИРОВ/Запаси'.")
    #
    #         location_dest_stock_move = self.env['stock.location'].search(
    #             [('name', '=', 'Vendors'), ('location_id', '=', 'Partners')], limit=1)
    #
    #         if not location_dest_stock_move:
    #             raise ValidationError("Не знайдено локації 'Vendors/Partners'.")
    #
    #         picking_vals = {
    #             'partner_id': record.partner_id.id,
    #             'picking_type_id': picking_type.id,  # Замените на ваш picking_type_id
    #             'origin': record.invoice_number,
    #             'location_dest_id': location_dest.id,
    #             'document_ids': [(6, 0, record.document_ids.ids)],
    #         }
    #         picking = stock_picking_obj.create(picking_vals)
    #
    #         for move_line in valid_moves:
    #             print(move_line.product_id.name)
    #             move_vals = {
    #                 'picking_id': picking.id,
    #                 'product_id': move_line.product_id.id,
    #                 'product_uom_qty': move_line.quantity,
    #                 'quantity': move_line.quantity,
    #                 'name': move_line.product_id.name,
    #                 'product_uom': move_line.product_id.uom_id.id,
    #                 'description_picking': move_line.product_id.name,
    #                 'location_id': location_dest_stock_move.id,
    #                 'location_dest_id': location_dest.id,
    #             }
    #             stock_move_obj.create(move_vals)
    #
    #         picking.button_validate()
    #
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Надходження',  # Имя окна
    #             'res_model': 'stock.picking',
    #             'view_mode': 'form',
    #             'res_id': picking.id,  # Открываем созданную запись
    #             'target': 'current',  # Открывать в текущем окне
    #         }
    #
    #     return True


class ChopLogsLine(models.Model):
    _name = 'chop.logs.line'
    _description = 'Chop Logs Line'

    receiving_wood_id = fields.Many2one(
        'chop.logs', string="Chop logs", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Продукт")
    quantity = fields.Float(string="Кількість")


# ///////////////// Receiving Blocks ////////////
class ReceivingBlocks(models.Model):
    _name = "receiving.blocks"
    _description = "Receiving Blocks"

    responsible = fields.Many2one('res.users', string='Відповідальний', default=lambda self: self.env.user)
    partner_id = fields.Many2one(
        'stock.warehouse',  # Модель складів в Odoo
        string='Отримати з',  # Назва поля
        required=True,  # Опційно: зробити обов'язковим
        default=lambda self: self.env['stock.warehouse'].search([('name', 'in',
              ['Біржа-1'])], limit=1)  # Опційно: default перший склад
    )
    warehouse_to_id = fields.Many2one(
        'stock.warehouse',  # Модель складів в Odoo
        string='Відправити в',  # Назва поля
        required=True,  # Опційно: зробити обов'язковим
        default=lambda self: self.env['stock.warehouse'].search([('name', 'in',
              ['Прийом сировини'])], limit=1)  # Опційно: default перший склад
    )
    invoice_number = fields.Integer('Номер накладної', required=True)
    move_ids_without_package = fields.One2many(
        'receiving.blocks.line', 'receiving_wood_id', string="Stock move")
    document_ids = fields.Many2many('ir.attachment', string='Завантажити документи')

    @api.model
    def default_get(self, fields_list):
        res = super(ReceivingBlocks, self).default_get(fields_list)
        products = self.env['product.product'].search(
            [('name', 'in',
              ['Чурак буковий сорт A', 'Чурак буковий сорт B', 'Чурак буковий сорт C', 'Чурак буковий сорт D'])])
        move_lines = []
        for product in products:
            move_lines.append((0, 0, {'product_id': product.id, 'quantity': 0.0}))
        res['move_ids_without_package'] = move_lines
        return res


class ReceivingBlocksLine(models.Model):
    _name = 'receiving.blocks.line'
    _description = 'Receiving Blocks Line'

    receiving_wood_id = fields.Many2one(
        'receiving.blocks', string="Receiving Blocks", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Продукт")
    quantity = fields.Float(string="Кількість")


# ///////////////// Block Drying ////////////
class BlocksDrying(models.Model):
    _name = "blocks.drying"
    _description = "Block Drying"

    responsible = fields.Many2one('res.users', string='Відповідальний', default=lambda self: self.env.user)
    partner_id = fields.Many2one(
        'stock.warehouse',  # Модель складів в Odoo
        string='Отримати з',  # Назва поля
        required=True,  # Опційно: зробити обов'язковим
        default=lambda self: self.env['stock.warehouse'].search([('name', 'in',
                ['Прийом сировини'])], limit=1) # Опційно: default перший склад
    )
    warehouse_to_id = fields.Many2one(
        'stock.warehouse',  # Модель складів в Odoo
        string='Відправити в',  # Назва поля
        required=True,  # Опційно: зробити обов'язковим
        default=lambda self: self.env['stock.warehouse'].search([('name', 'in',
                ['Біржа-1'])], limit=1) # Опційно: default перший склад
    )

    name = fields.Integer('Номер накладної', required=True)
    move_ids_without_package = fields.One2many(
        'blocks.drying.line', 'receiving_wood_id', string="Stock move")

    document_ids = fields.Many2many('ir.attachment', string='Завантажити документи')

    @api.model
    def default_get(self, fields_list):
        res = super(BlocksDrying, self).default_get(fields_list)
        products = self.env['product.product'].search(
            [('name', 'in',
              ['Чурак буковий сорт A', 'Чурак буковий сорт B', 'Чурак буковий сорт C', 'Чурак буковий сорт D'])])
        move_lines = []
        for product in products:
            move_lines.append((0, 0, {'product_id': product.id, 'quantity': 0.0}))
        res['move_ids_without_package'] = move_lines
        return res

    def action_create_operations(self):
        stock_picking_obj = self.env['mrp.production']

        for record in self:
            valid_moves = record.move_ids_without_package.filtered(lambda line: line.quantity > 0)

            if not valid_moves:
                raise ValidationError("Не знайдено продуктів з кількістю більше 0.")

            # picking_type = self.env['stock.picking.type'].search([('name', '=', 'Виробництво')],
            #                                                      limit=1)

            for obj in valid_moves:
                product_id = self.env['product.product'].search(
                    [('name', '=', f'Сушений {obj.product_id.name}')], limit=1)

                picking_vals = {
                    'product_id': product_id.id,
                    'product_qty': obj.quantity,
                }
                picking = stock_picking_obj.create(picking_vals)

                picking.action_confirm()




class BlocksDryingLine(models.Model):
    _name = 'blocks.drying.line'
    _description = 'Blocks Drying Line'

    receiving_wood_id = fields.Many2one(
        'blocks.drying', string="Block Drying", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Продукт")
    quantity = fields.Float(string="Кількість")


# ///////////////// Receiving Dry Blocks ////////////
class ReceivingDryBlocks(models.Model):
    _name = "receiving.dry.blocks"
    _description = "Receiving Dry Blocks"

    responsible = fields.Many2one('res.users', string='Відповідальний', default=lambda self: self.env.user)
    partner_id = fields.Many2one(
        'stock.warehouse',  # Модель складів в Odoo
        string='Отримати з',  # Назва поля
        required=True,  # Опційно: зробити обов'язковим
        default=lambda self: self.env['stock.warehouse'].search([('name', 'in',
                ['Біржа-1'])], limit=1) # Опційно: default перший склад
    )
    warehouse_to_id = fields.Many2one(
        'stock.warehouse',  # Модель складів в Odoo
        string='Відправити в',  # Назва поля
        required=True,  # Опційно: зробити обов'язковим
        default=lambda self: self.env['stock.warehouse'].search([('name', 'in',
                ['Прийом сировини'])], limit=1)# Опційно: default перший склад
    )
    invoice_number = fields.Integer('Номер накладної', required=True)
    move_ids_without_package = fields.One2many(
        'receiving.dry.blocks.line', 'receiving_wood_id', string="Stock move")
    document_ids = fields.Many2many('ir.attachment', string='Завантажити документи')

    @api.model
    def default_get(self, fields_list):
        res = super(ReceivingDryBlocks, self).default_get(fields_list)
        products = self.env['product.product'].search(
            [('name', 'in',
              ['Чурак буковий сухий сорт A', 'Чурак буковий сухий сорт B', 'Чурак буковий сухий сорт C', 'Чурак буковий сухий сорт D'])])
        move_lines = []
        for product in products:
            move_lines.append((0, 0, {'product_id': product.id, 'quantity': 0.0}))
        res['move_ids_without_package'] = move_lines
        return res

class ReceivingDryBlocksLine(models.Model):
    _name = 'receiving.dry.blocks.line'
    _description = 'Blocks Drying Line'

    receiving_wood_id = fields.Many2one(
        'receiving.dry.blocks', string="Receiving Dry Blocks", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Продукт")
    quantity = fields.Float(string="Кількість")


# ///////////////// Block Peeling ////////////
class BlocksPeeling(models.Model):
    _name = "blocks.peeling"
    _description = "Block Peeling"

    responsible = fields.Many2one('res.users', string='Відповідальний', default=lambda self: self.env.user)
    partner_id = fields.Many2one(
        'stock.warehouse',  # Модель складів в Odoo
        string='Отримати з',  # Назва поля
        required=True,  # Опційно: зробити обов'язковим
        default=lambda self: self.env['stock.warehouse'].search([('name', 'in',
                ['Прийом сировини'])], limit=1) # Опційно: default перший склад
    )
    warehouse_to_id = fields.Many2one(
        'stock.warehouse',
        string='Відправити в',  # Назва поля
        required=True,  # Опційно: зробити обов'язковим
        default=lambda self: self.env['stock.warehouse'].search([('name', 'in',
                 ['Біржа-1'])], limit=1) # Опційно: default перший склад
    )
    invoice_number = fields.Integer('Номер накладної', required=True)
    move_ids_without_package = fields.One2many(
        'blocks.peeling.line', 'receiving_wood_id', string="Stock move")
    document_ids = fields.Many2many('ir.attachment', string='Завантажити документи')

    @api.model
    def default_get(self, fields_list):
        res = super(BlocksPeeling, self).default_get(fields_list)
        products = self.env['product.product'].search(
            [('name', 'in',
              ['Чурак буковий сухий сорт A', 'Чурак буковий сухий сорт B', 'Чурак буковий сухий сорт C',
               'Чурак буковий сухий сорт D'])])
        move_lines = []
        for product in products:
            move_lines.append((0, 0, {'product_id': product.id, 'quantity': 0.0}))
        res['move_ids_without_package'] = move_lines
        return res



class BlocksPeelingLine(models.Model):
    _name = 'blocks.peeling.line'
    _description = 'Blocks Drying Line'

    receiving_wood_id = fields.Many2one(
        'blocks.peeling', string="Block Peeling", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Продукт")
    quantity = fields.Float(string="Кількість")
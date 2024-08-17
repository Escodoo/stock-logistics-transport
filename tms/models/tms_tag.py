# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsTag(models.Model):

    _name = "tms.tag"
    _description = "TMS Tag"

    name = fields.Char(string="Name", required=True, translate=True)
    parent_id = fields.Many2one("tms.tag", string="Parent")
    color = fields.Integer("Color Index", default=10)
    full_name = fields.Char(string="Full Name", compute="_compute_full_name")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=False,
        index=True,
        help="Company related to this tag",
    )

    _sql_constraints = [("name_uniq", "unique (name)", "Tag name already exists!")]

    def _compute_full_name(self):
        for record in self:
            if record.parent_id:
                record.full_name = record.parent_id.name + "/" + record.name
            else:
                record.full_name = record.name

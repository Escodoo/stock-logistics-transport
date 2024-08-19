# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    # TMS Geometry Field
    tms_shape = fields.GeoPoint(
        "TMS Coordinate", compute="_compute_tms_shape", store=True
    )
    tms_stage_custom_color = fields.Char(
        related="tms_stage_id.custom_color", string="TMS Stage Color"
    )

    @api.depends("partner_latitude", "partner_longitude")
    def _compute_tms_shape(self):
        for record in self:
            if record.partner_latitude or record.partner_longitude:
                point = fields.GeoPoint.from_latlon(
                    cr=record.env.cr,
                    latitude=record.partner_latitude,
                    longitude=record.partner_longitude,
                )
                record.tms_shape = point
            else:
                record.tms_shape = False

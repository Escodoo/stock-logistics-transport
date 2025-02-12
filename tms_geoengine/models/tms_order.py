# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class TmsOrder(models.Model):

    _inherit = "tms.order"

    origin_shape = fields.GeoPoint(
        related="origin_location_id.tms_shape", string="Origin Coordinate"
    )

    destination_shape = fields.GeoPoint(
        related="destination_location_id.tms_shape",
        string="Destination Coordinate",
        store=True,
    )

    def geo_localize(self):
        self.mapped("destination_location_id").geo_localize()

    @api.model
    def create(self, vals):
        res = super(TmsOrder, self).create(vals)
        if (
            not res.destination_location_id.partner_latitude
            or not res.destination_location_id.partner_longitude
        ):
            res.geo_localize()
        return res

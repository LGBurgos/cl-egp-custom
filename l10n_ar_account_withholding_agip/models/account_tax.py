from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class AccountTax(models.Model):
    _inherit = "account.tax"

    # pisamos get_partner_alicuot para ignorar el get_agip_data
    def get_partner_alicuot(self, partner, date, line=None):
        self.ensure_one()
        commercial_partner = partner.commercial_partner_id
        company = self.company_id
        alicuot = partner.arba_alicuot_ids.search(
            [
                (
                    "tag_id",
                    "in",
                    self.invoice_repartition_line_ids.mapped("tag_ids").ids,
                ),
                ("company_id", "=", company.id),
                ("partner_id", "=", commercial_partner.id),
                "|",
                ("from_date", "=", False),
                ("from_date", "<=", date),
                "|",
                ("to_date", "=", False),
                ("to_date", ">=", date),
            ],
            limit=1,
        )

        # solo buscamos en padron para estas responsabilidades
        if (
            not alicuot
            and commercial_partner.l10n_ar_afip_responsibility_type_id.code
            in ["1", "1FM", "2", "3", "4", "6", "11", "13"]
        ):
            invoice_tags = self.invoice_repartition_line_ids.mapped("tag_ids")
            padron_file = self.env["res.company.jurisdiction.padron"].search(
                [
                    ("jurisdiction_id", "in", invoice_tags.ids),
                    ("company_id", "=", company.id),
                    "|",
                    ("l10n_ar_padron_from_date", "=", False),
                    ("l10n_ar_padron_from_date", "<=", date),
                    "|",
                    ("l10n_ar_padron_to_date", "=", False),
                    ("l10n_ar_padron_to_date", ">=", date),
                ],
                limit=1,
            )
            from_date = date + relativedelta(day=1)
            to_date = date + relativedelta(day=1, days=-1, months=+1)

            agip_tag = self.env.ref("l10n_ar_ux.tag_tax_jurisdiccion_901")
            arba_tag = self.env.ref("l10n_ar_ux.tag_tax_jurisdiccion_902")
            cdba_tag = self.env.ref("l10n_ar_ux.tag_tax_jurisdiccion_904")
            if padron_file:
                nro, alicuot_ret, alicuot_per = padron_file._get_aliquit(
                    commercial_partner
                )
                return partner.arba_alicuot_ids.sudo().create(
                    {
                        "numero_comprobante": nro or "Alícuota no inscripto",
                        "alicuota_retencion": float(alicuot_ret)
                        or company.arba_alicuota_no_sincripto_retencion,
                        "alicuota_percepcion": float(alicuot_per)
                        or company.arba_alicuota_no_sincripto_percepcion,
                        "partner_id": commercial_partner.id,
                        "company_id": company.id,
                        "tag_id": padron_file.jurisdiction_id.id,
                        "from_date": from_date,
                        "to_date": to_date,
                    }
                )
            if arba_tag and arba_tag.id in invoice_tags.ids:
                arba_data = company.get_arba_data(
                    commercial_partner,
                    from_date,
                    to_date,
                )
                # si no hay numero de comprobante entonces es porque no
                # figura en el padron, aplicamos alicuota no inscripto
                if not arba_data["numero_comprobante"]:
                    arba_data["numero_comprobante"] = "Alícuota no inscripto"
                    arba_data[
                        "alicuota_retencion"
                    ] = company.arba_alicuota_no_sincripto_retencion
                    arba_data[
                        "alicuota_percepcion"
                    ] = company.arba_alicuota_no_sincripto_percepcion

                arba_data["partner_id"] = commercial_partner.id
                arba_data["company_id"] = company.id
                arba_data["tag_id"] = arba_tag.id
                arba_data["from_date"] = from_date
                arba_data["to_date"] = to_date
                alicuot = partner.arba_alicuot_ids.sudo().create(arba_data)
            # TODO ESTE ELIF NO ES NECESARIO PORQUE SE CARGA DEL PADRON O NO EXISTE
            # elif agip_tag and agip_tag.id in invoice_tags.ids:
            #     agip_data = company.get_agip_data(
            #         commercial_partner,
            #         date,
            #     )
            #     # si no hay numero de comprobante entonces es porque no
            #     # figura en el padron, aplicamos alicuota no inscripto
            #     if not agip_data['numero_comprobante']:
            #         agip_data['numero_comprobante'] = \
            #             'Alícuota no inscripto'
            #         agip_data['alicuota_retencion'] = \
            #             company.agip_alicuota_no_sincripto_retencion
            #         agip_data['alicuota_percepcion'] = \
            #             company.agip_alicuota_no_sincripto_percepcion
            #     agip_data['from_date'] = from_date
            #     agip_data['to_date'] = to_date
            #     agip_data['partner_id'] = commercial_partner.id
            #     agip_data['company_id'] = company.id
            #     agip_data['tag_id'] = agip_tag.id
            #     alicuot = partner.arba_alicuot_ids.sudo().create(agip_data)
            elif cdba_tag and cdba_tag.id in invoice_tags.ids:
                cordoba_data = company.get_cordoba_data(
                    commercial_partner,
                    date,
                )
                cordoba_data["from_date"] = from_date
                cordoba_data["to_date"] = to_date
                cordoba_data["partner_id"] = commercial_partner.id
                cordoba_data["company_id"] = company.id
                cordoba_data["tag_id"] = cdba_tag.id
                alicuot = partner.arba_alicuot_ids.sudo().create(cordoba_data)
        return alicuot

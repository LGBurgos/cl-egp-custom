from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import os
import re


class ResCompanyJurisdictionPadron(models.Model):
    _inherit = "res.company.jurisdiction.padron"

    @api.constrains("jurisdiction_id")
    def check_jurisdiction_id(self):
        arba_tag = self.env.ref("l10n_ar_ux.tag_tax_jurisdiccion_902")
        agip_tag = self.env.ref("l10n_ar_ux.tag_tax_jurisdiccion_901")
        for rec in self:
            if rec.jurisdiction_id not in (arba_tag, agip_tag):
                raise ValidationError(
                    _("El padron para (%s) no está implementado.")
                    % rec.jurisdiction_id.name
                )

    def _get_aliquit(self, partner):
        arba_tag = self.env.ref("l10n_ar_ux.tag_tax_jurisdiccion_902")  # ARBA
        agip_tag = self.env.ref("l10n_ar_ux.tag_tax_jurisdiccion_901")  # AGIP

        nro = False
        aliquot_ret = 0.0
        aliquot_per = 0.0

        # Determinar la jurisdicción
        is_arba = self.jurisdiction_id == arba_tag
        is_agip = self.jurisdiction_id == agip_tag

        if is_arba:
            # Para ARBA, buscamos archivos separados para Percepción y Retención
            padron_types = ["Per", "Ret"]
            for padron_type in padron_types:
                pattern = f"PadronRGS{padron_type}{self.l10n_ar_padron_from_date.month:02d}{self.l10n_ar_padron_from_date.year}.TXT"
                path_file = self.find_file("/tmp/", pattern)
                if not path_file:
                    self.descompress_file(self.file_padron)
                    path_file = self.find_file("/tmp/", pattern)

                if not path_file:
                    raise ValidationError(
                        _(
                            "No se encontró el archivo de padrón para %s en el período %s/%s."
                        )
                        % (
                            padron_type,
                            self.l10n_ar_padron_from_date.month,
                            self.l10n_ar_padron_from_date.year,
                        )
                    )

                nro_found, aliquot = self.find_aliquot("/tmp/" + path_file, partner.vat)
                if nro_found:  # Solo actualizamos nro si encontramos un valor
                    nro = nro_found
                if padron_type == "Per":
                    aliquot_per = aliquot and float(aliquot.replace(",", "."))
                else:
                    aliquot_ret = aliquot and float(aliquot.replace(",", "."))

        elif is_agip:
            # Para AGIP, un solo archivo con ambas alícuotas
            pattern = f"ARDJU008{self.l10n_ar_padron_from_date.month:02d}{self.l10n_ar_padron_from_date.year}.txt"
            path_file = self.find_file("/tmp/", pattern)
            if not path_file:
                self.descompress_file(self.file_padron)
                path_file = self.find_file("/tmp/", pattern)

            if not path_file:
                raise ValidationError(
                    _("No se encontró el archivo de padrón AGIP para el período %s/%s.")
                    % (
                        self.l10n_ar_padron_from_date.month,
                        self.l10n_ar_padron_from_date.year,
                    )
                )

            nro, aliquot_per, aliquot_ret = self._find_agip_aliquots(
                "/tmp/" + path_file, partner.vat
            )
            aliquot_per = aliquot_per and float(aliquot_per.replace(",", "."))
            aliquot_ret = aliquot_ret and float(aliquot_ret.replace(",", "."))

        else:
            raise ValidationError(
                _("La jurisdicción %s no está soportada para la lectura del padrón.")
                % self.jurisdiction_id.name
            )

        return nro, aliquot_ret, aliquot_per

    def find_file(self, rootdir, pattern):
        """Busca un archivo en el directorio basado en un patrón específico."""
        for subdir, dirs, files in os.walk(rootdir):
            for f in files:
                if re.search(pattern, f, re.IGNORECASE):
                    return f
        return False

    def find_aliquot(self, path, cuit):
        """Lectura de alícuotas para ARBA."""
        with open(path, "r") as fp:
            for line in fp.readlines():
                values = line.strip().split(";")
                if len(values) >= 10 and values[4] == cuit:  # CUIT en posición 4
                    return values[9], values[8]  # nro en 9, alícuota en 8
        return False, False

    def _find_agip_aliquots(self, path, cuit):
        """Lectura de alícuotas para AGIP, optimizada para archivos grandes y usando ISO-8859-1."""
        try:
            with open(
                path, "r", encoding="ISO-8859-1"
            ) as fp:  # Usar ISO-8859-1 según chardet
                for line in fp:  # Iterar línea por línea para mayor eficiencia
                    values = line.strip().split(";")
                    if len(values) >= 9 and values[3] == cuit:  # CUIT en posición 3
                        return (
                            False,
                            values[7],
                            values[8],
                        )  # percepción en 7, retención en 8
        except UnicodeDecodeError as e:
            _logger.error("Error al decodificar el archivo AGIP: %s", str(e))
            raise ValidationError(
                _(
                    "El archivo de padrón AGIP no está en un formato legible. Verifica la codificación del archivo."
                )
            )
        return False, False, False

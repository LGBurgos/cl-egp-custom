import requests
import logging
from datetime import datetime
from odoo import models, fields

_logger = logging.getLogger(__name__)

USD_VARIANTS = [
    {'code': 'USB', 'name': 'Dolar Blue','symbol': 'USDB'},
    {'code': 'BOL', 'name': 'Dolar Bolsa','symbol': 'USDBOLSA'},
    {'code': 'CCL', 'name': 'Dolar Contado con Liquidación','symbol': 'USDCCL'},
    {'code': 'MAY', 'name': 'Dolar Mayorista','symbol': 'USDMAY'},
    {'code': 'CRIP', 'name': 'Dolar Cripto','symbol': 'USDCRIP'},
    {'code': 'TARJ', 'name': 'Dolar Tarjeta','symbol': 'USDTARJ'},
]


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def _cron_actualizar_dolar_dolarapi(self):
        company = self.env.company

        # === 1. Procesar todos los USD de dolarapi.com ===
        url_usd = "https://dolarapi.com/v1/dolares"
        try:
            res = requests.get(url_usd, timeout=10)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            _logger.warning("❌ Error al obtener cotizaciones USD: %s", str(e))
            data = []

        for item in data:
            casa = item.get("casa")  # Ej: 'blue', 'oficial', etc.
            venta = item.get("venta")
            fecha_str = item.get("fechaActualizacion")

            if not casa or not venta or not fecha_str:
                _logger.warning("❌ Datos incompletos en USD: %s", item)
                continue

            # Armar código interno según casa
            if casa == 'oficial':
                currency = self.env.ref("base.USD", raise_if_not_found=False)
            elif casa == 'blue':
                currency = self.env.ref("custom_currency_dolarapi.res_currency_usd_blue", raise_if_not_found=False)
            elif casa == 'bolsa':
                currency = self.env.ref("custom_currency_dolarapi.res_currency_usd_bolsa", raise_if_not_found=False)
            elif casa == 'contadoconliqui':
                currency = self.env.ref("custom_currency_dolarapi.res_currency_usd_ccl", raise_if_not_found=False)
            elif casa == 'mayorista':
                currency = self.env.ref("custom_currency_dolarapi.res_currency_usd_mayorista", raise_if_not_found=False)
            elif casa == 'cripto':
                currency = self.env.ref("custom_currency_dolarapi.res_currency_usd_cripto", raise_if_not_found=False)
            elif casa == 'tarjeta':
                currency = self.env.ref("custom_currency_dolarapi.res_currency_usd_tarjeta", raise_if_not_found=False)
            else:
                _logger.warning("❌ Casa desconocida: %s", casa)
                continue

            
            if not currency:
                _logger.info("ℹ️ Moneda %s no encontrada. Omitida.", casa)
                continue

            if not currency.active:
                _logger.info("ℹ️ Moneda %s inactiva. Omitida.", casa)
                continue

            try:
                fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00")).date()
            except Exception as e:
                _logger.warning("❌ Error al parsear fecha para %s: %s", str(e))
                continue

            # Verificar si ya existe tasa para esa fecha
            existe = self.env['res.currency.rate'].search([
                ('currency_id', '=', currency.id),
                ('name', '=', fecha),
                ('company_id', '=', company.id),
            ], limit=1)

            if existe:
                _logger.info("🔁 Ya existe tasa de %s para %s", currency.name, fecha)
                existe.write({
                    'rate': 1 / float(venta) if venta else 0,
                })
                _logger.info("✅ Tasa actualizada %s (%s): %.6f", currency.name, fecha, 1 / float(venta) if venta else 0)
                continue

            try:
                rate = 1 / float(venta)
            except ZeroDivisionError:
                _logger.warning("❌ Venta en 0 para %s (%s)", fecha)
                continue

            self.env['res.currency.rate'].create({
                'currency_id': currency.id,
                'rate': rate,
                'name': fecha,
                'company_id': company.id,
            })
            _logger.info("✅ Tasa creada %s (%s): %.6f", currency.name, fecha, rate)

        # === 2. Procesar el EUR oficial aparte ===
        url_eur = "https://dolarapi.com/v1/cotizaciones/eur"
        try:
            res = requests.get(url_eur, timeout=10)
            res.raise_for_status()
            item = res.json()
        except Exception as e:
            _logger.warning("❌ Error al obtener cotización EUR: %s", str(e))
            return

        venta = item.get("venta")
        fecha_str = item.get("fechaActualizacion")

        if not venta or not fecha_str:
            _logger.warning("❌ Faltan datos para EUR: venta o fecha.")
            return

        try:
            fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00")).date()
        except Exception as e:
            _logger.warning("❌ Error al parsear fecha EUR: %s", str(e))
            return

        currency = self.env.ref("base.EUR", raise_if_not_found=False)
        if not currency:
            _logger.info("ℹ️ Moneda EUR no encontrada.")
            return

        if not currency.active:
            _logger.info("ℹ️ Moneda EUR inactiva. Omitida.")
            return

        existe = self.env['res.currency.rate'].search([
            ('currency_id', '=', currency.id),
            ('name', '=', fecha),
            ('company_id', '=', company.id),
        ], limit=1)

        if existe:
            existe.write({
                'rate': 1 / float(venta) if venta else 0,
            })
            _logger.info("🔁 Ya existe tasa de EUR para %s", fecha)
            return

        try:
            rate = 1 / float(venta)
        except ZeroDivisionError:
            _logger.warning("❌ Venta en 0 para EUR (%s)", fecha)
            return

        self.env['res.currency.rate'].create({
            'currency_id': currency.id,
            'rate': rate,
            'name': fecha,
            'company_id': company.id,
        })
        _logger.info("✅ Tasa creada EUR (%s): %.6f", fecha, rate)


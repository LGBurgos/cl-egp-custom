{
    "name": "Account Follow-up – Exclude Paid Invoices",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Exclude paid invoices from follow-up reminders",
    "description": """
Patch module for Odoo 18.

Excludes invoices marked as PAID from account follow-up reminders,
even if small residuals exist due to exchange rate differences or rounding.
""",
    "depends": [
        "account_followup",
    ],
    "data": [],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}

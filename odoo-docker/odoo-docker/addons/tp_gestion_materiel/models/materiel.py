from odoo import models, fields


class TpMateriel(models.Model):
    _name = "tp.materiel"
    _description = "Gestion du Matériel"

    name = fields.Char(string="Nom du matériel", required=True)
    reference = fields.Char(string="Référence Série")

    type_materiel = fields.Selection([
        ('pc', 'Ordinateur'),
        ('ecran', 'Écran'),
        ('imprimante', 'Imprimante'),
        ('accessoire', 'Accessoire')
    ], string="Type", default='pc')

    date_achat = fields.Date(string="Date d'achat")
    cout = fields.Float(string="Coût d'achat")

    etat = fields.Selection([
        ('neuf', 'Neuf'),
        ('bon', 'Bon état'),
        ('panne', 'En panne'),
        ('rebut', 'Au rebut')
    ], string="État", default='neuf')

    description = fields.Text(string="Notes")

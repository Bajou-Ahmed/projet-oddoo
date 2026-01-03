from odoo import models, fields, api

class AbsenceRequest(models.Model):
    _name = "absence.request"
    _description = "Demande d'Absence et Justification"
    _order = "request_date desc, id desc"

    name = fields.Char(string="Référence", readonly=True, default=lambda self: 'New')
    employee_id = fields.Many2one('res.users', string="Employé", required=True, default=lambda self: self.env.user)
    request_date = fields.Date(string="Date de demande", required=True, default=fields.Date.context_today)
    
    # Dates d'absence
    date_start = fields.Datetime(string="Date et heure de début", required=True)
    date_end = fields.Datetime(string="Date et heure de fin", required=True)
    duration_days = fields.Float(string="Durée (jours)", compute="_compute_duration", store=True, readonly=True)
    
    # Type d'absence
    absence_type = fields.Selection([
        ('sick', 'Maladie'),
        ('vacation', 'Congé'),
        ('personal', 'Personnel'),
        ('maternity', 'Congé Maternité'),
        ('paternity', 'Congé Paternité'),
        ('other', 'Autre')
    ], string="Type d'absence", required=True, default='personal')
    
    # Justification
    justification = fields.Text(string="Justification", required=True, help="Veuillez justifier votre absence")
    attachment_ids = fields.Many2many('ir.attachment', string="Pièces jointes", help="Joindre des documents justificatifs si nécessaire")
    
    # Workflow de validation
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('refused', 'Refusé')
    ], string="Statut", default='draft', required=True)
    
    # Validation
    manager_id = fields.Many2one('res.users', string="Manager", compute="_compute_manager", store=True)
    manager_comment = fields.Text(string="Commentaire du manager")
    approval_date = fields.Datetime(string="Date d'approbation", readonly=True)
    approved_by = fields.Many2one('res.users', string="Approuvé par", readonly=True)
    
    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                delta = record.date_end - record.date_start
                record.duration_days = delta.total_seconds() / 86400.0  # Convertir en jours
            else:
                record.duration_days = 0.0
    
    @api.depends('employee_id')
    def _compute_manager(self):
        for record in self:
            # Par défaut, on peut utiliser le manager de l'employé si disponible
            # Pour l'instant, on cherche un utilisateur admin par défaut
            if record.employee_id:
                # Si le module hr est installé, on pourrait utiliser hr.employee.parent_id
                # Pour l'instant, on cherche un utilisateur admin par défaut
                try:
                    admin_user = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_system').ids)], limit=1)
                    record.manager_id = admin_user if admin_user else False
                except:
                    record.manager_id = False
            else:
                record.manager_id = False
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('absence.request') or 'New'
        return super(AbsenceRequest, self).create(vals)
    
    def action_submit(self):
        """Soumet la demande d'absence"""
        self.write({'state': 'submitted'})
    
    def action_approve(self):
        """Approuve la demande d'absence"""
        self.write({
            'state': 'approved',
            'approval_date': fields.Datetime.now(),
            'approved_by': self.env.user.id
        })
    
    def action_refuse(self):
        """Refuse la demande d'absence"""
        self.write({'state': 'refused'})
    
    def action_reset_to_draft(self):
        """Remet la demande en brouillon"""
        self.write({'state': 'draft'})
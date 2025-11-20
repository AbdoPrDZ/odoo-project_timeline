# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from .tools import format_duration_display


class Project(models.Model):
  _inherit = 'project.project'

  timeline_ids = fields.One2many(
      'project.timeline',
      'project_id',
      string='Timelines',
      help='Timelines associated with this project',
  )
  timeline_duration = fields.Integer(
      string='Total Timeline Duration',
      help='Total duration of all timelines associated with this project',
      compute='_compute_timeline_duration',
  )
  timeline_duration_display = fields.Char(
      string='Total Timeline Duration',
      help='Total duration of all timelines associated with this project',
      compute='_compute_timeline_duration',
  )

  @api.model
  def create(self, vals):
    if not self.env.user.employee_id:
      raise ValidationError(
          _('User must be linked to an employee to create a project.')
      )
    return super().create(vals)

  @api.depends('timeline_ids.duration')
  def _compute_timeline_duration(self):
    for project in self:
      duration = sum(project.timeline_ids.mapped('duration'))
      project.timeline_duration = duration
      project.timeline_duration_display = format_duration_display(duration)

  def _prepare_values(self):    
    return [
        {
            'id': rec.id,
            'name': rec.name,
            'duration': rec.timeline_duration,
            'type_ids': [[typ.id, typ.name] for typ in rec.type_ids],
            'create_date': rec.create_date,
        } for rec in self
    ]

  def _check_user_access(self):
    """ Validates if the current user has access to the given project. """

    if not self.env.user.employee_id:
      raise ValidationError(
          _('User must be linked to an employee to access projects.')
      )

    if len(self) > 1:
      for rec in self:
        if not rec.exists() or rec.create_uid != self.env.user:
          raise ValidationError(
              _('You do not have access to this project.')
          )

  @api.model
  def app_create(self, vals):
    """ Creates a new project for the current user. """

    self._check_user_access()

    name = vals.get('name')
    
    if not name:
      raise ValidationError(
          _('Project name is required.')
      )

    project = self.create({
        'name': name,
    })

    return project._prepare_values()

  @api.model
  def app_search_read(self, limit=10, offset=0, order=None, **kwargs):
    """ Returns the main projects for the current user. """

    items = self.search([
        ('create_uid', '=', self.env.user.id),
        # ('employee_ids', 'in', [user.employee_id.id])
    ], limit=limit, offset=offset, order=order)

    items._check_user_access()

    return items._prepare_values()

  def app_read(self, **kwargs):
    """ Returns a specific project by ID for the current user. """

    self._check_user_access()

    return self._prepare_values()

  def app_write(self, vals):
    """ Updates the current project. """

    self._check_user_access()

    name = vals.get('name')

    if name:
      self.name = name

    return True

  def app_unlink(self):
    """ Deletes the current project. """

    self._check_user_access()

    return self.unlink()

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectTaskType(models.Model):
  _inherit = 'project.task.type'

  task_ids = fields.One2many(
      'project.task',
      'stage_id',
      string='Tasks',
      help='Tasks associated with this task type',
  )

  def _prepare_values(self):
    return [
        {
            'id': rec.id,
            'name': rec.name,
            'project_ids': [[proj.id, proj.name] for proj in rec.project_ids],
            'task_ids': [[task.id, task.name] for task in rec.task_ids],
            'create_date': rec.create_date,
        }
        for rec in self
    ]

  def _check_user_access(self):
    """ Validates if the current user has access to the given project. """

    if not self.env.user.employee_id:
      raise ValidationError(
          _('User must be linked to an employee to access projects.')
      )
    
    if len(self) > 0:
      projects = self.mapped('project_ids')
      projects._check_user_access()

  @api.model
  def app_create(self, vals):
    self._check_user_access()

    name = vals.get('name')
    project_ids = vals.get('project_ids', [])

    if not name or not project_ids:
      raise ValidationError(_("The 'name' and 'project_ids' fields are required to create a Project Task Type."))

    task_type = self.create({
      'name': name,
      'project_ids': [(6, 0, project_ids)],
    })

    return task_type._prepare_values()

  @api.model
  def app_search_read(self, domain, limit=10, offset=0, order=None, **kwargs):
    """ Returns the main projects for the current user. """

    project_ids = []
    if domain:
      for condition in domain:
        if condition[0] == 'project_ids' and condition[1] == 'in':
          project_ids = condition[2]
          break

    if not project_ids:
      raise ValidationError(_("The 'project_ids' field is required to search Project Task Types."))

    items = self.search([
        ('project_ids', 'in', project_ids),
        ('create_uid', '=', self.env.user.id),
    ], limit=limit, offset=offset, order=order)

    items._check_user_access()

    return items._prepare_values()

  def app_read(self, **kwargs):
    """ Returns a specific project by ID for the current user. """

    self._check_user_access()

    return self._prepare_values()

  def app_write(self, vals):
    """ Updates the current project task type. """

    self._check_user_access()

    name = vals.get('name')

    if name:
      self.name = name

    return True

  def app_unlink(self):
    """ Deletes the current project task type. """

    self._check_user_access()

    return self.unlink()

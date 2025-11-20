# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from .tools import format_duration_display


class ResUsers(models.Model):
  _inherit = 'res.users'

  running_project_timeline_id = fields.Many2one(
      'project.timeline',
      string='Running Project Timeline',
      help='Currently running project timeline for the user',
  )


class ProjectTask(models.Model):
  _inherit = 'project.task'

  timeline_ids = fields.One2many(
      'project.timeline',
      'task_id',
      string='Timelines',
      help='Timelines associated with this task',
  )
  running_timeline_id = fields.Many2one(
      'project.timeline',
      string='Running Timeline',
      help='Currently running timeline for this task',
      compute='_compute_running_timeline',
  )
  timeline_duration = fields.Integer(
      string='Total Timeline Duration',
      help='Total duration of all timelines associated with this task',
      compute='_compute_timeline_duration',
  )
  timeline_duration_display = fields.Char(
      string='Total Timeline Duration',
      help='Total duration of all timelines associated with this task',
      compute='_compute_timeline_duration',
  )

  @api.depends_context('uid')
  def _compute_running_timeline(self):
    user_running_timeline = self.env.user.running_project_timeline_id
    for task in self:
      task.running_timeline_id = user_running_timeline and user_running_timeline.task_id.id == task.id and user_running_timeline.id or False

  @api.depends('timeline_ids.duration')
  def _compute_timeline_duration(self):
    for task in self:
      duration = sum(task.timeline_ids.mapped('duration'))
      task.timeline_duration = duration
      task.timeline_duration_display = format_duration_display(duration)

  def _check_user_access(self):
    user = self.env.user

    if not user.employee_id:
      raise ValidationError(
          _('User must be linked to an employee to access task timelines.')
      )

    # if user.employee_id.id not in self.employee_ids.ids and user.id != self.create_uid.id:
    #   raise ValidationError(
    #       _('User must be assigned to the task to access task timelines.')
    #   )

    if len(self) > 0:
      projects = self.mapped('project_id')
      projects._check_user_access()

  def start_timeline(self):
    self._check_user_access()

    user = self.env.user
    if user.running_project_timeline_id:
      raise ValidationError(
          _('You already have an active project timeline. Please stop it before starting a new one.')
      )

    timeline = self.env['project.timeline'].create({
        'task_id': self.id,
        'project_id': self.project_id.id,
        'start_date': fields.Datetime.now(),
    })

    user.running_project_timeline_id = timeline.id

  def stop_timeline(self):
    self._check_user_access()

    user = self.env.user
    if not user.running_project_timeline_id or user.running_project_timeline_id.task_id.id != self.id:
      raise ValidationError(
          _('No active project timeline to stop.')
      )

    user.running_project_timeline_id.end_date = fields.Datetime.now()
    user.running_project_timeline_id = False

  def _prepare_values(self):
    return [
        {
            'id': rec.id,
            'name': rec.name,
            'project_id': rec.project_id.id,
            'stage_id': rec.stage_id.id,
            'duration': rec.timeline_duration,
            'running_timeline_id': rec.running_timeline_id.id,
            'create_date': rec.create_date,
        }
        for rec in self
    ]

  @api.model
  def app_create(self, vals):
    name = vals.get('name')
    project_id = vals.get('project_id')
    stage_id = vals.get('stage_id')
    
    if not name or not project_id or not stage_id:
      raise ValidationError(_("The 'name', 'project_id', and 'stage_id' fields are required to create a Project Task."))

    task = self.create({
      'name': name,
      'project_id': project_id,
      'stage_id': stage_id,
    })
    
    return task._prepare_values()

  @api.model
  def app_search_read(self, domain, limit=10, offset=0, order=None, **kwargs):
    """ Returns the main tasks for the current user. """

    project_id = None
    if domain:
      for condition in domain:
        if condition[0] == 'project_id' and condition[1] == '=':
          project_id = condition[2]
          break

    tasks = self.search([
        ('project_id', '=', project_id),
        ('create_uid', '=', self.env.user.id),
    ], limit=limit, offset=offset, order=order)

    tasks._check_user_access()

    return tasks._prepare_values()

  def app_read(self, **kwargs):
    """ Returns a specific task by ID for the current user. """

    self._check_user_access()

    return self._prepare_values()

  def app_write(self, vals):
    """ Updates the current project task. """

    self._check_user_access()

    name = vals.get('name')
    stage_id = vals.get('stage_id')

    if name:
      self.name = name
    if stage_id:
      self.stage_id = stage_id

    return True

  def app_unlink(self):
    """ Deletes the current project task. """

    self._check_user_access()

    return self.unlink()

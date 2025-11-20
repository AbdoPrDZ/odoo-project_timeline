# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from .tools import format_duration_display


class ProjectTimeline(models.Model):
  _name = 'project.timeline'
  _description = 'Project Timeline'

  task_id = fields.Many2one(
      'project.task',
      string='Task',
      help='Task associated with this timeline',
      required=True,
      readonly=True,
  )
  project_id = fields.Many2one(
      'project.project',
      string='Project',
      help='Project associated with this timeline',
      related='task_id.project_id',
      store=True,
  )
  employee_id = fields.Many2one(
      'hr.employee',
      string='Employee',
      help='Employee associated with this timeline',
      related='create_uid.employee_id',
      store=True,
  )
  start_date = fields.Datetime(
      string='Start Datetime',
      help='Start datetime of the timeline',
      required=True,
      readonly=True,
  )
  end_date = fields.Datetime(
      string='End Datetime',
      help='End datetime of the timeline',
      readonly=True,
  )
  duration = fields.Integer(
      string='Duration',
      help='Duration of the timeline',
      compute='_compute_duration',
  )
  duration_display = fields.Char(
      string='Duration',
      help='Human-readable duration display',
      compute='_compute_duration',
  )
  state = fields.Selection(
      [('running', 'Running'), ('stopped', 'Stopped')],
      string='State',
      help='Current state of the timeline',
      compute='_compute_state',
  )

  @api.depends('start_date', 'end_date')
  def _compute_duration(self):
    for timeline in self:
      duration = 0

      if timeline.end_date:
        duration = (timeline.end_date - timeline.start_date).total_seconds()

      timeline.duration = int(duration)
      timeline.duration_display = format_duration_display(duration)

  @api.depends('start_date', 'end_date')
  def _compute_state(self):
    for timeline in self:
      timeline.state = 'running' if not timeline.end_date else 'stopped'

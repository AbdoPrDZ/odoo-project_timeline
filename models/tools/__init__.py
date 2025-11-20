# -*- coding: utf-8 -*-

def format_duration_display(seconds):
  """Convert duration in seconds to a human-readable format."""

  days = seconds // 86400
  hours = (seconds % 86400) // 3600
  minutes = (seconds % 3600) // 60

  parts = []
  if days > 0:
    parts.append(f"{int(days)}d")
  if hours > 0:
    parts.append(f"{int(hours)}h")
  if minutes > 0 and len(parts) < 2:
    parts.append(f"{int(minutes)}m")
  if len(parts) < 2:
    parts.append(f"{int(seconds)}s")

  return ' '.join(parts)

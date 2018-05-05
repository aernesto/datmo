from __future__ import print_function

import shlex
import platform
import prettytable

from datmo.core.util.i18n import get as __
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.task import TaskController


class TaskCommand(ProjectCommand):
    def __init__(self, home, cli_helper, parser):
        super(TaskCommand, self).__init__(home, cli_helper, parser)
        self.task_controller = TaskController(home=home)

    def run(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.task.run"))

        # Create input dictionaries
        snapshot_dict = {}
        if kwargs['environment_definition_filepath']:
            snapshot_dict["environment_definition_filepath"] =\
                kwargs['environment_definition_filepath']

        if not isinstance(kwargs['cmd'], list):
            if platform.system() == "Windows":
                kwargs['cmd'] = kwargs['cmd']
            elif isinstance(kwargs['cmd'], str) or isinstance(
                    kwargs['cmd'], unicode):
                kwargs['cmd'] = shlex.split(kwargs['cmd'])

        task_dict = {
            "gpu": kwargs['gpu'],
            "ports": kwargs['ports'],
            "interactive": kwargs['interactive'],
            "command": kwargs['cmd']
        }

        # Create the task object
        task_obj = self.task_controller.create(task_dict)

        # Pass in the task
        try:
            updated_task_obj = self.task_controller.run(
                task_obj.id, snapshot_dict=snapshot_dict)
        except:
            self.cli_helper.echo(__("error", "cli.task.run", task_obj.id))
            return False
        return updated_task_obj

    def ls(self, **kwargs):
        session_id = kwargs.get('session_id',
                                self.task_controller.current_session.id)
        # Get all snapshot meta information
        header_list = ["id", "command", "status", "gpu", "created at"]
        t = prettytable.PrettyTable(header_list)
        task_objs = self.task_controller.list(
            session_id, sort_key='created_at', sort_order='descending')
        for task_obj in task_objs:
            t.add_row([
                task_obj.id, task_obj.command, task_obj.status, task_obj.gpu,
                task_obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
        self.cli_helper.echo(t)

        return True

    def stop(self, **kwargs):
        task_id = kwargs.get('id', None)
        self.cli_helper.echo(__("info", "cli.task.stop", task_id))
        try:
            result = self.task_controller.stop(task_id)
            if not result:
                self.cli_helper.echo(__("error", "cli.task.stop", task_id))
            return result
        except:
            self.cli_helper.echo(__("error", "cli.task.stop", task_id))
            return False

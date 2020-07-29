import click
import yaml

from plantit_cli.executor.inprocessexecutor import InProcessExecutor
from plantit_cli.executor.jobqueueexecutor import JobQueueExecutor
from plantit_cli.run import Run
from plantit_cli.store.irods import IRODSOptions


@click.command()
@click.argument('workflow')
@click.option('--token', required=False, type=str)
@click.option('--irods_host', required=False, type=str)
@click.option('--irods_port', required=False, type=int)
@click.option('--irods_username', required=False, type=str)
@click.option('--irods_password', required=False, type=str)
@click.option('--irods_zone', required=False, type=str)
def run(workflow, token, irods_host, irods_port, irods_username, irods_password, irods_zone):
    with open(workflow, 'r') as file:
        workflow_def = yaml.safe_load(file)
        workflow_def['token'] = token

        irods_options = None if irods_host is None else IRODSOptions(irods_host,
                                                                     irods_port,
                                                                     irods_username,
                                                                     irods_password,
                                                                     irods_zone)

        if 'api_url' not in workflow_def:
            workflow_def['api_url'] = None

        if 'executor' in workflow_def:
            executor_def = workflow_def['executor']
            del workflow_def['executor']
        else:
            executor_def = {'in-process'}

        if 'in-process' in executor_def:
            InProcessExecutor(irods_options).execute(Run(**workflow_def))
        elif 'pbs' in executor_def:
            executor_def = dict(executor_def['pbs'])
            executor_def['name'] = 'pbs'
            JobQueueExecutor(irods_options, **executor_def).execute(Run(**workflow_def))
        elif 'slurm' in executor_def['name']:
            executor_def = dict(executor_def['slurm'])
            executor_def['name'] = 'slurm'
            JobQueueExecutor(irods_options, **executor_def).execute(Run(**workflow_def))
        else:
            raise ValueError(f"Unrecognized executor (supported: 'in-process', 'pbs', 'slurm')")

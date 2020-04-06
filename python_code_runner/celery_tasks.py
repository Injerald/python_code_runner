import os
import tarfile

import docker

from celery import Celery
from celery.utils.log import get_task_logger

celery = Celery('flask', broker='amqp://guest@localhost//', backend='amqp://guest@localhost//')

logger = get_task_logger(__name__)


def copy_to(client, src, dst):
    name, dst = dst.split(':')
    container = client.containers.get(name)
    tar_file = src + '.tar'

    os.chdir(os.path.dirname(src))
    srcname = os.path.basename(src)
    tar = tarfile.open(src + '.tar', mode='w')
    try:
        tar.add(srcname)
    finally:
        tar.close()

    data = open(tar_file, 'rb').read()
    container.put_archive(os.path.dirname(dst), data)
    # Deleting py script file
    os.remove(tar_file)


@celery.task(bind=True, reply_to='code_results')
def process_code_execution(self, code):
    # Creating py script file
    filename = f'{self.request.id}.py'
    path_to_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'temp_code_files', filename
    )
    with open(path_to_file, 'w') as f:
        f.write(code)

    # Executing code in docker container
    client = docker.from_env()
    container = client.containers.run('python:3.7', detach=True, tty=True)
    copy_to(client, path_to_file, f'{container.name}:/')
    result = container.exec_run(f'python3 {filename}')
    container.remove(force=True)

    # Deleting py script file
    os.remove(path_to_file)

    return result.output.decode('utf-8')

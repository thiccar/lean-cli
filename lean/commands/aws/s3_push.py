# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean CLI v1.0. Copyright 2021 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
import subprocess
from typing import Optional

from click import command, option, argument

from lean.click import LeanCommand, PathParameter
from lean.constants import PROJECT_CONFIG_FILE_NAME
from lean.container import container


@command(cls=LeanCommand, name="s3-push")
@argument("bucket", type=str)
@option("--project",
        type=PathParameter(exists=True, file_okay=False, dir_okay=True),
        help="Path to the local project to push (all local projects if not specified)")
@option("--profile", type=str, help="AWS Profile to use (must have a section in ~/.aws/credentials)")
@option("--dryrun", is_flag=True, default=False, help="Corresponds to --dryrun option of aws s3 sync")
def s3_push(bucket: str, project: Optional[Path], profile: Optional[str], dryrun: bool) -> None:
    """Push local projects to S3 using AWS CLI docker image.
    https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3/sync.html
    https://docs.aws.amazon.com/cli/latest/userguide/getting-started-docker.html

    This command overrides the content of cloud files with the content of their respective local counterparts.

    This command will delete cloud files which don't have a local counterpart.
    """
    # Parse which projects need to be pushed
    if project is not None:
        project_config_manager = container.project_config_manager
        project_config = project_config_manager.get_project_config(project)
        if not project_config.file.exists():
            raise RuntimeError(f"'{project}' is not a Lean project")

        _s3_push_single_project(bucket, project, profile, dryrun)
    else:
        projects_to_push = [p.parent for p in Path.cwd().rglob(PROJECT_CONFIG_FILE_NAME)]
        for project in projects_to_push:
            _s3_push_single_project(bucket, project, profile, dryrun)

def _s3_push_single_project(bucket: str, project: Path, profile: Optional[str], dryrun: bool) -> None:
    logger = container.logger

    path_manager = container.path_manager
    relative_path = path_manager.get_relative_path(project)

    command_parts = [
        f"docker run --rm -v {Path.home()}/.aws:/root/.aws -v {Path.cwd()}:/workspace",
        f"amazon/aws-cli s3 sync /workspace/{relative_path.as_posix()} s3://{bucket}/{relative_path.as_posix()}",
        "--delete",
        "--dryrun" if dryrun else "",
        f"--profile {profile}" if profile is not None else ""
    ] + [
        f"--exclude {pattern}" for pattern in [
            "backtests/*", "__pycache__/*", "config.json", "bin/*", "obj/*", ".ipynb_checkpoints/*", ".idea/*",
            ".vscode/*", "storage/*"
        ]
    ]
    command = " ".join(command_parts)
    logger.info(command)
    cp = subprocess.run(command, shell=True)
    cp.check_returncode()

    project_manager = container.project_manager
    libraries = project_manager.get_project_libraries(project)
    for library in libraries:
        _s3_push_single_project(bucket, library, profile, dryrun)

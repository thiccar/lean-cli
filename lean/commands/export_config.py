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
import json
from pathlib import Path
from typing import List, Optional, Tuple
from click import command, option, argument, Choice

from lean.click import LeanCommand, PathParameter
from lean.container import container, Logger


@command(cls=LeanCommand, name="export-config", requires_lean_config=True)
@argument("project", type=PathParameter(exists=True, file_okay=True, dir_okay=True))
@argument("output-file", type=PathParameter(dir_okay=False))
@option("--env", type=str, help="Environment to configure (default = backtesting)")
def export_config(project: Path, output_file: Path, env: Optional[str], **kwargs) -> None:
    logger = container.logger
    project_manager = container.project_manager
    algorithm_file = project_manager.find_algorithm_file(Path(project))
    lean_config_manager = container.lean_config_manager

    environment = "backtesting" if env is None else env
    lean_config = lean_config_manager.get_complete_lean_config(environment, algorithm_file, None)
    with output_file.open("w") as f:
        json.dump(lean_config, f, indent=4)
        logger.info(f"Wrote config to {output_file}")

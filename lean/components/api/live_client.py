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

from datetime import datetime
from math import floor
from typing import Any, List, Optional

from lean.components.api.api_client import APIClient
from lean.models.api import QCLiveAlgorithm, QCLiveAlgorithmStatus


class LiveClient:
    """The LiveClient class contains methods to interact with live/* API endpoints."""

    def __init__(self, api_client: APIClient) -> None:
        """Creates a new LiveClient instance.

        :param api_client: the APIClient instance to use when making requests
        """
        self._api = api_client

    def get_all(self,
                status: Optional[QCLiveAlgorithmStatus] = None,
                start: datetime = datetime.fromtimestamp(0),
                end: datetime = datetime.now()) -> List[QCLiveAlgorithm]:
        """Retrieves all live algorithms.

        :param status: the status to filter by or None if no status filter should be applied
        :param start: the earliest launch time the returned algorithms should have
        :param end: the latest launch time the returned algorithms should have
        :return: a list of live algorithms which match the given filters
        """
        parameters = {
            start: floor(start.timestamp()),
            end: floor(end.timestamp())
        }

        if status is not None:
            parameters["status"] = status

        data = self._api.get("live/read", parameters)
        return [QCLiveAlgorithm(**algorithm) for algorithm in data["live"]]

    def start(self,
              project_id: int,
              compile_id: str,
              node_id: str,
              brokerage_settings: Any,
              price_data_handler: str,
              tiingo_token: Optional[str] = None) -> QCLiveAlgorithm:
        """Starts live trading for a project.

        :param project_id: the id of the project to start live trading for
        :param compile_id: the id of the compile to use for live trading
        :param node_id: the id of the node to start live trading on
        :param brokerage_settings: the brokerage settings to use
        :param price_data_handler: the data feed to use
        :param tiingo_token: the Tiingo token to use for the Tiingo data feed or None to disable the Tiingo data feed
        :return: the created live algorithm
        """
        parameters = {
            "projectId": project_id,
            "compileId": compile_id,
            "nodeId": node_id,
            "brokerage": brokerage_settings,
            "dataHandler": price_data_handler,
            "versionId": "-1"
        }

        if tiingo_token is not None:
            parameters["addOnDataFeed"] = {
                "TiingoNews": {
                    "token": tiingo_token
                }
            }

        data = self._api.post("live/create", parameters)
        return QCLiveAlgorithm(**data)

    def stop(self, project_id: int) -> None:
        """Stops live trading for a certain project without liquidated existing positions.

        :param project_id: the id of the project to stop live trading for
        """
        self._api.post("live/update/stop", {
            "projectId": project_id
        })

    def liquidate_and_stop(self, project_id: int) -> None:
        """Stops live trading and liquidates existing positions for a certain project.

        :param project_id: the id of the project to stop live trading and liquidate existing positions for
        """
        self._api.post("live/update/liquidate", {
            "projectId": project_id
        })
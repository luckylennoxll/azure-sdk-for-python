# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

import logging
from collections.abc import Iterable
from typing import (
    TypeVar,
    Generic,
    Optional,
)
from .configuration import Configuration
from .pipeline import Pipeline
from .pipeline.transport._base import PipelineClientBase
from .pipeline.transport import HttpTransport
from .pipeline.policies import (
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    RequestIdPolicy,
    RetryPolicy,
)

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")

_LOGGER = logging.getLogger(__name__)


class PipelineClient(PipelineClientBase, Generic[HTTPRequestType, HTTPResponseType]):
    """Service client core methods.

    Builds a Pipeline client.

    :param str base_url: URL for the request.
    :keyword ~azure.core.configuration.Configuration config: If omitted, the standard configuration is used.
    :keyword Pipeline pipeline: If omitted, a Pipeline object is created and returned.
    :keyword list[HTTPPolicy] policies: If omitted, the standard policies of the configuration object is used.
    :keyword per_call_policies: If specified, the policies will be added into the policy list before RetryPolicy
    :paramtype per_call_policies: Union[HTTPPolicy, SansIOHTTPPolicy, list[HTTPPolicy], list[SansIOHTTPPolicy]]
    :keyword per_retry_policies: If specified, the policies will be added into the policy list after RetryPolicy
    :paramtype per_retry_policies: Union[HTTPPolicy, SansIOHTTPPolicy, list[HTTPPolicy], list[SansIOHTTPPolicy]]
    :keyword HttpTransport transport: If omitted, RequestsTransport is used for synchronous transport.
    :return: A pipeline object.
    :rtype: ~azure.core.pipeline.Pipeline

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_sync.py
            :start-after: [START build_pipeline_client]
            :end-before: [END build_pipeline_client]
            :language: python
            :dedent: 4
            :caption: Builds the pipeline client.
    """

    def __init__(
        self,
        base_url: str,
        *,
        pipeline: Optional[Pipeline[HTTPRequestType, HTTPResponseType]] = None,
        config: Optional[Configuration] = None,
        **kwargs
    ):
        super(PipelineClient, self).__init__(base_url)
        self._config: Configuration = config or Configuration(**kwargs)
        self._base_url = base_url

        self._pipeline = pipeline or self._build_pipeline(self._config, **kwargs)

    def __enter__(self):
        self._pipeline.__enter__()
        return self

    def __exit__(self, *exc_details):
        self._pipeline.__exit__(*exc_details)

    def close(self):
        self.__exit__()

    def _build_pipeline(  # pylint: disable=no-self-use
        self,
        config: Configuration,
        *,
        transport: Optional[HttpTransport[HTTPRequestType, HTTPResponseType]] = None,
        policies=None,
        per_call_policies=None,
        per_retry_policies=None,
        **kwargs
    ) -> Pipeline[HTTPRequestType, HTTPResponseType]:
        per_call_policies = per_call_policies or []
        per_retry_policies = per_retry_policies or []

        if policies is None:  # [] is a valid policy list
            policies = [
                config.request_id_policy or RequestIdPolicy(**kwargs),
                config.headers_policy,
                config.user_agent_policy,
                config.proxy_policy,
                ContentDecodePolicy(**kwargs),
            ]
            if isinstance(per_call_policies, Iterable):
                policies.extend(per_call_policies)
            else:
                policies.append(per_call_policies)

            policies.extend(
                [
                    config.redirect_policy,
                    config.retry_policy,
                    config.authentication_policy,
                    config.custom_hook_policy,
                ]
            )
            if isinstance(per_retry_policies, Iterable):
                policies.extend(per_retry_policies)
            else:
                policies.append(per_retry_policies)

            policies.extend(
                [
                    config.logging_policy,
                    DistributedTracingPolicy(**kwargs),
                    config.http_logging_policy or HttpLoggingPolicy(**kwargs),
                ]
            )
        else:
            if isinstance(per_call_policies, Iterable):
                per_call_policies_list = list(per_call_policies)
            else:
                per_call_policies_list = [per_call_policies]
            per_call_policies_list.extend(policies)
            policies = per_call_policies_list

            if isinstance(per_retry_policies, Iterable):
                per_retry_policies_list = list(per_retry_policies)
            else:
                per_retry_policies_list = [per_retry_policies]
            if len(per_retry_policies_list) > 0:
                index_of_retry = -1
                for index, policy in enumerate(policies):
                    if isinstance(policy, RetryPolicy):
                        index_of_retry = index
                if index_of_retry == -1:
                    raise ValueError(
                        "Failed to add per_retry_policies; no RetryPolicy found in the supplied list of policies. "
                    )
                policies_1 = policies[: index_of_retry + 1]
                policies_2 = policies[index_of_retry + 1 :]
                policies_1.extend(per_retry_policies_list)
                policies_1.extend(policies_2)
                policies = policies_1

        if transport is None:
            from .pipeline.transport import RequestsTransport

            transport = RequestsTransport(**kwargs)

        return Pipeline(transport, policies)

    def send_request(self, request: HTTPRequestType, **kwargs) -> HTTPResponseType:
        """Method that runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest('GET', 'http://www.example.com')
        <HttpRequest [GET], url: 'http://www.example.com'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.HttpResponse
        """
        stream = kwargs.pop("stream", False)  # want to add default value
        return_pipeline_response = kwargs.pop("_return_pipeline_response", False)
        pipeline_response = self._pipeline.run(request, stream=stream, **kwargs)  # pylint: disable=protected-access
        if return_pipeline_response:
            return pipeline_response  # type: ignore  # This is a private API we don't want to type in signature
        return pipeline_response.http_response

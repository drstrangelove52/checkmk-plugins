#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkmk 2.3 Server-Side Calls – Vectra Special Agent

noop_parser is used to receive the raw WATO dict.
The Password form spec delivers the token as a Secret object,
which is passed directly to SpecialAgentCommand. Checkmk resolves
the actual value at process launch and masks it in the UI.
"""

from collections.abc import Iterator, Mapping

from cmk.server_side_calls.v1 import (
    HostConfig,
    SpecialAgentCommand,
    SpecialAgentConfig,
    noop_parser,
)


def _generate_vectra_commands(
    params: Mapping[str, object],
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:

    brain_host    = str(params["brain_host"])
    no_verify_ssl = bool(params.get("no_verify_ssl", False))
    timeout       = int(params.get("timeout", 30))

    args: list = [
        "--brain",   brain_host,
        "--token",   params["api_token"],
        "--timeout", str(timeout),
    ]

    if "brain_port" in params:
        args += ["--port", str(params["brain_port"])]

    if no_verify_ssl:
        args.append("--no-verify-ssl")

    yield SpecialAgentCommand(command_arguments=args)


special_agent_vectra_sensors = SpecialAgentConfig(
    name="vectra_sensors",
    parameter_parser=noop_parser,
    commands_function=_generate_vectra_commands,
)

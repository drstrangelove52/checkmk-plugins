#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkmk 2.3 Server-Side Calls – Vectra Special Agent

noop_parser delivers the raw WATO dict. The Password form spec delivers
client_secret as a tuple (store_id, format, pass_safely). _to_secret()
reconstructs a proper Secret with pass_safely=False so Checkmk resolves
and passes the actual value directly to the agent.
"""

from collections.abc import Iterator, Mapping

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
    noop_parser,
)


def _to_secret(value: object) -> Secret:
    """Convert a raw noop_parser password value to a Checkmk Secret.

    pass_safely=False tells Checkmk to resolve the password on the server
    side and pass the actual value directly as a command-line argument.
    """
    if isinstance(value, Secret):
        return Secret(id=value.id, format=value.format, pass_safely=False)
    if isinstance(value, tuple) and len(value) == 3:
        store_id, fmt, _ = value
        return Secret(id=store_id, format=fmt, pass_safely=False)
    return Secret(id=str(value), format="%s", pass_safely=False)


def _generate_vectra_commands(
    params: Mapping[str, object],
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:

    brain_host    = str(params["brain_host"])
    no_verify_ssl = bool(params.get("no_verify_ssl", False))
    timeout       = int(params.get("timeout", 30))

    args: list = [
        "--brain",         brain_host,
        "--client-id",     str(params["client_id"]),
        "--client-secret", _to_secret(params["client_secret"]),
        "--timeout",       str(timeout),
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

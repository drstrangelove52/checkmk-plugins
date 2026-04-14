#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkmk 2.3 Server-Side Calls – Vectra Special Agent

The API token is wrapped in Secret so Checkmk masks it in process listings
and the UI. noop_parser is used to receive the raw WATO dict; the Password
form spec delivers the token as ("password", "value") or ("store", "id").
"""

from collections.abc import Iterator, Mapping

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
    noop_parser,
)


def _as_secret(raw: object) -> Secret:
    """Wraps the Password form spec value in a Secret for process masking.

    Password fields deliver either:
      ("password", "cleartext_token")  – direct input
      ("store",    "store_id")          – password store reference
    Any other format is converted to string and wrapped directly.
    """
    if isinstance(raw, (list, tuple)) and len(raw) == 2:
        return Secret(str(raw[1]))
    return Secret(str(raw))


def _generate_vectra_commands(
    params: Mapping[str, object],
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:

    brain_host    = str(params["brain_host"])
    no_verify_ssl = bool(params.get("no_verify_ssl", False))
    timeout       = int(params.get("timeout", 30))
    token_secret  = _as_secret(params["api_token"])

    args: list = [
        "--brain",   brain_host,
        "--token",   token_secret,
        "--timeout", str(timeout),
    ]

    if no_verify_ssl:
        args.append("--no-verify-ssl")

    yield SpecialAgentCommand(command_arguments=args)


special_agent_vectra_sensors = SpecialAgentConfig(
    name="vectra_sensors",
    parameter_parser=noop_parser,
    commands_function=_generate_vectra_commands,
)

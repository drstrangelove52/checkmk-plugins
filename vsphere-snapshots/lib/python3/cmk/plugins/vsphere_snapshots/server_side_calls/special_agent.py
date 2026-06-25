#!/usr/bin/env python3
"""Server-side calls: translate WATO parameters into CLI arguments for agent_vsphere_snapshots."""

from collections.abc import Iterator

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


def _generate_vsphere_snapshots_commands(
    params: dict, host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    assert isinstance(secret := params["password"], Secret)
    args: list = [
        "--hostname", host_config.name,
        "--user", params["user"],
        "--password", secret.unsafe(),
        "--fallback-host", params["fallback_host"],
    ]

    if "port" in params:
        args += ["--port", str(params["port"])]

    if params.get("no_ssl_verify"):
        args.append("--no-ssl-verify")

    yield SpecialAgentCommand(command_arguments=args)


special_agent_vsphere_snapshots = SpecialAgentConfig(
    name="vsphere_snapshots",
    parameter_parser=lambda params: params,
    commands_function=_generate_vsphere_snapshots_commands,
)

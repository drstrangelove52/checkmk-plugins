#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    FieldSize,
    Password,
    String,
)
from cmk.rulesets.v1.rule_specs import NotificationParameters


def _form_f24ecall() -> Dictionary:
    return Dictionary(
        title=Title("F24 eCall SMS"),
        help_text=Help(
            "Send SMS notifications via the F24 eCall HTTPS API "
            "(https://ecall-messaging.com). "
            "You need an account with username and password, "
            "and the HTTP/HTTPS API must be unlocked for your account."
        ),
        elements={
            "username": DictElement(
                parameter_form=String(
                    title=Title("User Name"),
                    help_text=Help("Your eCall account username."),
                    field_size=FieldSize.MEDIUM,
                ),
                required=True,
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Title("Password"),
                    help_text=Help("Your eCall account password."),
                ),
                required=True,
            ),
            "message_template": DictElement(
                parameter_form=String(
                    title=Title("SMS Message Template"),
                    help_text=Help(
                        "Template for the SMS text (max. 160 characters). "
                        "Use $VARIABLE$ placeholders for Checkmk notification context variables. "
                        "Available variables: "
                        "HOSTNAME, HOSTSTATE, HOSTOUTPUT, "
                        "SERVICEDESC, SERVICESTATE, SERVICEOUTPUT, "
                        "NOTIFICATIONTYPE, NOTIFICATIONCOMMENT, "
                        "CONTACTNAME, LONGDATETIME, SHORTDATETIME, WHAT."
                    ),
                    prefill=DefaultValue(
                        "$NOTIFICATIONTYPE$: $HOSTNAME$ $SERVICESTATE$$HOSTSTATE$"
                        " $SERVICEDESC$ $SERVICEOUTPUT$$HOSTOUTPUT$"
                    ),
                    field_size=FieldSize.LARGE,
                ),
                required=False,
            ),
        },
    )


rule_spec_f24ecall = NotificationParameters(
    name="f24ecall",
    title=Title("F24 eCall SMS"),
    parameter_form=_form_f24ecall,
)

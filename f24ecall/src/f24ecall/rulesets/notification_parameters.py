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
from cmk.rulesets.v1.rule_specs import NotificationParameters, Topic


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
            "host_message_template": DictElement(
                parameter_form=String(
                    title=Title("Host SMS Template"),
                    help_text=Help(
                        "Template for host notifications (max. 160 characters). "
                        "Use $VARIABLE$ placeholders. "
                        "Available: NOTIFICATIONTYPE, HOSTNAME, HOSTALIAS, HOSTADDRESS, "
                        "HOSTSTATE, HOSTOUTPUT, NOTIFICATIONCOMMENT, SHORTDATETIME."
                    ),
                    prefill=DefaultValue(
                        "$NOTIFICATIONTYPE$: $HOSTNAME$ $HOSTSTATE$ $HOSTOUTPUT$"
                    ),
                    field_size=FieldSize.LARGE,
                ),
                required=False,
            ),
            "service_message_template": DictElement(
                parameter_form=String(
                    title=Title("Service SMS Template"),
                    help_text=Help(
                        "Template for service notifications (max. 160 characters). "
                        "Use $VARIABLE$ placeholders. "
                        "Available: NOTIFICATIONTYPE, HOSTNAME, HOSTALIAS, "
                        "SERVICEDESC, SERVICESTATE, SERVICEOUTPUT, "
                        "NOTIFICATIONCOMMENT, SHORTDATETIME, CONTACTNAME."
                    ),
                    prefill=DefaultValue(
                        "$NOTIFICATIONTYPE$: $HOSTNAME$ $SERVICESTATE$"
                        " $SERVICEDESC$ $SERVICEOUTPUT$"
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
    topic=Topic.NOTIFICATIONS,
    parameter_form=_form_f24ecall,
)

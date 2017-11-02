import json
import re
import traceback
import uuid
from datetime import datetime, timedelta

import six
from disco.types.base import UNSET
from peewee import (BigIntegerField, BooleanField, DateTimeField,
                    ForeignKeyField, TextField, UUIDField)
from playhouse.postgres_ext import ArrayField, BinaryJSONField

from referee.db import BaseModel
from referee import REV


@BaseModel.register
class Command(BaseModel):
    message_id = BigIntegerField(primary_key=True)

    plugin = TextField()
    command = TextField()
    version = TextField()
    success = BooleanField()
    traceback = TextField(null=True)

    class Meta:
        db_table = 'commands'

        indexes = (
            (('success', ), False),
            (('plugin', 'command'), False),
        )

    @classmethod
    def track(cls, event, command, exception=False):
        return cls.create(
            message_id=event.message.id,
            plugin=command.plugin.name,
            command=command.name,
            version=REV,
            success=not exception,
            traceback=traceback.format_exc() if exception else None,
        )

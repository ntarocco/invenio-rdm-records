# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Base Provider."""

from invenio_pidstore.models import PersistentIdentifier, PIDStatus


class BaseClient:
    """PID Client base class."""

    def __init__(self, name, username, password, url=None, **kwargs):
        """Constructor."""
        self.name = name
        self.username = username
        self.password = password
        self.url = url


class BasePIDProvider:
    """Base Provider class."""

    name = None

    def _generate_id(self, record, **kwargs):
        """Generates an identifier value."""
        raise NotImplementedError

    def __init__(self, api_client=None, pid_type=None,
                 default_status=PIDStatus.NEW, system_managed=True,
                 required=False, **kwargs):
        """Constructor."""
        self.api_client = api_client
        self.pid_type = pid_type
        self.default_status = default_status
        self.system_managed = system_managed
        self.required = required

    def is_managed(self):
        """Returns if the PIDs from the provider are managed by the system.

        This helps differentiate external providers.
        """
        return self.system_managed

    def get(self, pid_value, pid_type=None, **kwargs):
        """Get a persistent identifier for this provider.

        :param pid_type: Persistent identifier type.)
        :param pid_value: Persistent identifier value.
        :returns: A :class:`invenio_pidstore.models.base.PersistentIdentifier`
            instance.
        """
        return PersistentIdentifier.get(pid_type or self.pid_type, pid_value,
                                        pid_provider=self.name, **kwargs)

    def create(self, pid_value=None, pid_type=None, status=None,
               object_type=None, object_uuid=None, **kwargs):
        """Create a new instance for the given type and pid.

        :param pid_value: Persistent identifier value. (Default: None).
        :param pid_type: Persistent identifier type. (Default: None).
        :param status: Status for the created PID (Default:
            :attr:`invenio_pidstore.models.PIDStatus.NEW`).
        :param object_type: The object type is a string that identify its type.
            (Default: None).
        :param object_uuid: The object UUID. (Default: None).
        :returns: A :class:`invenio_pidstore.models.PersistentIdentifier`
            instance.
        """
        pid_type = pid_type or self.pid_type
        assert pid_type

        pid_value = pid_value or self._generate_id(**kwargs)
        assert pid_value

        status = status or self.default_status
        assert status

        return PersistentIdentifier.create(
            pid_type,
            pid_value,
            pid_provider=self.name,
            object_type=object_type,
            object_uuid=object_uuid,
            status=status,
        )

    def reserve(self, pid, record, **kwargs):
        """Reserve a persistent identifier.

        This might or might not be useful depending on the service of the
        provider.
        See: :meth:`invenio_pidstore.models.PersistentIdentifier.reserve`.
        """
        is_reserved_or_registered = pid.is_reserved() or pid.is_registered()
        if not is_reserved_or_registered:
            return pid.reserve()
        return True

    def register(self, pid, record, **kwargs):
        """Register a persistent identifier.

        See: :meth:`invenio_pidstore.models.PersistentIdentifier.register`.
        """
        if not pid.is_registered():
            return pid.register()
        return True

    def update(self, pid, record, **kwargs):
        """Update information about the persistent identifier."""
        raise NotImplementedError

    def delete(self, pid, record, **kwargs):
        """Delete a persistent identifier.

        See: :meth:`invenio_pidstore.models.PersistentIdentifier.delete`.
        """
        return pid.delete()

    def get_status(self, identifier, **kwargs):
        """Get the status of the identifier."""
        return self.get(identifier, **kwargs).status

    def validate(self, identifier=None, provider=None, client=None, **kwargs):
        """Validate the attributes of the identifier."""
        if provider and provider != self.name:
            raise ValueError(f"Provider name {provider} does not "
                             f"match {self.name}")

        return True

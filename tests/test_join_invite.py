"""Tests for group join and invite-link workflows."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from telethon.errors import FloodWaitError, UserAlreadyParticipantError
from modules.join_manager import GroupJoinError, join_group
from modules.invite import InviteLinkError, create_invite_link


class JoinTests(unittest.TestCase):
    def test_public_join(self):
        client = Mock()
        client.get_entity.return_value = SimpleNamespace(title="Group", username="group")
        result = join_group(client, "@group")
        self.assertEqual(result["status"], "joined")

    def test_already_joined(self):
        client = Mock()
        client.get_entity.return_value = object()
        client.side_effect = UserAlreadyParticipantError(request=None)
        self.assertEqual(join_group(client, "group")["status"], "already_joined")

    def test_private_invite(self):
        client = Mock()
        client.return_value = SimpleNamespace(chats=[SimpleNamespace(title="Private")])
        result = join_group(client, "https://t.me/+InviteHash123")
        self.assertEqual(result["title"], "Private")

    def test_join_flood_wait(self):
        client = Mock()
        client.get_entity.return_value = object()
        client.side_effect = FloodWaitError(request=None, seconds=42)
        with self.assertRaisesRegex(GroupJoinError, "42 seconds"):
            join_group(client, "group")


class InviteTests(unittest.TestCase):
    def test_invite_link_create(self):
        client = Mock()
        client.get_entity.return_value = SimpleNamespace(title="Managed")
        client.return_value = SimpleNamespace(link="https://t.me/+generated")
        self.assertEqual(create_invite_link(client, "group")["link"], "https://t.me/+generated")

    def test_invite_flood_wait(self):
        client = Mock()
        client.get_entity.return_value = object()
        client.side_effect = FloodWaitError(request=None, seconds=13)
        with self.assertRaisesRegex(InviteLinkError, "13 seconds"):
            create_invite_link(client, "group")


if __name__ == "__main__":
    unittest.main()

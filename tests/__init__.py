import unittest

from redmine_migrator import insert_statement, update_pk_sequence_statement, update_statement


class TestHelpers(unittest.TestCase):

    def test_insert_statement(self):
        columns = ('id', 'container_id', 'container_type', 'filename')
        data = dict([(name, None) for name in columns])
        stmnt = insert_statement('attachments', columns, data)
        ref = (
            "INSERT INTO attachments (id, container_id, container_type, filename) "
            "VALUES (:id, :container_id, :container_type, :filename)"
        )
        self.assertEqual(stmnt, ref)

        del data['id']
        stmnt = insert_statement('attachments', columns, data)
        self.assertNotEqual(stmnt, ref)
        ref = (
            "INSERT INTO attachments (container_id, container_type, filename) "
            "VALUES (:container_id, :container_type, :filename)"
        )
        self.assertEqual(stmnt, ref)

    def test_update_pk_sequence_statement(self):
        stmnt = update_pk_sequence_statement('attachments', 1)
        self.assertEqual(stmnt, "ALTER SEQUENCE attachments_id_seq RESTART WITH 2")

    def test_update_statement(self):
        columns = ('id', 'container_id', 'container_type', 'filename')
        data = dict([(name, None) for name in columns])
        stmnt = update_statement('attachments', columns, data)
        ref = (
            "UPDATE attachments SET id = :id, container_id = :container_id, "
            "container_type = :container_type, filename = :filename "
            "WHERE id = :id"
        )
        self.assertEqual(stmnt, ref)

        del data['id']
        stmnt = update_statement('attachments', columns, data)
        self.assertNotEqual(stmnt, ref)
        ref = (
            "UPDATE attachments SET container_id = :container_id, "
            "container_type = :container_type, filename = :filename "
            "WHERE id = :id"
        )
        self.assertEqual(stmnt, ref)
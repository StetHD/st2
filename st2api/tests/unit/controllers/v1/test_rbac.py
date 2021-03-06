# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from st2common.rbac.types import PermissionType
from st2common.rbac.types import ResourceType
from st2common.persistence.auth import User
from st2common.persistence.rbac import Role
from st2common.persistence.rbac import UserRoleAssignment
from st2common.persistence.rbac import PermissionGrant
from st2common.models.db.auth import UserDB
from st2common.models.db.rbac import RoleDB
from st2common.models.db.rbac import UserRoleAssignmentDB
from st2common.models.db.rbac import PermissionGrantDB
from tests.base import APIControllerWithRBACTestCase


class TestRbacController(APIControllerWithRBACTestCase):
    def setUp(self):
        super(TestRbacController, self).setUp()

        permissions = [PermissionType.RULE_CREATE,
                       PermissionType.RULE_VIEW,
                       PermissionType.RULE_MODIFY,
                       PermissionType.RULE_DELETE]

        for name in permissions:
            user_db = UserDB(name=name)
            user_db = User.add_or_update(user_db)
            self.users[name] = user_db

            # Roles
            # action_create grant on parent pack
            grant_db = PermissionGrantDB(resource_uid='pack:examples',
                                         resource_type=ResourceType.PACK,
                                         permission_types=[name])
            grant_db = PermissionGrant.add_or_update(grant_db)
            grant_2_db = PermissionGrantDB(resource_uid='action:wolfpack:action-1',
                                           resource_type=ResourceType.ACTION,
                                           permission_types=[PermissionType.ACTION_EXECUTE])
            grant_2_db = PermissionGrant.add_or_update(grant_2_db)
            permission_grants = [str(grant_db.id), str(grant_2_db.id)]
            role_db = RoleDB(name=name, permission_grants=permission_grants)
            role_db = Role.add_or_update(role_db)
            self.roles[name] = role_db

            # Role assignments
            role_assignment_db = UserRoleAssignmentDB(
                user=user_db.name,
                role=role_db.name)
            UserRoleAssignment.add_or_update(role_assignment_db)

    def test_role_get_one(self):
        self.use_user(self.users['admin'])

        list_resp = self.app.get('/v1/rbac/roles')
        self.assertEqual(list_resp.status_int, 200)
        self.assertTrue(len(list_resp.json) > 0,
                        '/v1/rbac/roles did not return correct roles.')
        role_id = list_resp.json[0]['id']
        get_resp = self.app.get('/v1/rbac/roles/%s' % role_id)
        retrieved_id = get_resp.json['id']
        self.assertEqual(get_resp.status_int, 200)
        self.assertEqual(retrieved_id, role_id, '/v1/ruletypes returned incorrect ruletype.')

    def test_role_get_all(self):
        self.use_user(self.users['admin'])

        resp = self.app.get('/v1/rbac/roles')
        self.assertEqual(resp.status_int, 200)
        self.assertTrue(list(resp.json) > 0,
                        '/v1/rbac/roles did not return correct roles.')

    def test_role_get_one_fail_doesnt_exist(self):
        self.use_user(self.users['admin'])

        resp = self.app.get('/v1/rbac/roles/1', expect_errors=True)
        self.assertEqual(resp.status_int, 404)

    def test_permission_type_get_one(self):
        self.use_user(self.users['admin'])

        list_resp = self.app.get('/v1/rbac/permission_types')
        self.assertEqual(list_resp.status_int, 200)
        self.assertTrue(len(list(list_resp.json)) > 0,
                        '/v1/rbac/permission_types did not return correct permission types.')
        resource_type = list(list_resp.json)[0]
        get_resp = self.app.get('/v1/rbac/permission_types/%s' % resource_type)
        self.assertEqual(get_resp.status_int, 200)
        self.assertTrue(len(get_resp.json) > 0,
                        '/v1/rbac/permission_types did not return correct permission types.')

    def test_permission_type_get_all(self):
        self.use_user(self.users['admin'])

        resp = self.app.get('/v1/rbac/permission_types')
        self.assertEqual(resp.status_int, 200)
        self.assertTrue(len(list(resp.json)) > 0,
                        '/v1/rbac/permission_types did not return correct permission types.')

    def test_permission_type_get_one_fail_doesnt_exist(self):
        self.use_user(self.users['admin'])

        resp = self.app.get('/v1/rbac/permission_types/1', expect_errors=True)
        self.assertEqual(resp.status_int, 404)

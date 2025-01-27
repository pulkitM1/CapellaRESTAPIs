# -*- coding: utf-8 -*-
# Generic/Built-in
import logging

import json
from ..lib.CapellaAPIRequests import CapellaAPIRequests


class CommonCapellaAPI(CapellaAPIRequests):

    def __init__(self, url, secret, access, user, pwd, TOKEN_FOR_INTERNAL_SUPPORT=None):
        super(CommonCapellaAPI, self).__init__(url, secret, access)
        self.user = user
        self.pwd = pwd
        self.internal_url = url.replace("cloud", "", 1)
        self._log = logging.getLogger(__name__)
        self.perPage = 100
        self.TOKEN_FOR_INTERNAL_SUPPORT = TOKEN_FOR_INTERNAL_SUPPORT
        self.cbc_api_request_headers = {
            'Authorization': 'Bearer %s' % self.TOKEN_FOR_INTERNAL_SUPPORT,
            'Content-Type': 'application/json'
        }

    def trigger_log_collection(self, cluster_id):
        url = self.internal_url + "/internal/support/logcollections/clusters/{}".format(cluster_id)
        resp = self._urllib_request(url, "POST", params=json.dumps({}),
                                    headers=self.cbc_api_request_headers)
        return resp

    def get_cluster_tasks(self, cluster_id):
        url = self.internal_url + "/internal/support/clusters/{}/pools/default/tasks".format(cluster_id)
        resp = self._urllib_request(url, "GET",
                                    headers=self.cbc_api_request_headers)
        return resp

    def signup_user(self, full_name, email, password, tenant_name, token=None):
        """
        Invite a new user to the tenant

        Example use:

        ```
        token = "secret-token"
        resp = client.invite_user(tenant_id, user, token)
        verify_token = resp.headers["Vnd-project-Avengers-com-e2e-token"]
        user_id = resp.json()["userId"]
        ```
        """
        headers = {}
        if token:
            headers["Vnd-project-Avengers-com-e2e"] = token
        url = "{}/register".format(self.internal_url)
        body = {
            "tenant": tenant_name,
            "email": email,
            "name": full_name,
            "password": password
        }
        resp = self.do_internal_request(url, method="POST",
                                        params=json.dumps(body),
                                        headers=headers)
        return resp

    def verify_email(self, token):
        """
        Verify an email invitation.

        Example use:

        ```
        token = "email-verify-token"
        resp = client.verify_email(token)
        jwt = resp.json()["jwt"]
        ```
        """
        url = "{}/emails/verify/{}".format(self.internal_url, token)
        resp = self.do_internal_request(url, method="POST")
        return resp

    def list_accessible_tenants(self):
        """
        List tenants that are accessible to the user
        """
        url = "{}/tenants".format(self.internal_url)
        resp = self.do_internal_request(url, method="GET")
        return resp

    def create_access_secret_key(self, name, tenant_id):
        headers = {}
        url = "{}/tokens?tenantId={}".format(self.internal_url, tenant_id)
        body = {
            "name": name,
            "tenantId": tenant_id
        }
        resp = self.do_internal_request(url, method="POST",
                                        params=json.dumps(body),
                                        headers=headers)
        return resp

    def revoke_access_secret_key(self, tenant_id, key_id):
        url = "{}/tokens/{}?tenantId={}".format(self.internal_url, key_id, tenant_id)
        resp = self.do_internal_request(url, method="DELETE")
        return resp

    def create_circuit_breaker(self, cluster_id, duration_seconds = -1):
        """
        Create a deployment circuit breaker for a cluster, which prevents
        any auto-generated deployments such as auto-scaling up/down, control
        plane initiated rebalances, etc.

        Default circuit breaker duration is 24h.

        See AV-46172 for more.
        """
        url = "{}/internal/support/clusters/{}/deployments-circuit-breaker" \
              .format(self.internal_url, cluster_id)
        params = {}
        if duration_seconds > 0:
            params['timeInSeconds'] = duration_seconds
        resp = self._urllib_request(url, "POST", params=json.dumps(params),
                                    headers=self.cbc_api_request_headers)
        return resp

    def get_circuit_breaker(self, cluster_id):
        """
        Retrieve a deployment circuit breaker for a cluster.

        If circuit breaker is not set for a cluster, this returns a 404.

        See AV-46172 for more.
        """
        url = "{}/internal/support/clusters/{}/deployments-circuit-breaker" \
              .format(self.internal_url, cluster_id)
        resp = self._urllib_request(url, "GET",
                                    headers=self.cbc_api_request_headers)
        return resp

    def delete_circuit_breaker(self, cluster_id):
        """
        Delete circuit breaker for a cluster.

        See AV-46172 for more.
        """
        url = "{}/internal/support/clusters/{}/deployments-circuit-breaker" \
              .format(self.internal_url, cluster_id)
        resp = self._urllib_request(url, "DELETE",
                                    headers=self.cbc_api_request_headers)
        return resp

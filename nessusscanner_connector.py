# File: nessusscanner_connector.py
#
# Copyright (c) 2018-2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
#
#
# Phantom App imports
import sys
import time

import phantom.app as phantom
import requests
import simplejson as json
from bs4 import BeautifulSoup
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

# Imports local to this App
from nessusscanner_consts import *


class RetVal(tuple):
    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


# Define the App Class
class NessusCloudConnector(BaseConnector):
    ACTION_ID_SCAN_HOST = "scan_host"
    ACTION_ID_LIST_POLICIES = "list_policies"

    def __init__(self):
        # Call the BaseConnectors init first
        super().__init__()

    def _dump_error_log(self, error, message="Exception occurred."):
        self.error_print(message, dump_object=error)

    def _process_empty_reponse(self, response, action_result):
        if response.status_code == 200:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(action_result.set_status(phantom.APP_ERROR, "Empty response and no information in the header"), None)

    def _process_html_response(self, response, action_result):
        # An html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            error_text = soup.text
            split_lines = error_text.split("\n")
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = "\n".join(split_lines)
        except Exception as e:
            error_text = "Cannot parse error details"
            self._dump_error_log(e, "Error occurred in _process_html_response")

        message = f"Status Code: {status_code}. Data from server:\n{error_text}\n"

        message = message.replace("{", "{{").replace("}", "}}")

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):
        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            self._dump_error_log(e, "Error occurred in _process_json_response")
            return RetVal(action_result.set_status(phantom.APP_ERROR, f"Unable to parse JSON response. Error: {e!s}"), None)

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        # You should process the error returned in the json
        message = "Error from server. Status Code: {} Data from server: {}".format(r.status_code, r.text.replace("{", "{{").replace("}", "}}"))

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_response(self, r, action_result):
        # store the r_text in debug data, it will get dumped in the logs if the action fails
        if hasattr(action_result, "add_debug_data"):
            action_result.add_debug_data({"r_status_code": r.status_code})
            action_result.add_debug_data({"r_text": r.text})
            action_result.add_debug_data({"r_headers": r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        content_type = r.headers.get("Content-Type", "")

        # this service returns the JSON with the content type set
        # as text !!, so need to handle that
        if "json" in content_type or "text" in content_type:
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if "html" in content_type:
            return self._process_html_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_reponse(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {} Data from server: {}".format(
            r.status_code, r.text.replace("{", "{{").replace("}", "}}")
        )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _make_rest_call(self, endpoint, action_result, method="get", data=None, headers=None, params=None):
        resp_json = None

        headers, server, verify = self._build_request()

        url = f"{server}{endpoint}"

        try:
            request_func = getattr(requests, method)
        except AttributeError as ae:
            self._dump_error_log(ae, "Error occurred in _make_rest_call")
            return RetVal(action_result.set_status(phantom.APP_ERROR, f"Invalid method: {method}"), resp_json)

        try:
            r = request_func(url, headers=headers, json=data, params=params, verify=verify)
        except Exception as e:
            self._dump_error_log(e, "Error occurred in _make_rest_call")
            return RetVal(action_result.set_status(phantom.APP_ERROR, f"Error Connecting to server. Details: {e!s}"), resp_json)

        return self._process_response(r, action_result)

    # used to format the headers and returns where the Nessus server is
    def _build_request(self):
        config = self.get_config()

        accessKey = config.get(ACCESS_KEY)
        secretKey = config.get(SECRET_KEY)
        server = config.get(NESSUS_SERVER)

        port = config.get(LISTEN_PORT)
        verifyCert = config.get(VERIFY_CERT)

        server = f"https://{server}:{port}/"

        headers = {
            "X-ApiKeys": f"accessKey={accessKey}; secretKey={secretKey};"  # pragma: allowlist secret
        }

        return headers, server, verifyCert

    def _test_connectivity(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Attempting to get a list of users to test connectivity")

        ret_val, resp_json = self._make_rest_call("users", action_result)

        if phantom.is_fail(ret_val):
            self.save_progress("Test Connectivity Failed")
            return action_result.get_status()

        # Return success
        self.save_progress("Test Connectivity Passed")

        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_scan_host(self, param):
        self.debug_print("param", param)

        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # target to scan
        host_to_scan = param[TARGET_TO_SCAN]

        # get the id of the scan policy to use
        policy_id = param[POLICY_ID]

        # these are the options needed to create the scan launched. The scan uses the policy id and targets from
        # Phantom. The UUID does not need to be changed as it comes from the advanced scan template
        scanOptions = {
            "uuid": "ab4bacd2-05f6-425c-9d79-3ba3940ad1c24e51e1f403febe40",
            "settings": {
                "name": "Scan Launched from Phantom",
                "enabled": "true",
                "scanner_id": "1",
                "policy_id": str(policy_id),
                "text_targets": str(host_to_scan),
                "launch_now": "true",
            },
        }

        self.save_progress("Launching scan against " + str(host_to_scan))

        ret_val, running_scan_data = self._make_rest_call("scans", action_result, method="post", data=scanOptions)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # Once the scan has been launched and is running it is assigned an id which is gathered below
        scan_id = running_scan_data["scan"]["id"]

        completed = " "
        hosts = []

        # this checks every 30 seconds to see if the scan is still running.
        while completed != "completed":
            ret_val, scanStatus = self._make_rest_call(f"scans/{scan_id!s}", action_result)

            if phantom.is_fail(ret_val):
                self.save_progress("There was an error checking for the status of the scan")
                return action_result.get_status()

            completed = scanStatus["info"]

            if completed["status"] != "completed":
                self.send_progress("scan still in progress")
                time.sleep(30)
            else:
                completed = "completed"
                self.send_progress("scan completed")
                hosts = scanStatus.get("hosts", [])

        if type(hosts) != list:
            hosts = [hosts]

        for curr_item in hosts:
            action_result.add_data(curr_item)

        if hosts:
            scan_final_data = hosts[-1]
            total = scan_final_data["low"] + scan_final_data["medium"] + scan_final_data["high"] + scan_final_data["critical"]
            summary = action_result.update_summary({})
            summary["total_vulns"] = total
        else:
            return action_result.set_status(phantom.APP_ERROR, "Response is empty. Please check the input parameters.")

        return action_result.set_status(phantom.APP_SUCCESS)

    def _list_policies(self, param):
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # gets the full information for the Nessus policies
        ret_val, list_policies = self._make_rest_call("policies/", action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        policies = list_policies.get("policies", [])

        if not policies:
            policies = []

        if type(policies) != list:
            policies = [policies]

        policy_counter = 0

        for curr_item in policies:
            action_result.add_data(curr_item)
            if curr_item.get("id"):
                policy_counter = policy_counter + 1

        # creates an empty list to add the summary elements to
        summary = action_result.update_summary({})
        summary["policy_count"] = policy_counter
        action_result.set_status(phantom.APP_SUCCESS)

        return action_result.get_status()

    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if action_id == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY:
            ret_val = self._test_connectivity(param)
        elif action_id == self.ACTION_ID_SCAN_HOST:
            ret_val = self._handle_scan_host(param)
        elif action_id == self.ACTION_ID_LIST_POLICIES:
            ret_val = self._list_policies(param)

        return ret_val


if __name__ == "__main__":
    import argparse

    import pudb

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument("input_test_json", help="Input Test JSON file")
    argparser.add_argument("-u", "--username", help="username", required=False)
    argparser.add_argument("-p", "--password", help="password", required=False)
    argparser.add_argument("-v", "--verify", action="store_true", help="verify", required=False, default=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password
    verify = args.verify

    if username is not None and password is None:
        # User specified a username but not a password, so ask
        import getpass

        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = BaseConnector._get_phantom_base_url() + "login"
            print("Accessing the Login page")
            r = requests.get(login_url, verify=verify)  # nosemgrep: python.requests.best-practice.use-timeout.use-timeout
            csrftoken = r.cookies["csrftoken"]

            data = {"username": username, "password": password, "csrfmiddlewaretoken": csrftoken}
            headers = {"Cookie": f"csrftoken={csrftoken}", "Referer": login_url}

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=verify, data=data, headers=headers)
            session_id = r2.cookies["sessionid"]
        except Exception as e:
            print("Unable to get session id from the platfrom. Error: " + str(e))
            sys.exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = NessusCloudConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json["user_session_token"] = session_id
            connector._set_csrf_info(csrftoken, headers["Referer"])

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)

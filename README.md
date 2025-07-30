# Nessus

Publisher: Splunk \
Connector Version: 2.2.3 \
Product Vendor: Tenable \
Product Name: Nessus \
Minimum Product Version: 5.3.5

This app integrates with Tenable's Nessus scanner to provide endpoint-based investigative actions

Playbooks using the Nessus scanner can use the list policies first which will render a widget in
mission control of the available policies.

## Nessus Ports Requirements (Based on Standard Guidelines of [IANA ORG](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml) )

- Nessus(service) TCP(transport protocol) - 1241
- Nessus(service) UDP(transport protocol) - 1241

### Configuration variables

This table lists the configuration variables required to operate Nessus. These variables are specified when configuring a Nessus asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**nessus_server** | required | string | Nessus server IP/hostname |
**verify_server_cert** | optional | boolean | Verify server certificate |
**listen_port** | required | string | Port that the Nessus server is listening on |
**access_key** | required | password | Access Key from user's api screen |
**secret_key** | required | password | Secret Key from user's api screen |

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate the asset configuration using api tokens \
[list policies](#action-list-policies) - List the available scan policies \
[scan endpoint](#action-scan-endpoint) - Scans a host using the selected scan policy ID

## action: 'test connectivity'

Validate the asset configuration using api tokens

Type: **test** \
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

## action: 'list policies'

List the available scan policies

Type: **investigate** \
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.data.\*.creation_date | numeric | | 1500907246 |
action_result.data.\*.description | string | | |
action_result.data.\*.id | string | `nessus policy id` | 4 |
action_result.data.\*.last_modification_date | numeric | | 1500907264 |
action_result.data.\*.name | string | | Policy for basic network test - Herman |
action_result.data.\*.no_target | string | | false |
action_result.data.\*.owner | string | | admin |
action_result.data.\*.owner_id | numeric | | 2 |
action_result.data.\*.shared | numeric | | 1 |
action_result.data.\*.template_uuid | string | | 731a8e52-3ea6-a291-ec0a-d2ff0619c19d7bd788d6be818b65 |
action_result.data.\*.user_permissions | numeric | | 128 |
action_result.data.\*.visibility | string | | shared |
action_result.summary.policy_count | numeric | | 1 |
action_result.message | string | | Policy count: 1 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'scan endpoint'

Scans a host using the selected scan policy ID

Type: **investigate** \
Read only: **True**

This action requires the ID of the scan policy to be used in the scan. Note, the scan may take 10-15 minutes.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**target_to_scan** | required | IP of host to scan | string | `ip` `hostname` |
**policy_id** | required | ID of the scan policy to use | string | `nessus policy id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.policy_id | string | `nessus policy id` | 4 |
action_result.parameter.target_to_scan | string | `ip` `hostname` | 172.16.54.130 |
action_result.data.\*.critical | numeric | | 1 |
action_result.data.\*.high | numeric | | 4 |
action_result.data.\*.host_id | numeric | | 2 |
action_result.data.\*.host_index | numeric | | 0 |
action_result.data.\*.hostname | string | `ip` `host name` | 172.16.54.130 |
action_result.data.\*.info | numeric | | 71 |
action_result.data.\*.low | numeric | | 2 |
action_result.data.\*.medium | numeric | | 7 |
action_result.data.\*.numchecksconsidered | numeric | | 4139 |
action_result.data.\*.progress | string | | 4139-4139/91296-91296 |
action_result.data.\*.scanprogresscurrent | numeric | | 4139 |
action_result.data.\*.scanprogresstotal | numeric | | 4139 |
action_result.data.\*.score | numeric | | 14791 |
action_result.data.\*.severity | numeric | | 85 |
action_result.data.\*.severitycount.item.\*.count | numeric | | 71 |
action_result.data.\*.severitycount.item.\*.severitylevel | numeric | | 0 |
action_result.data.\*.totalchecksconsidered | numeric | | 4139 |
action_result.summary.total_vulns | numeric | | 14 |
action_result.message | string | | Total vulns: 14 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2025 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

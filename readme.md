[comment]: # "Auto-generated SOAR connector documentation"
# Nessus

Publisher: Splunk  
Connector Version: 2\.1\.1  
Product Vendor: Tenable  
Product Name: Nessus  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.0\.0  

This app integrates with Tenable's Nessus scanner to provide endpoint\-based investigative actions

[comment]: # ""
[comment]: # "    File: readme.md"
[comment]: # ""
[comment]: # "    Copyright (c) 2018-2021 Splunk Inc."
[comment]: # ""
[comment]: # "    Licensed under Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0.txt)"
[comment]: # ""
Playbooks using the Nessus scanner can use the list policies first which will render a widget in
mission control of the available policies.

## Nessus Ports Requirements (Based on Standard Guidelines of [IANA ORG](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml) )

-   Nessus(service) TCP(transport protocol) - 1241
-   Nessus(service) UDP(transport protocol) - 1241


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Nessus asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**nessus\_server** |  required  | string | Nessus server IP/hostname
**verify\_server\_cert** |  optional  | boolean | Verify server certificate
**listen\_port** |  required  | string | Port that the Nessus server is listening on
**placeholder** |  optional  | ph | 
**access\_key** |  required  | password | Access Key from user's api screen
**secret\_key** |  required  | password | Secret Key from user's api screen

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration using api tokens  
[list policies](#action-list-policies) - List the available scan policies  
[scan endpoint](#action-scan-endpoint) - Scans a host using the selected scan policy ID  

## action: 'test connectivity'
Validate the asset configuration using api tokens

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'list policies'
List the available scan policies

Type: **investigate**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.data\.\*\.creation\_date | numeric | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.id | string |  `nessus policy id` 
action\_result\.data\.\*\.last\_modification\_date | numeric | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.no\_target | string | 
action\_result\.data\.\*\.owner | string | 
action\_result\.data\.\*\.owner\_id | numeric | 
action\_result\.data\.\*\.shared | numeric | 
action\_result\.data\.\*\.template\_uuid | string | 
action\_result\.data\.\*\.user\_permissions | numeric | 
action\_result\.data\.\*\.visibility | string | 
action\_result\.summary\.policy\_count | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'scan endpoint'
Scans a host using the selected scan policy ID

Type: **investigate**  
Read only: **True**

This action requires the ID of the scan policy to be used in the scan\. Note, the scan may take 10\-15 minutes\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**target\_to\_scan** |  required  | IP of host to scan | string |  `ip`  `hostname` 
**policy\_id** |  required  | ID of the scan policy to use | string |  `nessus policy id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.policy\_id | string |  `nessus policy id` 
action\_result\.parameter\.target\_to\_scan | string |  `ip`  `hostname` 
action\_result\.data\.\*\.critical | numeric | 
action\_result\.data\.\*\.high | numeric | 
action\_result\.data\.\*\.host\_id | numeric | 
action\_result\.data\.\*\.host\_index | numeric | 
action\_result\.data\.\*\.hostname | string |  `ip`  `host name` 
action\_result\.data\.\*\.info | numeric | 
action\_result\.data\.\*\.low | numeric | 
action\_result\.data\.\*\.medium | numeric | 
action\_result\.data\.\*\.numchecksconsidered | numeric | 
action\_result\.data\.\*\.progress | string | 
action\_result\.data\.\*\.scanprogresscurrent | numeric | 
action\_result\.data\.\*\.scanprogresstotal | numeric | 
action\_result\.data\.\*\.score | numeric | 
action\_result\.data\.\*\.severity | numeric | 
action\_result\.data\.\*\.severitycount\.item\.\*\.count | numeric | 
action\_result\.data\.\*\.severitycount\.item\.\*\.severitylevel | numeric | 
action\_result\.data\.\*\.totalchecksconsidered | numeric | 
action\_result\.summary\.total\_vulns | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
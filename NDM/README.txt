Datadog Network Device Monitoring (NDM) Lab
SNMP + Docker-Based Simulation Environment

============================================================
OVERVIEW
============================================================

This repository provides a fully working, reproducible lab
environment for experimenting with Datadog Network Device
Monitoring (NDM) using SNMP.

The lab uses Docker Compose to spin up:
- A Datadog Agent configured for SNMP / NDM
- Multiple simulated SNMP network devices (router, switch, firewall)

The purpose of this lab is to allow anyone to quickly:
- Stand up a working NDM environment without real hardware
- Validate SNMP polling end-to-end
- Observe devices in the Datadog Network Devices UI
- Experiment with default SNMP profiles and custom profiles
- Simulate common network scenarios safely

This lab focuses on SNMP telemetry and NDM modeling, not real
packet forwarding or routing.

============================================================
HIGH-LEVEL ARCHITECTURE
============================================================

All containers run on a dedicated Docker bridge network with
static IP addresses.

- Datadog Agent
  - Container name: dd-agent-ndm-lab
  - IP: 172.28.0.10

- SNMP Router (simulated)
  - Container name: snmp-router
  - IP: 172.28.0.21
  - UDP port: 1161

- SNMP Switch (simulated)
  - Container name: snmp-switch
  - IP: 172.28.0.22
  - UDP port: 1161

- SNMP Firewall (simulated)
  - Container name: snmp-firewall
  - IP: 172.28.0.23
  - UDP port: 1161

The Datadog Agent polls each simulated device over SNMP and
publishes device metadata and metrics to Datadog NDM.

============================================================
REPOSITORY STRUCTURE
============================================================

.
├── docker-compose.yml
├── snmp/
│   ├── conf.yaml
│   └── profiles/
│       └── (custom SNMP profiles go here)
└── devices/
    ├── router/
    │   └── router.snmprec
    ├── switch/
    │   └── switch.snmprec
    └── firewall/
        └── firewall.snmprec

============================================================
FILE AND DIRECTORY EXPLANATION
============================================================

------------------------------------------------------------
docker-compose.yml
------------------------------------------------------------

Purpose:
- Orchestrates the entire lab environment

What it does:
- Starts the Datadog Agent container
- Starts one SNMP simulator container per device
- Creates a dedicated Docker network
- Assigns static IP addresses
- Mounts SNMP configs, profiles, and device recordings

Why it exists:
- Provides a one-command setup (docker compose up -d)
- Ensures consistent behavior across machines
- Avoids manual networking or SNMP configuration

------------------------------------------------------------
snmp/conf.yaml
------------------------------------------------------------

Purpose:
- Datadog Agent SNMP integration configuration

What it does:
- Defines which devices the agent should poll
- Specifies SNMP connection details
- Adds device-level tags used in Datadog

Why it exists:
- This is how the Datadog Agent discovers and polls
  network devices using explicit IPs
- Drives device creation in Datadog NDM

Important note:
- SNMP community values must match what the simulator expects

------------------------------------------------------------
snmp/profiles/
------------------------------------------------------------

Purpose:
- Holds custom Datadog SNMP profile definitions

What it does:
- Extends or overrides default SNMP profiles
- Controls which OIDs are collected
- Controls metric naming and tagging

Why it exists:
- Default profiles do not cover all devices or use cases
- Required for realistic labs and learning profile behavior

------------------------------------------------------------
devices/
------------------------------------------------------------

Purpose:
- Root directory for all simulated network devices

Why it exists:
- Keeps device simulations isolated and readable
- Makes it easy to add or remove devices

------------------------------------------------------------
devices/<device-name>/
------------------------------------------------------------

Purpose:
- Represents a single simulated network device

What it does:
- Contains exactly one SNMP recording file
- Is mounted into the corresponding simulator container

------------------------------------------------------------
SNMP RECORDING FILES (*.snmprec)
------------------------------------------------------------

Purpose:
- Define how each simulated device responds to SNMP queries

What they do:
- Provide static or semi-dynamic SNMP responses
- Control device identity, interfaces, and counters
- Serve SNMP responses for as long as the simulator is running

Important behavior:
- The SNMP simulator does not emit data autonomously
- All SNMP responses are request-driven
- By default, values are static unless variation modules are used

Community behavior:
- With snmpsim, the SNMP community is often derived from
  the basename of the .snmprec file
  Examples:
    router.snmprec   -> community "router"
    switch.snmprec   -> community "switch"

Why you would modify .snmprec files:
- Change device vendor or model (sysObjectID)
- Add or remove interfaces
- Simulate interface up/down states
- Add counters for throughput, errors, or discards
- Create more realistic NDM dashboards
- Test default vs custom profile behavior

References for modifying .snmprec files:
- snmpsim GitHub repository:
  https://github.com/etingof/snmpsim

- snmpsim data file formats (.snmprec, .snmpwalk):
  https://snmpsim.readthedocs.io/en/latest/documentation/datafiles.html

- snmpsim variation modules:
  https://snmpsim.readthedocs.io/en/latest/documentation/variation-modules.html

These resources document syntax, supported data types,
and methods for creating dynamic values.

============================================================
SIMULATING TRAFFIC & COUNTERS
============================================================

It is important to understand what "traffic" means in the
context of SNMP-based Network Device Monitoring.

------------------------------------------------------------
What is being simulated
------------------------------------------------------------

This lab simulates:
- SNMP telemetry returned by network devices
- Interface counters, status, and metadata
- Device health and availability

It does NOT simulate:
- Real packet forwarding
- Network flows
- Bandwidth at the packet level

Datadog NDM derives interface throughput and utilization
from SNMP counters, not from real traffic.

------------------------------------------------------------
Why traffic graphs may look flat initially
------------------------------------------------------------

SNMP recording files are static by default.

If counters such as ifInOctets or ifOutOctets do not change
between polls, Datadog will correctly calculate a rate of zero.

This is expected behavior.

------------------------------------------------------------
How SNMP "traffic" is generated
------------------------------------------------------------

SNMP traffic in this lab is entirely request-driven:

- Datadog Agent polls devices on an interval
- snmpsim responds using values from .snmprec files
- Datadog calculates rates from successive counter values

The simulator itself does not generate traffic or metrics.

------------------------------------------------------------
Ways to simulate more activity
------------------------------------------------------------

There are three main approaches, depending on your goal:

1) Increase SNMP polling activity
   - Add more simulated devices
   - Add more interfaces or OIDs
   - Collect richer tables via profiles
   - Poll more frequently

2) Simulate interface throughput
   - Include interface counter OIDs in .snmprec files
   - Use snmpsim variation modules to make counters increase
     over time (recommended approach)

3) Simulate device or interface instability
   - Change interface status values
   - Restart simulator containers
   - Modify .snmprec values and reload the simulator

------------------------------------------------------------
Recommended approach for realistic NDM graphs
------------------------------------------------------------

For realistic bandwidth and utilization charts:
- Ensure interface octet counters exist
- Use snmpsim variation modules to increment counters
- Allow Datadog to compute rates from those changes

This produces stable, realistic-looking NDM graphs while
remaining fully deterministic and reproducible.

============================================================
TYPICAL WORKFLOW
============================================================

1. Start the lab using Docker Compose
2. Verify SNMP responses using snmpwalk
3. Run "agent check snmp" to confirm polling
4. Observe devices in Datadog NDM
5. Modify SNMP recordings or profiles
6. Restart only the affected containers
7. Observe changes in the UI

============================================================
WHAT THIS LAB IS GOOD FOR
============================================================

- Learning Datadog NDM fundamentals
- Understanding SNMP profile selection
- Testing custom profiles safely
- Simulating failures and state changes
- Demos, onboarding, and enablement

============================================================
WHAT THIS LAB IS NOT
============================================================

- A packet-level traffic simulator
- A routing or switching emulator
- A performance benchmark tool

============================================================
CLEANUP
============================================================

To stop and remove all containers:

docker compose down --remove-orphans

============================================================
NEXT STEPS
============================================================

Once comfortable with the base setup:
- Experiment with default profile matching
- Create and apply custom SNMP profiles
- Simulate traffic, errors, and outages
- Extend the lab with additional devices


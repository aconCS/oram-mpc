# Network emulation

The network emulator creates three isolated network namespaces for the MPC
parties. Each party has its own virtual interface and IP address, and traffic
between them passes through a virtual bridge.

This makes it possible to test the MPC setup under network conditions such as
latency, jitter, packet loss and bandwidth limits.

## Network setup

| Party | Namespace | IP address |
|---|---|---|
| 0 | mpc0 | 10.10.0.10 |
| 1 | mpc1 | 10.10.0.11 |
| 2 | mpc2 | 10.10.0.12 |

The namespaces are connected through a Linux bridge. Traffic control (`tc`)
is used on each party's interface to apply network conditions.

## Commands

Network conditions can be set for an individual party:

```bash
sudo .venv/bin/python -m network.cli set --party 1 --latency 50
```

The current traffic control configuration can be checked with:

```bash
sudo .venv/bin/python -m network.cli status
```

## Testing

Connectivity was tested by pinging between parties:

```bash
sudo ip netns exec mpc0 ping -c 5 10.10.0.11
sudo ip netns exec mpc1 ping -c 5 10.10.0.10
```

Latency was tested by adding a 50 ms delay to Party 1. The round trip time
between Party 0 and Party 1 increased to roughly 50 ms in both directions.

When a 50 ms delay was applied to both Party 0 and Party 1, the round trip
time increased to roughly 100 ms. This confirmed that delays from both
parties are added together across the round trip.

Jitter, packet loss and bandwidth limits were also tested. The 10 Mbps
bandwidth limit was verified using `iperf3`, with one party acting as the
server and another as the client.

Combined conditions were tested by applying latency, jitter, packet loss and
bandwidth limits at the same time. Invalid values were also tested and were
rejected by the CLI.

## Reset and teardown

Traffic shaping can be removed with:

```bash
sudo .venv/bin/python -m network.cli reset
```

After resetting, all parties showed `noqueue`, confirming the traffic shaping
rules had been removed.

The network can be removed with:

```bash
sudo .venv/bin/python -m network.cli teardown
```

After teardown, no `mpc*` namespaces or interfaces remained.
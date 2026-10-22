"""Per-party cost metrics for MPyC programs: time, bytes, messages, rounds, memory.

Bytes come from MPyC's own counter (MessageExchanger.nbytes_sent, which
includes MPyC's 12 byte message header).

Rounds are counted with a Lamport clock: every outgoing message carries the
sender's clock as a 4 byte stamp, and receiving a message stamped s moves the
local clock to max(clock, s + 1). The clock then equals the length of the
longest chain of messages that had to wait on each other, i.e. the number of
sequential communication rounds. The stamp is stripped on receipt and not
counted in the byte totals.

Memory is the peak Python heap (tracemalloc) while the operation runs.
tracemalloc slows Python down, so turn it off when you only care about time.
"""
import struct
import time
import tracemalloc

from mpyc.asyncoro import MessageExchanger
from mpyc.runtime import mpc

_STAMP = struct.Struct('<I')

clock = 0       # Lamport clock of this party = rounds so far
messages = 0    # messages sent by this party

_orig_send = MessageExchanger.send
_orig_receive = MessageExchanger.receive


def _send(self, pc, payload):
    global messages
    _orig_send(self, pc, _STAMP.pack(clock) + payload)
    self.nbytes_sent -= _STAMP.size
    messages += 1


def _unstamp(payload):
    global clock
    s, = _STAMP.unpack_from(payload)
    clock = max(clock, s + 1)
    return payload[_STAMP.size:]


def _receive(self, pc):
    payload = _orig_receive(self, pc)
    if isinstance(payload, bytes):
        return _unstamp(payload)

    out = self.runtime._loop.create_future()
    payload.add_done_callback(lambda f: out.set_result(_unstamp(f.result())))
    return out


def install():
    """Patch MPyC's message layer. Must run on every party, before mpc.start()."""
    MessageExchanger.send = _send
    MessageExchanger.receive = _receive


def bytes_sent():
    return sum(p.protocol.nbytes_sent for p in mpc.parties if p.pid != mpc.pid)


class Measure:
    """Measure one operation on this party.

        async with Measure() as m:
            await mpc.gather(op(...))
        m.stats -> {'time', 'bytes', 'messages', 'rounds', 'peak_mem'}

    All parties should enter and leave together; Measure synchronises them on
    entry so rounds of earlier work don't leak into this measurement.
    """

    def __init__(self, memory=True):
        self.memory = memory
        self.stats = None

    async def __aenter__(self):
        global clock
        await mpc.transfer(None)   # sync point, excluded from the stats below
        clock = 0
        self._bytes, self._msgs = bytes_sent(), messages
        if self.memory:
            tracemalloc.start()
            self._mem0 = tracemalloc.get_traced_memory()[0]
        self._t0 = time.perf_counter()
        return self

    async def __aexit__(self, *exc):
        elapsed = time.perf_counter() - self._t0
        peak = 0
        if self.memory:
            peak = tracemalloc.get_traced_memory()[1] - self._mem0
            tracemalloc.stop()
        self.stats = {
            'time': elapsed,
            'bytes': bytes_sent() - self._bytes,
            'messages': messages - self._msgs,
            'rounds': clock,
            'peak_mem': peak,
        }
        return False


async def combine(stats):
    """Collect every party's stats; returns the totals over all parties.

    bytes/messages are summed, time/rounds/peak_mem are the max over parties.
    """
    per_party = await mpc.transfer(stats)
    return {
        'time': max(s['time'] for s in per_party),
        'bytes': sum(s['bytes'] for s in per_party),
        'messages': sum(s['messages'] for s in per_party),
        'rounds': max(s['rounds'] for s in per_party),
        'peak_mem': max(s['peak_mem'] for s in per_party),
    }

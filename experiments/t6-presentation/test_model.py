import itertools
import unittest
from dataclasses import replace
from model import (Authority, Viewer, Packet, MODES, transition, can_write,
                   admitted, snapshot, follow, unfollow, navigate, receive)


class PresentationResearch(unittest.TestCase):
    def setUp(self):
        self.a, _ = transition(Authority(), 0, control_allowed=True, presenter='alice')
        self.p = Packet(self.a.scope, self.a.epoch, 'alice', 0, (10, 20, 2))
        self.v = follow(Viewer(self.a))

    def test_all_modes_and_trusted_write_inputs_are_independent_of_presenter(self):
        for mode, allowed, valid, scoped, presenter in itertools.product(
                MODES, (False, True), (False, True), (False, True), (None, 'alice')):
            a = replace(self.a, mode=mode, presenter=presenter)
            self.assertEqual(can_write(a, current_t2_write_allowed=allowed,
                                      session_valid=valid, scope_matches=scoped),
                             allowed and valid and scoped and mode != 'locked')

    def test_follow_never_changes_authority_or_personal_view(self):
        v = receive(self.v, self.p)
        self.assertEqual(v.authority, self.a)
        self.assertEqual(v.personal, (0, 0, 1))
        self.assertEqual(unfollow(v).displayed, (0, 0, 1))
        self.assertEqual(follow(v), v)

    def test_navigation_exits_follow_and_rejoin_restores_latest_personal_view(self):
        v = navigate(receive(self.v, self.p), (33, 44, 3))
        self.assertFalse(v.following)
        self.assertEqual(receive(v, replace(self.p, sequence=1)), v)
        v = receive(follow(v), replace(self.p, sequence=1))
        self.assertEqual(unfollow(v).displayed, (33, 44, 3))

    def test_revocation_and_same_presenter_aba_counterexample(self):
        # Alice -> none -> Alice: user-ID-only acceptance wrongly accepts old seq99.
        revoked, _ = transition(self.a, 1, control_allowed=True)
        renewed, _ = transition(revoked, 2, control_allowed=True, presenter='alice')
        old = replace(self.p, sequence=99)
        self.assertEqual(old.sender, renewed.presenter)  # naive gate accepts
        self.assertFalse(admitted(renewed, old, session_valid=True, read_allowed=True))
        v = follow(snapshot(self.v, renewed))
        self.assertEqual(receive(v, old), v)
        new = replace(self.p, epoch=renewed.epoch)
        self.assertEqual(receive(v, new).displayed, new.view)

    def test_each_invalid_publication_is_side_effect_free(self):
        bad = [replace(self.p, scope=('guild-b', 'board-a')),
               replace(self.p, scope=('guild-a', 'board-b')),
               replace(self.p, epoch=True), replace(self.p, epoch=0),
               replace(self.p, sender='mallory'), replace(self.p, sequence=True),
               replace(self.p, sequence=-1), replace(self.p, sequence=2**53),
               *[replace(self.p, view=v) for v in
                 [(float('nan'), 0, 1), (0, float('inf'), 1), (0, 0, 0),
                  (0, 0, 11), (1_000_001, 0, 1), (True, 0, 1), (0, 1)]]]
        for packet in bad:
            self.assertFalse(admitted(self.a, packet, session_valid=True, read_allowed=True))
            self.assertEqual(receive(self.v, packet), self.v)
        for valid, read in [(False, True), (True, False), (False, False)]:
            self.assertFalse(admitted(self.a, self.p, session_valid=valid, read_allowed=read))

    def test_reordered_and_duplicate_packets_converge_without_rewind(self):
        packets = [replace(self.p, sequence=i, view=(i, i, 1)) for i in range(4)]
        for order in itertools.permutations(packets):
            v = self.v
            for packet in order + order:
                before = v.sequence
                v = receive(v, packet)
                self.assertGreaterEqual(v.sequence, before)
            self.assertEqual(v.displayed, (3, 3, 1))

    def test_concurrent_mode_and_presenter_cas_has_one_winner(self):
        changes = [dict(mode='locked'), dict(presenter='bob')]
        for order in itertools.permutations(changes):
            a = self.a
            results = []
            for change in order:
                a, result = transition(a, 1, control_allowed=True, **change)
                results.append(result)
            self.assertEqual(results, ['ok', 'stale-revision'])
            self.assertEqual(a.revision, 2)
            self.assertEqual(a.epoch, 2)

    def test_mode_transition_revokes_stream_and_reconnect_requires_rejoin(self):
        a, _ = transition(self.a, 1, control_allowed=True, mode='open')
        self.assertIsNone(a.presenter)
        v = snapshot(receive(self.v, self.p), a)
        self.assertFalse(v.following)
        self.assertEqual(v.displayed, v.personal)
        self.assertEqual(follow(v), v)
        self.assertEqual(snapshot(v, self.a), v)
        reconnect = snapshot(receive(self.v, self.p), self.a)
        self.assertFalse(reconnect.following)
        other = snapshot(self.v, replace(self.a, scope=('g2', 'b2')))
        self.assertEqual(other.personal, (0, 0, 1))
        self.assertEqual(receive(follow(other), self.p), follow(other))

    def test_invalid_control_has_no_effect(self):
        for kw, expected in [({'control_allowed': False}, 'forbidden'),
                              ({'control_allowed': True, 'mode': 'presentation'}, 'invalid'),
                              ({'control_allowed': True, 'presenter': ''}, 'invalid')]:
            self.assertEqual(transition(self.a, 1, **kw), (self.a, expected))
        self.assertEqual(transition(self.a, 0, control_allowed=True), (self.a, 'stale-revision'))
        self.assertEqual(transition(self.a, True, control_allowed=True), (self.a, 'stale-revision'))

    def test_huge_integer_viewports_are_rejected_without_overflow(self):
        for axis in range(3):
            for huge in (10**400, -(10**400)):
                view = [0, 0, 1]
                view[axis] = huge
                packet = replace(self.p, view=tuple(view))
                self.assertFalse(admitted(self.a, packet, session_valid=True, read_allowed=True))
                self.assertEqual(receive(self.v, packet), self.v)
                self.assertEqual(navigate(self.v, tuple(view)), self.v)

    def test_same_stream_reconnect_preserves_watermark(self):
        v = receive(self.v, replace(self.p, sequence=10, view=(10, 10, 1)))
        rejoined = follow(snapshot(v, self.a))
        self.assertEqual(rejoined.sequence, 10)
        # Previously snapshot reset sequence=-1 and accepted delayed seq1.
        old = replace(self.p, sequence=1, view=(1, 1, 1))
        self.assertEqual(receive(rejoined, old), rejoined)
        self.assertEqual(receive(rejoined, replace(old, sequence=10)), rejoined)
        self.assertEqual(receive(rejoined, replace(old, sequence=11)).sequence, 11)
        renewed, _ = transition(self.a, 1, control_allowed=True, presenter='alice')
        fresh = follow(snapshot(v, renewed))
        self.assertEqual(fresh.sequence, -1)
        self.assertEqual(receive(fresh, replace(self.p, epoch=renewed.epoch)).sequence, 0)

    def test_naive_follow_snapshot_overwrites_personal_counterexample(self):
        displayed = receive(self.v, self.p)
        naive_personal_on_second_follow = displayed.displayed
        self.assertNotEqual(naive_personal_on_second_follow, displayed.personal)
        self.assertEqual(unfollow(follow(displayed)).displayed, (0, 0, 1))


if __name__ == '__main__':
    unittest.main()

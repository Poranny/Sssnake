def test_hit_wall_true(collision_checker, full_state):
    thresh = collision_checker.wall_hit_distance

    full_state.head_position = (thresh / 2, full_state.map_size / 2)
    assert collision_checker.hit_wall(full_state)

def test_hit_wall_false(collision_checker, full_state):
    thresh = collision_checker.wall_hit_distance
    ms = full_state.map_size

    full_state.head_position = (thresh * 2, ms / 2)
    assert not collision_checker.hit_wall(full_state)

def test_hit_tail_true(collision_checker, full_state):
    thresh = collision_checker.tail_hit_distance
    full_state.head_position = (0.0, 0.0)
    full_state.segments_positions = [(thresh / 2, 0.0)]
    assert collision_checker.hit_tail(full_state)

def test_hit_tail_false(collision_checker, full_state):
    thresh = collision_checker.tail_hit_distance
    full_state.head_position = (0.0, 0.0)
    full_state.segments_positions = [(thresh * 2, 0.0)]
    assert not collision_checker.hit_tail(full_state)

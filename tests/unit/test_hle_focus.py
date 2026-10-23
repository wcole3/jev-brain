from scripts import hle_focus


def meta_row(cid, group, i):
    return {"id": f"{cid}:{group}:{i}", "meta": {"catalog_id": cid, "group_id": group}}


def synthetic():
    hle = [meta_row(hle_focus.HLE, i, 0) for i in range(100)]
    ranking = [meta_row(1, g, i) for g in range(40) for i in range(3)]  # linked groups of 3
    single = [meta_row(4, g, 0) for g in range(60)]
    out_of_index = [meta_row(24, g, 0) for g in range(60)]
    return hle + ranking + single + out_of_index


def test_hle_share_holds_and_out_of_index_benchmarks_are_left_out():
    meta = synthetic()
    q, ids = hle_focus.hle_focus(meta, [m["id"] for m in meta])
    hle = sum(i.startswith(f"{hle_focus.HLE}:") for i in ids)
    assert hle == 100 and hle / len(ids) >= hle_focus.MIN_HLE_SHARE
    assert not any(i.startswith("24:") for i in ids)
    bigger = hle_focus.hle_share(100, {c: hle_focus.pick_groups(g, q + 1) for c, g in hle_focus.others(meta, [m["id"] for m in meta]).items()})
    assert bigger < hle_focus.MIN_HLE_SHARE


def test_groups_stay_whole():
    meta = synthetic()
    _, ids = hle_focus.hle_focus(meta, [m["id"] for m in meta])
    chosen = {i.rsplit(":", 1)[0] for i in ids if i.startswith("1:")}
    assert all(sum(i.startswith(g + ":") for i in ids) == 3 for g in chosen)


def test_only_dev_rows_and_deterministic():
    meta = synthetic()
    dev = [m["id"] for m in meta if m["meta"]["catalog_id"] != 4 or m["meta"]["group_id"] < 30]
    a = hle_focus.hle_focus(meta, dev)
    assert a == hle_focus.hle_focus(list(reversed(meta)), dev)
    assert all(int(i.split(":")[1]) < 30 for i in a[1] if i.startswith("4:"))

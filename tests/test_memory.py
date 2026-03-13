from app.memory import SessionMemory


def test_memory_roundtrip(tmp_path):
    db = tmp_path / "mem.db"
    mem = SessionMemory(str(db))

    mem.add_scenario("frame", {"toolset": "Cisco", "recommended_action": "show ip int brief"})
    mem.add_attempt("show ip int brief", "interface down/down")

    ctx = mem.recent_context(limit=5)
    assert len(ctx["scenarios"]) == 1
    assert len(ctx["attempts"]) == 1
    assert ctx["scenarios"][0]["suggestion"]["toolset"] == "Cisco"

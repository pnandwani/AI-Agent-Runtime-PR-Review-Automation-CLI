from agent_pr_reviewer.gitops import parse_unified_diff


def test_parse_unified_diff_collects_added_lines() -> None:
    diff_text = """diff --git a/example.py b/example.py
index 1111111..2222222 100644
--- a/example.py
+++ b/example.py
@@ -1,0 +1,3 @@
+print("hello")
+value = 1
+# TODO remove debug
"""
    files = parse_unified_diff(diff_text)
    assert len(files) == 1
    assert files[0].path == "example.py"
    assert files[0].added_lines == [1, 2, 3]

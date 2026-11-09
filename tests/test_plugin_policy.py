import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def all_hooks():
    config = json.loads((ROOT / "hooks" / "hooks.json").read_text())
    return [h for groups in config["hooks"].values() for group in groups for h in group["hooks"]]


def shipped_files():
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / f for f in tracked.splitlines() if not f.startswith("tests/")]


def test_plugin_ships_no_command_hooks():
    assert all_hooks()
    assert all(h["type"] == "prompt" for h in all_hooks())


def test_prompt_hook_gets_input_and_has_no_stray_dollar():
    for h in all_hooks():
        assert "$ARGUMENTS" in h["prompt"]
        assert re.findall(r"(?<!\\)\$\w*", h["prompt"]) == ["$ARGUMENTS"]


def test_no_preapproved_shell_access():
    for path in list((ROOT / "commands").glob("*.md")) + list((ROOT / "agents").glob("*.md")):
        assert "Bash" not in path.read_text().split("---")[1], path.name


def test_manifest_version_matches_skill():
    version = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]
    skill = (ROOT / "skills" / "auto-test" / "SKILL.md").read_text()
    assert f"version: {version}" in skill


def test_no_executable_code_shipped():
    assert [p.name for p in shipped_files() if p.suffix in {".py", ".sh", ".js", ".rb", ".ts"}] == []


def test_no_credential_or_env_references():
    pattern = re.compile(
        r"os\.environ|getenv|process\.env|\.env\b|database\.yml|DATABASE_URL|API_KEY|_TOKEN\b"
        r"|credential|password|secret|\$\{user_config|DISABLE_TEST_REMINDER",
        re.I,
    )
    offenders = [p.name for p in shipped_files() if pattern.search(p.read_text(errors="ignore"))]
    assert offenders == []


def test_no_network_or_file_access_references():
    fetchers = ["cu" "rl ", "wg" "et ", "np" "x "]
    pattern = re.compile(r"https?://|" + "|".join(fetchers) + r"|urllib|requests\.|socket|fetch\(|open\(")
    offenders = [p.name for p in shipped_files() if p.name != "plugin.json" and p.suffix != ".svg" and pattern.search(p.read_text(errors="ignore"))]
    assert offenders == []


def test_prompt_hook_is_non_blocking_with_escape_hatch():
    for h in all_hooks():
        assert h["continueOnBlock"] is True
        assert "test-generator: skip" in h["prompt"]


def test_agent_and_command_tools_exclude_shell():
    allowed = {"Read", "Glob", "Grep", "Write"}
    for path in list((ROOT / "commands").glob("*.md")) + list((ROOT / "agents").glob("*.md")):
        front = path.read_text().split("---")[1]
        tools = re.search(r"(?:allowed-tools|tools):\s*\[?([^\]\n]*)", front).group(1)
        assert {t.strip().split("(")[0] for t in tools.split(",")} <= allowed, path.name


def test_command_write_grants_are_scoped_to_test_files():
    front = (ROOT / "commands" / "generate-tests.md").read_text().split("---")[1]
    tools = [t.strip() for t in re.search(r"allowed-tools:\s*\[([^\]]*)", front).group(1).split(",")]
    writes = [t for t in tools if t.startswith("Write")]
    assert writes
    assert all(re.fullmatch(r"Write\([^)]+\)", t) for t in writes), writes


def test_agent_uses_tools_key():
    front = (ROOT / "agents" / "test-writer.md").read_text().split("---")[1]
    assert re.search(r"^tools:", front, re.M)
    assert "allowed-tools" not in front


def test_command_receives_arguments():
    text = (ROOT / "commands" / "generate-tests.md").read_text()
    assert "$ARGUMENTS" in text and "argument-hint:" in text.split("---")[1]


def test_manifest_has_required_fields():
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    for key in ("name", "description", "version", "author", "homepage", "repository", "license", "keywords", "icon"):
        assert manifest.get(key), key
    assert manifest["version"] == "1.1.0"
    assert (ROOT / manifest["icon"]).is_file()


def test_no_root_claude_md():
    assert not (ROOT / "CLAUDE.md").exists()


def test_skill_references_exist():
    skill = (ROOT / "skills" / "auto-test" / "SKILL.md").read_text()
    names = re.findall(r"references/([\w-]+\.md)", skill)
    assert names
    for name in names:
        assert (ROOT / "skills" / "auto-test" / "references" / name).is_file(), name


def test_docs_have_no_em_or_en_dashes():
    for path in ROOT.rglob("*.md"):
        text = path.read_text()
        assert "\u2014" not in text and "\u2013" not in text, path.name

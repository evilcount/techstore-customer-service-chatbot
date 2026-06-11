import subprocess
import sys


def test_requests_rag_cli_help_runs_from_project_root():
    result = subprocess.run(
        [sys.executable, "scripts/requests_rag_chatbot.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "RAG chatbot over the official Requests" in result.stdout

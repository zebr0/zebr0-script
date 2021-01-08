import datetime
import io

import pytest
import zebr0

import zebr0_script


@pytest.fixture(scope="module")
def server():
    with zebr0.TestServer() as server:
        yield server


def format_mtime(path):
    return datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime("%c")


def test_ok(server, tmp_path, capsys, monkeypatch):
    server.data = {"script": ["echo one", "sleep 1 && echo two"]}

    configuration_file = tmp_path.joinpath("zebr0.conf")
    zebr0.Client("http://127.0.0.1:8000", ["lorem", "ipsum"], 1).save_configuration(configuration_file)
    reports_path = tmp_path.joinpath("reports")

    zebr0_script.main(["-r", str(reports_path), "log"])
    assert capsys.readouterr().out == ""

    zebr0_script.main(["-f", str(configuration_file), "-r", str(reports_path), "show"])
    assert capsys.readouterr().out == 'pending: "echo one"\npending: "sleep 1 && echo two"\n'

    monkeypatch.setattr("sys.stdin", io.StringIO("e\nn\nq\n"))
    zebr0_script.main(["-f", str(configuration_file), "-r", str(reports_path), "debug"])
    assert capsys.readouterr().out == 'next: "echo one"\n(e)xecute, (s)kip, or (q)uit?\n.\nsuccess!\nwrite report? (y)es or (n)o\nnext: "sleep 1 && echo two"\n(e)xecute, (s)kip, or (q)uit?\n'

    zebr0_script.main(["-f", str(configuration_file), "-r", str(reports_path), "run"])
    assert capsys.readouterr().out == 'executing: "echo one"\n.\nsuccess!\nexecuting: "sleep 1 && echo two"\n.\nsuccess!\n'

    report1_date = format_mtime(reports_path.joinpath("a885d7b3306acd60490834d5fdd234b5"))
    report2_date = format_mtime(reports_path.joinpath("7ab9b46af97310796a1918713345d986"))

    zebr0_script.main(["-r", str(reports_path), "log"])
    assert capsys.readouterr().out == "a885d7b3306acd60490834d5fdd234b5 " + report1_date + ' {"command": "echo one", "status": "success"}\n7ab9b46af97310796a1918713345d986 ' + report2_date + ' {"command": "sleep 1 && echo two", "status": "success"}\n'

    zebr0_script.main(["-f", str(configuration_file), "-r", str(reports_path), "show"])
    assert capsys.readouterr().out == 'success: "echo one"\nsuccess: "sleep 1 && echo two"\n'

    zebr0_script.main(["-f", str(configuration_file), "-r", str(reports_path), "run"])
    assert capsys.readouterr().out == 'skipping: "echo one"\nskipping: "sleep 1 && echo two"\n'

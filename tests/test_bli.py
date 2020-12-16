import tempfile
from pathlib import Path

import pytest

import zebr0
import zebr0_script


@pytest.fixture(scope="module")
def server():
    with zebr0.TestServer() as server:
        yield server


def test_execute_command():
    with tempfile.TemporaryDirectory() as tmp:
        assert zebr0_script.execute_command("touch {}/test".format(tmp))
        assert Path(tmp).joinpath("test").is_file()
        assert not zebr0_script.execute_command("false")
        # with popen used like that, it's impossible to test stdout


def test_execute(monkeypatch, capsys):
    def fake_execute_command(_):
        print("ok")
        return True

    monkeypatch.setattr(zebr0_script, "execute_command", fake_execute_command)

    with tempfile.TemporaryDirectory() as tmp:
        zebr0_script.execute("dummy", Path(tmp).joinpath("test"))
        assert capsys.readouterr().out == "ok\ndone\n"


def test_execute_ko(monkeypatch, capsys):
    def fake_execute_command(_):
        print("ko")
        return False

    monkeypatch.setattr(zebr0_script, "execute_command", fake_execute_command)

    with tempfile.TemporaryDirectory() as tmp:
        zebr0_script.execute("dummy", Path(tmp).joinpath("test"), 5, 0.1)
        assert capsys.readouterr().out == "ko\nretrying\nko\nretrying\nko\nretrying\nko\nretrying\nko\nerror\n"


def test_execute_ko_then_ok(monkeypatch, capsys):
    trick = {}

    def fake_execute_command(_):
        trick["count"] = trick.get("count", 0) + 1
        return trick.get("count") == 3

    monkeypatch.setattr(zebr0_script, "execute_command", fake_execute_command)

    with tempfile.TemporaryDirectory() as tmp:
        zebr0_script.execute("dummy", Path(tmp).joinpath("test"), 3, 0.1)
        assert capsys.readouterr().out == "retrying\nretrying\ndone\n"


def test_lookup(server, capsys):
    server.data = {"data": "dummy\n"}

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        client = zebr0.Client("http://localhost:8000", configuration_file=Path(""))

        testfile = tmp.joinpath("many/directories/test")
        historyfile = tmp.joinpath("history")
        sdfsdf = {"lookup": "data", "path": testfile}

        zebr0_script.lookup(sdfsdf, historyfile, client)

        assert testfile.read_text() == "dummy\n"
        assert historyfile.read_text() == str(sdfsdf)
        assert capsys.readouterr().out == "done\n"


def test_recursive_lookup2(server, capsys):
    server.data = {"script": ["install package xxx",
                              {"lookup": "configuration-file", "path": "/etc/xxx/conf.ini"},
                              "chmod 400 /etc/xxx/conf.ini",
                              {"include": "second-script"},
                              {"make-coffee": "black"}],
                   "second-script": ["install package yyy",
                                     "yyy configure network"]}

    client = zebr0.Client("http://localhost:8000", configuration_file=Path(""))
    result = zebr0_script.recursive_lookup2("script", Path("/tmp"), client)
    assert list(result) == [("install package xxx", Path("/tmp/edd85cad01d197aa80d9edcbfce9a575")),
                            ({"lookup": "configuration-file", "path": "/etc/xxx/conf.ini"}, Path("/tmp/b61788ba0623fc4d9114699ab00d8bf7")),
                            ("chmod 400 /etc/xxx/conf.ini", Path("/tmp/df6218e3bf04bcfe1670d1009b08dcbf")),
                            ("install package yyy", Path("/tmp/fdeb9fb70de466a3975f25725c897913")),
                            ("yyy configure network", Path("/tmp/c39b670739e8ece59c0f53b6b1b0dfb3"))]
    assert capsys.readouterr().out == "unknown command, ignored: {'make-coffee': 'black'}\n"

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from cryptography.fernet import Fernet
from . import server


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        for p in [patch.object(server, "DATA", Path(temp.name)),
                  patch.object(server, "cipher", Fernet(Fernet.generate_key())),
                  patch.dict(os.environ, {"OPENAI_API_KEY": ""})]:
            p.start()
            self.addCleanup(p.stop)
        self.api = TestClient(server.app)
        server.initialize()
        self.headers = {"Authorization": "Bearer " + server.TOKEN.decode()}

    def test_vault_versions_and_protection(self):
        self.assertEqual(self.api.get("/api/state").status_code, 401)
        self.assertEqual(self.api.get("/access").status_code, 404)
        box = dict(v=1, salt="salt", iv="iv", data="encrypted")
        body = dict(rev=0, box=box)
        self.assertEqual(self.api.post("/api/state",json=body,headers=self.headers).json(), {"rev":1})
        self.assertEqual(self.api.post("/api/state",json=body,headers=self.headers).status_code,409)
        self.assertEqual(self.api.get("/api/state",headers=self.headers).json()["box"],box)

    def test_worker_deduplication_recovery_and_output(self):
        payload = dict(role="العقل المركزي",context="synthetic question")
        def submit():
            return self.api.post("/api/jobs",json=payload,headers=self.headers)
        self.assertEqual(submit().status_code,503)
        with patch.dict(os.environ, {"OPENAI_API_KEY":"fixture"}):
            key=submit().json()["id"]
            self.assertEqual(key,submit().json()["id"])
        with server.closing(server.connect()) as c,c:
            c.execute("UPDATE jobs SET state='running'")
        server.initialize()
        self.assertTrue(server.work_once(lambda x:"draft for "+x["context"]))
        self.assertFalse(server.work_once(lambda x:"duplicate"))
        result=self.api.get("/api/jobs/"+key,headers=self.headers).json()
        self.assertEqual(result,dict(state="done",result="draft for synthetic question"))
        self.assertNotIn(b"synthetic question",(server.DATA/"center.sqlite").read_bytes())


if __name__ == "__main__":
    unittest.main()

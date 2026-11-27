import importlib.util,json,sys,unittest,zipfile
from pathlib import Path
import httpx,yaml
PLUGIN = Path(__file__).resolve().parents[1] / 'saiarung27' / 'sealgraf'
sys.path.insert(0,str(PLUGIN))
from sealgraf_client import SealgrafClient,SealgrafError,SealgrafApiError
class Activation(unittest.TestCase):
    def client(self, handler):
        return SealgrafClient('https://sealgraf.com','synthetic-test-key',transport=httpx.MockTransport(handler))
    def test_success_is_setup_only(self):
        seen=[]
        def handle(r):
            seen.append((r.method,r.url.path,json.loads(r.content)))
            return httpx.Response(200,json={'ok':True,'credential_accepted':True})
        self.client(handle).validate_key()
        self.assertEqual(seen,[('POST','/v1/integrations/validate',{'integration_id':'dify'})])
    def test_legacy_server_fallback(self):
        seen=[]
        def handle(r):
            seen.append(r.url.path)
            return httpx.Response(404,json={}) if len(seen)==1 else httpx.Response(200,json={'items':[]})
        self.client(handle).validate_key()
        self.assertEqual(seen,['/v1/integrations/validate','/v1/receipts'])
    def test_failures_do_not_fallback(self):
        for status in (401,403,429,500):
            seen=[]
            def handle(r):
                seen.append(r.url.path)
                return httpx.Response(status,json={'detail':'rejected'})
            with self.assertRaises(SealgrafApiError): self.client(handle).validate_key()
            self.assertEqual(len(seen),1)
    def test_malformed_success_refused(self):
        for data in ({'ok':True},{'credential_accepted':True},{'ok':True,'credential_accepted':'true'}):
            with self.assertRaises(SealgrafError):
                self.client(lambda r:httpx.Response(200,json=data)).validate_key()

unittest.main()

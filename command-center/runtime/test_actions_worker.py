import unittest
from .actions_worker import process, job_id, QUEUE, EVENTS, stamp

class MemorySheets:
    def __init__(self):
        self.events=[]
        context="synthetic brief"
        self.jobs=[[job_id("العقل المركزي",context),"task1","العقل المركزي",context]]
    def read(self, tab, columns):
        return self.events if tab==EVENTS else self.jobs
    def event(self,key,state,result="",error=""):
        self.events.append([key,state,result,stamp(),error])

class WorkerTests(unittest.TestCase):
    def test_duplicate_requests_are_processed_once(self):
        sheet=MemorySheets()
        sheet.jobs*=2
        self.assertEqual(process(sheet,lambda role,context:"draft"),1)
        self.assertEqual(process(sheet,lambda *args:self.fail("duplicate billing")),0)
        self.assertEqual(sheet.events[-1][1:3],["done","draft"])
    def test_failure_and_uncertain_calls_require_review(self):
        sheet=MemorySheets()
        def fail(*args): raise RuntimeError("private provider detail")
        process(sheet,fail)
        self.assertEqual(sheet.events[-1][1],"failed")
        self.assertNotIn("private provider detail",str(sheet.events))
        self.assertEqual(process(sheet,fail),0)
    def test_budget_and_invalid_input(self):
        sheet=MemorySheets()
        self.assertEqual(process(sheet,lambda *args:"draft",daily_limit=0),0)
        sheet.jobs[0][3]="modified"
        self.assertEqual(process(sheet,lambda *args:self.fail("invalid job")),0)

if __name__=="__main__":unittest.main()

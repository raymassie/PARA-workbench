from pathlib import Path
import contextlib
import importlib.util
import io
import json
import plistlib
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
def load(name,filename):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/filename)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
calendar=load('calendar_reader','read-calendar.py')
schedules=load('schedule_renderer','render-schedules.py')

class PortableConfig(unittest.TestCase):
    def test_no_calendar_config_performs_no_device_query(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(calendar,'read_calendar') as query, patch('sys.argv',['read-calendar.py','--config',str(Path(temp)/'missing.json')]), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(calendar.main(),0)
            query.assert_not_called();self.assertFalse(json.loads(output.getvalue())['available'])
    def test_calendar_names_are_explicit_local_data(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'settings.json';p.write_text(json.dumps({'calendar_names':['Work','Personal']}))
            self.assertEqual(calendar.configured_names(p),['Work','Personal'])
            p.write_text(json.dumps({'calendar_names':[123]}))
            with self.assertRaises(ValueError):calendar.configured_names(p)
    def test_calendar_name_is_an_argument_not_executable_text(self):
        from subprocess import CompletedProcess
        name='Work "special" calendar'
        with patch.object(calendar.subprocess,'run',return_value=CompletedProcess([],0,'','')) as run:
            self.assertTrue(calendar.read_calendar(name)['available'])
            argv=run.call_args.args[0]
            self.assertEqual(argv[-1],name);self.assertNotIn(name,argv[2])
    def test_calendar_retries_once(self):
        from subprocess import CompletedProcess
        with patch.object(calendar.subprocess,'run',side_effect=[CompletedProcess([],1,'','temporary'),CompletedProcess([],0,'Event','')]) as run:
            value=calendar.read_calendar('Work');self.assertTrue(value['available']);self.assertEqual(run.call_count,2)
    def test_schedule_rendering_uses_the_selected_vault(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'A vault & notes';out=Path(temp)/'jobs'
            paths=schedules.render(root,out)
            self.assertEqual(len(paths),3)
            for p in paths:
                data=plistlib.loads(p.read_bytes())
                self.assertEqual(data['WorkingDirectory'],str(root.resolve()))
                self.assertFalse(data['RunAtLoad']);self.assertTrue(data['Label'].startswith('org.para-librarian.'))
                self.assertNotIn('__VAULT_ROOT__',p.read_text())
            self.assertEqual(schedules.render(root,out),paths)
    def test_schedule_renderer_preserves_local_customizations(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'jobs';paths=schedules.render(Path(temp)/'vault',out)
            paths[0].write_text('custom local definition')
            with self.assertRaises(ValueError):schedules.render(Path(temp)/'vault',out)
            self.assertEqual(paths[0].read_text(),'custom local definition')

if __name__=='__main__':unittest.main(verbosity=2)

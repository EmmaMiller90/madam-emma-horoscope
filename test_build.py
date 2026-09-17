import unittest,tempfile,json
from pathlib import Path
from datetime import datetime,timezone,timedelta
import build
import xml.etree.ElementTree as ET
class Tests(unittest.TestCase):
 def test_editions(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);t=datetime(2026,9,16,4,40,tzinfo=timezone.utc);a=build.build(p,t);self.assertEqual(a['edition'],1);self.assertEqual(a['date'],'2026-09-16');before=(p/'daily-2026-09-16.json').read_bytes();build.build(p,t+timedelta(hours=2));self.assertEqual(before,(p/'daily-2026-09-16.json').read_bytes());self.assertEqual(len(list(p.glob('sign-*.html'))),12)
   self.assertEqual(set(a['readings']),{s['name'] for s in json.loads((build.ROOT/'editorial.json').read_text())['signs']});self.assertEqual(len({r['Signal'] for r in a['readings'].values()}),12)
   for r in a['readings'].values():self.assertEqual(set(r),{'Signal','Noise','Move','Boundary','Return'})
   self.assertIn('No future reading', (p/'tomorrow.html').read_text());self.assertIn('No live edition was published', (p/'yesterday.html').read_text());ET.fromstring((p/'feed.atom').read_text())
   b=build.build(p,t+timedelta(days=1));self.assertEqual(b['edition'],2);self.assertEqual(b['valid_until'],'2026-09-18T00:00:00Z');self.assertIn('day-2026-09-16.html',(p/'today.html').read_text());self.assertEqual(len(json.loads((p/'index.json').read_text())['editions']),2)
   with self.assertRaises(ValueError):build.build(p,t)
   build.build(p,t+timedelta(days=3));self.assertFalse((p/'daily-2026-09-18.json').exists())
 def test_exact_midnight_and_retry(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);before=datetime(2026,9,16,23,59,59,tzinfo=timezone.utc)
   a=build.build(p,before);b=build.build(p,before+timedelta(seconds=1))
   self.assertEqual((a['date'],b['date']),('2026-09-16','2026-09-17'))
   self.assertEqual(b['edition'],2)
   snapshot={f.name:f.read_bytes() for f in p.iterdir()}
   build.build(p,before+timedelta(minutes=48))
   self.assertEqual(snapshot,{f.name:f.read_bytes() for f in p.iterdir()})
 def test_editorial_rotation(self):
  start=datetime(2026,9,16,tzinfo=timezone.utc)
  editions=[build.edition(start+timedelta(days=n),n+1) for n in range(190)]
  data=json.loads((build.ROOT/'editorial.json').read_text())
  for i,s in enumerate(data['signs']):
   # Preserve launch selection, visit every combination, avoid same-section
   # next-day repetition even at ternary carry and full-cycle boundaries.
   for key in ('Signal','Noise','Move'):
    self.assertEqual(editions[0]['readings'][s['name']][key],s[key.lower()][i%3])
    self.assertTrue(all(a['readings'][s['name']][key]!=b['readings'][s['name']][key] for a,b in zip(editions,editions[1:])))
   triples=[tuple(e['readings'][s['name']][k] for k in ('Signal','Noise','Move')) for e in editions[:27]]
   self.assertEqual(len(set(triples)),27)
   self.assertEqual(editions[0]['readings'][s['name']],editions[189]['readings'][s['name']])
  for e in editions:
   for key in ('Signal','Noise','Move'):
    self.assertEqual(len({r[key] for r in e['readings'].values()}),12)
 def test_existing_edition_survives_editorial_change(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);t=datetime(2026,9,16,tzinfo=timezone.utc)
   build.build(p,t);snapshot={f.name:f.read_bytes() for f in p.iterdir()}
   with patch.object(build,'edition',side_effect=AssertionError('Must reuse immutable edition')):
    build.build(p,t+timedelta(hours=1))
   self.assertEqual(snapshot,{f.name:f.read_bytes() for f in p.iterdir()})
 def test_failure(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):build.build(d,datetime(2026,9,15,tzinfo=timezone.utc))
   self.assertFalse((Path(d)/'today.json').exists())
 def test_clock(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):build.build(d,datetime(2026,9,16))
if __name__=='__main__':unittest.main()

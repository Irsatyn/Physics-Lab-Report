import sys, tempfile, unittest
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'physics-lab-report/scripts'))
import build_report as b

class InlineMathTests(unittest.TestCase):
    def test_letters_inline_subscripts_and_all_punctuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); image=root/'photo.png'; Image.new('RGB',(32,32)).save(image)
            payload={'experiment':'测试','questions_provided':False,'data_photos':[str(image)],
                'explanation_notes':['资料中的符号识读存在差异，仅记录在说明文档。'],
                'sections':{str(i):[] for i in range(1,9)}}
            payload['sections']['6']=[{'text':'电压 Udy,电流 {{math:{"sub":["I","m"]}}}；单位 V。'},
                {'equation':{'seq':['U=1.2 V,',{'sub':['I','m']}]}},
                {'figure':{'path':str(image),'caption':'图1 参数 Udy。'}},
                {'table':{'headers':['参数 Udy','测量值'],'rows':[['Im','1.2']]}}]
            payload['sections']['7']=[{'text':'结果满足物理关系。'}]
            out=root/'report.docx'; b.build(payload,out)
            with ZipFile(out) as z: xml=etree.fromstring(z.read('word/document.xml'))
            texts=xml.findall('.//w:t',b.NS)
            self.assertFalse(any('Udy' in (t.text or '') or 'Im' in (t.text or '') or '{{math:' in (t.text or '') for t in texts))
            self.assertTrue(xml.findall('.//m:sSub',b.NS))
            self.assertFalse(any('识读存在差异' in (t.text or '') for t in texts))
            self.assertIn(payload['explanation_notes'][0],b.delivery_notes(payload))
            for t in xml.findall('.//w:t',b.NS)+xml.findall('.//m:t',b.NS):
                if ',' in (t.text or '') or '。' in (t.text or '') or '.' in (t.text or ''):
                    fonts=t.getparent().find('w:rPr/w:rFonts',b.NS)
                    self.assertIsNotNone(fonts)
                    self.assertEqual(fonts.get(b.qn('w:ascii')),'宋体')
                    self.assertEqual(fonts.get(b.qn('w:eastAsia')),'宋体')
            audit=b.audit_document(out)
            self.assertEqual(audit['section_equation_placements']['6'],1)
            self.assertEqual(audit['unformatted_letters'],0)
            self.assertEqual(audit['punctuation_font_issues'],0)

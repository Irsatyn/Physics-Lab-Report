import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from PIL import Image
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'physics-lab-report' / 'scripts'))


class ReportTests(unittest.TestCase):
    def test_report_contract(self):
        import build_report
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            photo = folder / 'photo.png'
            Image.new('RGB', (600, 300), 'white').save(photo)
            payload = {'experiment': '工具测试', 'sections': {str(i): [{'text': '测试内容'}] for i in range(1, 9)},
                       'data_photos': [str(photo)]}
            payload['sections']['6'] += [{'equation': {'seq': ['R=', {'frac': [{'seq': ['U', '+1']}, 'I']}, '=10 Ω']}}]
            payload['sections']['6'] += [{'figure': {'path': str(photo), 'caption': '测试数据图'}}]
            template = ROOT / 'physics-lab-report' / 'assets' / 'physics-report-template.docx'
            original = template.read_bytes()
            output = folder / 'report.docx'
            audit = build_report.build(payload, output, template=template)
            self.assertEqual(audit['equations'], 1)
            self.assertEqual(audit['data_photos'], 1)
            self.assertEqual(template.read_bytes(), original)
            with ZipFile(output) as z:
                xml = etree.fromstring(z.read('word/document.xml'))
            ns = build_report.NS
            self.assertEqual(len(xml.findall('.//m:f', ns)), 1)
            self.assertEqual(len(xml.findall('.//m:num/m:e', ns)), 0)
            self.assertEqual(len(xml.findall('.//m:e/m:e', ns)), 0)
            texts = [''.join(p.itertext()) for p in xml.findall('.//w:body/w:p', ns)]
            fifth = next(i for i, t in enumerate(texts) if t.startswith('五、'))
            sixth = next(i for i, t in enumerate(texts) if t.startswith('六、'))
            paras = xml.findall('.//w:body/w:p', ns)
            self.assertEqual(sum(len(p.findall('.//w:drawing', ns)) for p in paras[fifth:sixth]), 1)
            self.assertIn('姓名：', ''.join(texts))
            with self.assertRaises(ValueError):
                build_report.build({**payload, 'data_photos': []}, folder / 'bad.docx', template=template)
            self.assertFalse((folder / 'bad.docx').exists())
            draft = build_report.build({**payload, 'data_photos': []}, folder / 'draft.docx', template=template, draft=True)
            self.assertEqual(draft['status'], 'draft')
            with self.assertRaises(ValueError):
                build_report.build(payload, template, template=template)
            with self.assertRaises(ValueError):
                build_report.math_node({'unsupported': 'x'})

    def test_arbitrarily_nested_sequences_are_flattened(self):
        import build_report as b
        expression = b.math_node({'seq': [{'seq': ['x', {'seq': ['+', 'y']}]}, '=1']})
        self.assertEqual(len(expression.findall('.//m:e', b.NS)), 0)
        self.assertEqual(''.join(expression.itertext()), 'x+y=1')

    def test_empty_equations_are_rejected(self):
        import build_report as b
        for value in ['', '  ', {'seq': ['x', '']}, {'frac': ['', 'x']}, float('nan')]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                b.math_node(value)

    def test_required_content_and_plot_cannot_be_empty(self):
        import build_report as b
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            image = folder/'photo.png'
            Image.new('RGB', (100, 100), 'white').save(image)
            payload = {'experiment': '测试', 'data_photos': [str(image)],
                       'sections': {str(i): [{'text': '内容'}] for i in range(1, 9)}}
            payload['sections']['6'].append({'equation': {'frac': ['U', 'I']}})
            with self.assertRaises(ValueError):
                b.build(payload, folder/'missing-plot.docx')
            payload['sections']['6'].append({'figure': {'path': str(image)}})
            process = payload['sections']['6'][0]
            payload['sections']['6'][0] = {'table': {'headers': ['数据'], 'rows': [[' ']]}}
            with self.assertRaises(ValueError):
                b.build(payload, folder/'empty-process.docx')
            payload['sections']['6'][0] = process
            for index in ('7', '8'):
                saved = payload['sections'][index]
                payload['sections'][index] = [{'text': '   '}]
                with self.assertRaises(ValueError):
                    b.build(payload, folder/'empty.docx')
                payload['sections'][index] = saved
            audit = b.build(payload, folder/'assembled.docx')
            self.assertEqual(audit['status'], 'assembled')

    def test_report_values_can_bind_to_calculation_results(self):
        import build_report as b
        import json
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            data = folder/'results.json'
            data.write_text(json.dumps({'slope': 2.123456}))
            payload = {'experiment': '结果绑定测试', 'data_photos': [],
                       'result_files': {'fit': str(data)},
                       'sections': {str(i): [] for i in range(1, 9)}}
            payload['sections']['6'] = [{'text': 'a={{result:fit.slope:.3f}}'},
                                        {'equation': {'seq': ['a=', '{{result:fit.slope:.3f}}']}}]
            b.build(payload, folder/'draft.docx', draft=True)
            with ZipFile(folder/'draft.docx') as z:
                xml = etree.fromstring(z.read('word/document.xml'))
            self.assertIn('a=2.123', ''.join(xml.itertext()))
            self.assertNotIn('{{result:', ''.join(xml.itertext()))
            self.assertIn('{{result:', payload['sections']['6'][0]['text'])


if __name__ == '__main__':
    unittest.main()

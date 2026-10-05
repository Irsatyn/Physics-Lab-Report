import json
import sys
import tempfile
import unittest
from pathlib import Path
from page_fixtures import synthetic_pages

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'physics-lab-report'/'scripts'))


class FinalizeTests(unittest.TestCase):
    def test_removed_input_photo_blocks_without_crashing(self):
        import finalize_report as f
        import build_report as b
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            photo = root/'photo.png'
            Image.new('RGB', (100, 100), 'white').save(photo)
            payload = {'experiment': '缺失输入测试', 'data_photos': [str(photo)],
                       'sections': {str(i): [{'text': '内容'}] for i in range(1, 9)}}
            payload['sections']['6'] += [{'equation': {'frac': ['U', 'I']}}, {'figure': {'path': str(photo)}}]
            docx = root/'report.docx'
            b.build(payload, docx)
            photo.unlink()
            result = f.evaluate(payload, docx, {}, root)
            self.assertEqual(result['status'], 'review-pending')
            self.assertTrue(any('不存在' in item for item in result['issues']))

    def test_initialized_checklist_requires_real_review_and_execution(self):
        import finalize_report as f
        import build_report as b
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root/'image.png'
            Image.new('RGB', (100, 100), 'white').save(image)
            payload = {'experiment': '初始化检查测试', 'data_photos': [str(image)],
                       'sections': {str(i): [{'text': '测试内容'}] for i in range(1, 9)}}
            payload['sections']['6'] += [{'equation': {'frac': ['U', 'I']}}, {'figure': {'path': str(image)}}]
            docx = root/'report.docx'
            b.build(payload, docx)
            record = f.initialize_quality(payload, docx, root, pages=synthetic_pages(root), code=[str(Path(__file__).resolve())])
            self.assertTrue(all(r['status'] == 'pending' for r in record['vision_reviews']))
            self.assertIsNone(record['execution_records'][0]['exit_code'])
            self.assertEqual(f.evaluate(payload, docx, record, root)['status'], 'review-pending')

    def test_missing_or_stale_vision_and_layout_evidence_blocks_submission(self):
        import finalize_report as f
        import build_report as b
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            photo = root/'photo.png'
            Image.new('RGB', (100, 100), 'white').save(photo)
            payload = {'experiment': '质量检查测试', 'data_photos': [str(photo)],
                       'sections': {str(i): [{'text': '测试内容'}] for i in range(1, 9)}}
            payload['sections']['6'] += [{'equation': {'frac': ['U', 'I']}}, {'figure': {'path': str(photo)}}]
            docx = root/'report.docx'
            b.build(payload, docx)
            self.assertEqual(f.evaluate(payload, docx, {}, root)['status'], 'review-pending')
            pages = synthetic_pages(root)
            quality = {
                'report_sha256': f.digest_file(docx), 'input_sha256': b.payload_digest(payload),
                'vision_reviews': [{'path': str(photo), 'sha256': f.digest_file(photo), 'status': 'passed',
                                    'reviewer': 'current-model', 'checks': ['test fixture only'], 'evidence': 'unit-test fixture'}],
                'calculation_review': {'status': 'passed', 'reviewer': 'current-model', 'evidence': 'unit-test fixture'},
                'layout_review': {'status': 'passed', 'reviewer': 'current-model', 'page_count': len(pages), 'pages': pages, 'evidence': 'unit-test fixture'},
                'execution_records': [{'path': str(Path(__file__).resolve()), 'sha256': f.digest_file(Path(__file__)),
                                       'exit_code': 0, 'command': 'unit-test fixture'}],
                'delivery_files': [str(docx), str(Path(__file__).resolve())]}
            quality['vision_reviews'] += [
                {'path': p, 'sha256': f.digest_file(p), 'status': 'passed', 'reviewer': 'current-model',
                 'checks': ['synthetic fixture'], 'evidence': 'synthetic fixture'} for p in pages]
            self.assertEqual(f.evaluate(payload, docx, quality, root)['status'], 'submission-ready')
            quality['calculation_review'].pop('reviewer')
            with self.subTest('calculation reviewer required'):
                self.assertEqual(f.evaluate(payload, docx, quality, root)['status'], 'review-pending')
            quality['calculation_review']['reviewer'] = 'current-model'
            quality['vision_reviews'][0]['sha256'] = 'stale'
            self.assertEqual(f.evaluate(payload, docx, quality, root)['status'], 'review-pending')
            quality['vision_reviews'][0]['sha256'] = f.digest_file(photo)
            b.build(payload, docx, draft=True)
            quality['report_sha256'] = f.digest_file(docx)
            with self.subTest('explicit draft cannot be finalized'):
                self.assertEqual(f.evaluate(payload, docx, quality, root)['status'], 'draft')
            data = root/'results.json'
            data.write_text(json.dumps({'slope': 2}))
            payload['result_files'] = {'fit': str(data)}
            quality['delivery_files'].append(str(data))
            payload['sections']['6'][0] = {'text': 'slope={{result:fit.slope:.1f}}'}
            b.build(payload, docx)
            quality['report_sha256'] = f.digest_file(docx)
            quality['input_sha256'] = b.payload_digest(payload)
            quality['artifact_checks'] = [{'path': str(data), 'sha256': f.digest_file(data), 'status': 'passed', 'evidence': 'unit-test fixture'}]
            self.assertEqual(f.evaluate(payload, docx, quality, root)['status'], 'submission-ready')
            data.write_text(json.dumps({'slope': 9}))
            quality['artifact_checks'][0]['sha256'] = f.digest_file(data)
            with self.subTest('report must be rebuilt after changing results'):
                self.assertEqual(f.evaluate(payload, docx, quality, root)['status'], 'review-pending')
            payload['sections']['7'] = [{'text': 'changed'}]
            self.assertEqual(f.evaluate(payload, docx, quality, root)['status'], 'review-pending')


if __name__ == '__main__':
    unittest.main()

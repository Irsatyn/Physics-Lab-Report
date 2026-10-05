"""Check declared review evidence against current files; never fabricates reviews.

This checks completeness and freshness of records, not the truth of a model's
claim that it saw an image or the scientific correctness of its conclusions.
"""
import argparse
import hashlib
import json
from pathlib import Path

import build_report as report


def digest_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def evaluate(payload, docx, quality, base):
    try:
        return _evaluate(payload, docx, quality, base)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {'status': 'review-pending', 'issues': ['无法完成检查，输入文件或记录无效：' + str(exc)],
                'record_validation_only': True}


def _evaluate(payload, docx, quality, base):
    base, docx = Path(base).resolve(), Path(docx).resolve()
    def path(value):
        return (base/str(value)).resolve()
    issues = []
    bound = report.bind_results(payload)
    missing = report.content_issues(bound)
    issues.extend(missing)
    if not docx.is_file():
        return {'status': 'draft', 'issues': issues + ['报告文件不存在']}
    audit = report.audit_document(docx)
    assembled = audit.get('assembly_manifest')
    explicit_draft = isinstance(assembled, dict) and assembled.get('stage') == 'draft'
    if explicit_draft:
        issues.append('报告以草稿模式组装，需补齐资料并重新生成')
    if not assembled:
        issues.append('报告缺少组装版本记录')
    else:
        try:
            if assembled.get('version') != 2 or not assembled.get('template_file'):
                issues.append('报告缺少实际模板版本记录，需重新生成')
            current = report.assembly_manifest(payload, bound, template=assembled.get('template_file'))
            if any(assembled.get(key) != current[key] for key in ('input_sha256', 'bound_sha256', 'artifact_sha256')):
                issues.append('报告与当前输入、结果或图像版本不一致，需重新生成并复核')
        except OSError:
            issues.append('组装版本无法核对：输入文件不存在或不可读')
    if audit.get('unformatted_letters'):
        issues.append('存在未使用公式编辑器的字母/参数')
    if audit.get('punctuation_font_issues'):
        issues.append('存在未显式使用宋体的标点')
    if audit['invalid_math_containers']:
        issues.append('Word 公式结构不正确')
    for section, blocks in payload['sections'].items():
        expected = sum('equation' in block for block in blocks)
        if audit['section_equation_placements'][section] < expected:
            issues.append('第' + section + '部分公式缺失或位置不符')
    if audit['section_image_placements']['5'] < len(payload.get('data_photos', [])):
        issues.append('第五部分照片数量不符')
    if audit['section_image_placements']['6'] < sum('figure' in b for b in payload['sections']['6']):
        issues.append('第六部分图像数量不符')
    for blocks in payload['sections'].values():
        for block in blocks:
            figure = block.get('figure', {})
            if figure.get('source') == 'imagegen':
                fingerprint = digest_file(path(figure['path']))
                placements = [r for r in audit['image_resolutions'] if r['sha256'] == fingerprint]
                if not placements or any(r['metadata_dpi'] < 300 or r['effective_dpi'] < 300 for r in placements):
                    issues.append('生图在报告中的元数据或有效分辨率不足 300 dpi：' + figure['path'])
    if quality.get('report_sha256') != digest_file(docx):
        issues.append('报告缺少匹配的复核指纹或复核后已修改')
    if quality.get('input_sha256') != report.payload_digest(payload):
        issues.append('报告输入缺少匹配的复核指纹或复核后已修改')

    visual_paths = list(payload.get('data_photos', [])) + list(payload.get('visual_sources', []))
    visual_paths += [block['figure']['path'] for blocks in payload['sections'].values() for block in blocks if 'figure' in block]
    records = {path(r['path']): r for r in quality.get('vision_reviews', []) if isinstance(r, dict) and r.get('path')}
    for value in visual_paths:
        image = path(value)
        record = records.get(image, {})
        if not image.is_file():
            issues.append('待复核图片不存在：' + str(value))
        elif (record.get('reviewer') != 'current-model' or record.get('status') != 'passed'
              or not record.get('checks') or not record.get('evidence') or record.get('unresolved')
              or record.get('sha256') != digest_file(image)):
            issues.append('缺少当前模型的有效识图复核：' + str(value))
    for label, field in [('数值核验', 'calculation_review'), ('排版复核', 'layout_review')]:
        record = quality.get(field, {})
        if (record.get('reviewer') != 'current-model' or record.get('status') != 'passed'
            or not record.get('evidence') or record.get('unresolved')):
            issues.append(label + '尚未完成')
    layout = quality.get('layout_review', {})
    if layout.get('reviewer') != 'current-model':
        issues.append('最终页面尚未由当前模型查看')
    pages = layout.get('pages', [])
    if (not pages or layout.get('page_count') != len(pages) or len({path(p) for p in pages}) != len(pages)
        or any(not path(p).is_file() for p in pages)):
        issues.append('缺少最终渲染页面')
    else:
        if not 10 <= len(pages) <= 20:
            issues.append('最终实验报告须为 10–20 页；当前为 ' + str(len(pages)) + ' 页，需调整内容与排版并重新复核')
        for page in pages:
            image = path(page)
            record = records.get(image, {})
            if (record.get('reviewer') != 'current-model' or record.get('status') != 'passed'
                or not record.get('checks') or not record.get('evidence')
                or record.get('sha256') != digest_file(image) or record.get('unresolved')):
                issues.append('最终渲染页面缺少有效看图记录：' + str(page))
    artifacts = {path(r['path']): r for r in quality.get('artifact_checks', []) if isinstance(r, dict) and r.get('path')}
    asset_paths = list(payload.get('result_files', {}).values()) + list(payload.get('data_files', []))
    if payload.get('template_file'):
        asset_paths.append(payload['template_file'])
    elif assembled and assembled.get('template_file') and Path(assembled['template_file']).resolve() != report.TEMPLATE.resolve():
        asset_paths.append(assembled['template_file'])
    for value in asset_paths:
        file = path(value)
        record = artifacts.get(file, {})
        if (not file.is_file() or record.get('status') != 'passed' or not record.get('evidence')
            or record.get('sha256') != digest_file(file)):
            issues.append('计算结果文件未核验或已修改：' + str(value))
    executions = quality.get('execution_records', [])
    if not executions:
        issues.append('缺少已执行的计算或绘图源码记录')
    for record in executions:
        code = path(record.get('path', ''))
        if (not code.is_file() or code.suffix.lower() not in {'.py', '.m'}
            or type(record.get('exit_code')) is not int or record.get('exit_code') != 0 or not record.get('command')
            or record.get('sha256') != digest_file(code)):
            issues.append('计算/绘图执行记录不完整或源码已修改')
    files = [path(p) for p in quality.get('delivery_files', [])]
    if docx not in files or any(not p.is_file() for p in files):
        issues.append('交付清单缺少报告或包含不存在的文件')
    for record in executions:
        if path(record.get('path', '')) not in files:
            issues.append('交付清单缺少实际使用的源码')
    delivered_hashes = {digest_file(p) for p in files if p.is_file()}
    for value in asset_paths:
        file = path(value)
        if file.is_file() and digest_file(file) not in delivered_hashes:
            issues.append('交付清单缺少复现数据或结果：' + str(value))
    if quality.get('unresolved'):
        issues.append('存在未解决的问题')
    return {'status': 'draft' if missing or explicit_draft else ('review-pending' if issues else 'submission-ready'),
            'issues': list(dict.fromkeys(issues)), 'audit': audit,
            'delivery_notes': report.delivery_notes(payload),
            'record_validation_only': True}


def initialize_quality(payload, docx, base, pages=(), code=()):
    """Create pending records, never marks a review or an execution as passed."""
    base = Path(base).resolve()
    def path(value): return (base/str(value)).resolve()
    docx = Path(docx).resolve()
    visual = list(payload.get('data_photos', [])) + list(payload.get('visual_sources', [])) + list(pages)
    visual += [b['figure']['path'] for blocks in payload['sections'].values() for b in blocks if 'figure' in b]
    assets = list(payload.get('result_files', {}).values()) + list(payload.get('data_files', []))
    if payload.get('template_file'):
        assets.append(payload['template_file'])
    else:
        assembled = report.audit_document(docx).get('assembly_manifest') or {}
        if assembled.get('template_file') and Path(assembled['template_file']).resolve() != report.TEMPLATE.resolve():
            assets.append(assembled['template_file'])
    def record(value):
        file = path(value)
        return {'path': str(file), 'sha256': digest_file(file), 'status': 'pending', 'evidence': '', 'unresolved': []}
    return {
        'report_sha256': digest_file(docx), 'input_sha256': report.payload_digest(payload),
        'vision_reviews': [{**record(p), 'reviewer': 'current-model', 'checks': []} for p in dict.fromkeys(visual)],
        'artifact_checks': [record(p) for p in dict.fromkeys(assets)],
        'calculation_review': {'status': 'pending', 'reviewer': 'current-model', 'evidence': '', 'unresolved': []},
        'layout_review': {'status': 'pending', 'reviewer': 'current-model', 'evidence': '',
                          'page_count': len(pages), 'pages': [str(path(p)) for p in pages], 'unresolved': []},
        'execution_records': [{'path': str(path(p)), 'sha256': digest_file(path(p)), 'exit_code': None, 'command': ''} for p in code],
        'delivery_files': [str(p) for p in dict.fromkeys([docx]+[path(p) for p in code]+[path(p) for p in assets])],
        'unresolved': []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('docx', type=Path)
    parser.add_argument('--quality', required=True, type=Path)
    parser.add_argument('--init-quality', action='store_true', help='Write a new pending checklist; does not perform any review')
    parser.add_argument('--pages', nargs='*', default=[])
    parser.add_argument('--code', nargs='*', default=[])
    args = parser.parse_args()
    payload = report.load_payload(args.input)
    if args.init_quality:
        if args.quality.exists():
            parser.error('Quality record already exists; do not overwrite completed reviews')
        data = initialize_quality(payload, args.docx, args.input.resolve().parent, args.pages, args.code)
        args.quality.parent.mkdir(parents=True, exist_ok=True)
        args.quality.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Pending quality checklist created; no review has been marked passed')
        return
    quality = json.loads(args.quality.read_text(encoding='utf-8-sig'))
    result = evaluate(payload, args.docx, quality, args.input.resolve().parent)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'submission-ready' else 1)


if __name__ == '__main__':
    main()

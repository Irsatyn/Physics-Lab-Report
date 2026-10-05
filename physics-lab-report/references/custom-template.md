# 自定义模板和复杂公式的生成与验收

## 路由

只需沿用页面设置和样式时使用 `build_report.py --template`，它会重建正文。用户要求保留文本框、复杂表格、内容控件和固定布局时，编写并执行本次专用 `.py` 生成脚本：读取模板，修改副本中的指定内容位置，不调用标准 build 函数清空正文。原始模板不覆盖。

## 生成脚本契约

1. 以相同 report.json 清点八部分、照片、图像、数据、结果和视觉来源，调用 `load_payload`、`bind_results`、`content_issues` 校验完整性。将原始模板路径记录在 `template_file`，载入模板副本并按已检查的占位位置填充绑定后的内容；JSON 与实际写入内容必须一致。
2. 照片/数据图和对应标题应处于第五/六部分。最终检查器目前通过正文的八个标准标题识别分节，并审计正文内联图片；复杂布局可保留，但标题和必需照片/图像必须仍采用该可审计结构。若用户固定模板无法满足，保留模板要求并交付待复核稿，说明检查器限制，不添加隐藏标题或图片绕过检查。
3. 复杂公式可调用 `add_equation(doc, {"omml": xml})` 插入完整公式段落；表格/指定段落中可将 `math_node({"omml": xml})` 的返回节点插入目标 `w:p`。此原始 OMML 入口只用于完整公式，不能嵌入 seq/frac 树。完成结构检查及页面视觉复核。
4. 完成所有内容填充后、第一次保存该生成版本前，调用下面的生成记录接口。仅生成脚本在实际生成时调用，不能事后给旧文档补记录。模板、内容或结果变化时，重新执行完整生成流程并重新渲染复核。

```python
from build_report import assembly_manifest, set_assembly_manifest

# payload 来自 load_payload；bound 来自 bind_results。
# doc 为已由本次生成脚本按 bound 填充完成的模板副本。
set_assembly_manifest(doc, assembly_manifest(payload, bound, draft=False))
doc.save(output_path)
```

5. 执行专用脚本，把生成源码、原始模板和复现所需文件加入交付清单。用 `audit_document` 检查 OMML 和分章节图像数量；生图有效 dpi 由最终检查器统一检查。导出全部最终页面，实际查看公式、文本框、表格、内容控件、照片、分页及模板保留情况。
6. 使用原 report.json 和新 DOCX 初始化质量记录，`--code` 包含成功的计算/绘图源码和专用生成脚本。补齐真实复核记录后运行 `finalize_report.py`；只有返回 submission-ready 才可称为可提交报告。

`template_file` 与模板内容指纹纳入 assembly_manifest，并在质量 artifact_checks 中核验。上述接口只解决自定义生成的版本绑定，不自动证明填充内容正确或模板完整；当前模型须实际对照 JSON 和模板并核验全部页面。

`assembly_manifest` 的版本 2 将实际模板路径保存在 Word 文档变量中；默认从 `template_file` 选择，省略时使用默认模板。专用脚本实际读取的模板必须与该路径一致，也可用 `assembly_manifest(payload, bound, draft=False, template=actual_template)` 显式传入；与 `template_file` 冲突会报错。标准 `build_report.py --template` 会自动传入实际模板。修改模板后需重新生成和复核，不能只刷新模板复核指纹。最终检查要求每部分的实际公式数量不少于其 JSON 公式块数量；表格和内容控件中的公式也计入相应章节。

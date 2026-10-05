# 开发与打包

仓库包含一个可安装 skill：`physics-lab-report/`。其入口为 `SKILL.md`，`agents/openai.yaml` 提供界面提示；支持资源分别放 `assets/`、`scripts/`、`references/`。根目录 README、依赖、测试与 CI 用于项目维护，不进入 skill 安装包。

```powershell
python -m pip install -r requirements-dev.txt
python -X utf8 -m unittest discover -s tests -v
python scripts/package_skill.py
```

安装包仅包含 `physics-lab-report/`，排除字节码和缓存；打包脚本验证文件清单、ZIP 完整性和文件内容一致性。报告渲染可选使用 `pypdfium2`，Windows Word 导出脚本需本机已安装 Word；运行普通测试无需 Word、MATLAB 或外部解析服务。

更新要求时同步入口、对应参考和回归测试；原生公式、字体、照片或布局的修改还应渲染实际样例并由当前模型查看。测试材料必须是合成材料，不提交个人实验数据、来源附件、工作缓存或凭据。

项目暂未声明开源许可证，GitHub 发布不自动授予再分发或修改许可。

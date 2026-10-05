# Physics Lab Report

生成中文 Word 物理实验报告的 Codex skill：10–20 页、原生可编辑公式、互补数据图及可复现代码。未上传资料时，按实验名称联网检索可靠资料，来源及检索说明仅写说明文档。缺真实测量数据或照片时交付草稿。

## 使用

下载 [安装包](physics-lab-report.zip)，将解压后的 `physics-lab-report/` 放入 `~/.codex/skills/`，然后调用：

```text
使用 $physics-lab-report，为“实验名称”编写物理实验报告。
```

最终交付：报告、说明文档、图片文件夹、代码文件夹。详细要求见 [SKILL.md](physics-lab-report/SKILL.md)。

## 项目结构

```text
physics-lab-report/     可安装 skill（入口、模板、脚本、参考）
tests/                 回归测试
scripts/               项目打包工具
docs/                  开发与验证说明
.github/workflows/     CI 检查
requirements*.txt      运行及开发依赖
physics-lab-report.zip 安装包
```

## 开发

```bash
python -m pip install -r requirements-dev.txt
python -X utf8 -m unittest discover -s tests -v
python scripts/package_skill.py
```

[开发说明](docs/development.md) · [验证范围](docs/verification.md)

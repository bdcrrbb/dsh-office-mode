"""Phase 2 验证脚本：校验 preset.yml / agent.cordis.yml / skills / templates 结构完整性。
处理 DSH cordis 专有 !!js 标签（视为字符串）。
"""
import yaml, pathlib, re, json, sys

# 自定义 !!js 标签处理器
def js_constructor(loader, node):
    return loader.construct_scalar(node)

yaml.SafeLoader.add_constructor('tag:yaml.org,2002:js', js_constructor)

root = pathlib.Path("/home/dsh/office-mode")
errors = []

# 1. YAML 解析
for f in ["preset.yml", "agent.cordis.yml"]:
    text = (root/f).read_text()
    js_count = text.count("!!js")
    try:
        data = yaml.load(text, Loader=yaml.SafeLoader)
        if isinstance(data, list):
            print(f"  {f}: list, {len(data)} rows, {js_count} !!js tags ✓")
        elif isinstance(data, dict):
            print(f"  {f}: dict, {js_count} !!js tags ✓")
        else:
            errors.append(f"{f}: unexpected type {type(data)}")
    except Exception as e:
        errors.append(f"{f}: PARSE ERROR — {e}")

# 2. SKILL.md frontmatter
for s in ["docx", "pptx", "report-writing"]:
    t = (root/f"skills/{s}/SKILL.md").read_text()
    m = re.match(r"^---\nname: ([\w-]+)\ndescription: >-\n(.+?)\n---\n", t, re.S)
    if m:
        print(f"  skills/{s}/SKILL.md: name={m.group(1)}, desc={len(m.group(2))} chars ✓")
    else:
        errors.append(f"skills/{s}/SKILL.md: frontmatter mismatch")

# 3. style.json
try:
    style = json.load(open(root/"templates/style.json"))
    print(f"  templates/style.json: {len(style)} top keys ✓")
except Exception as e:
    errors.append(f"templates/style.json: {e}")

# 4. 关键内容检查
cordis_text = (root/"agent.cordis.yml").read_text()
checks = [
    ("customSkillDirs", "customSkillDirs" in cordis_text),
    ("persona 办公", "办公文档写作 agent" in cordis_text),
    ("fetch: true", "fetch: true" in cordis_text),
    ("office/skills 路径", "/var/lib/dsh/.agent-presets/office/skills" in cordis_text),
]
for name, ok in checks:
    if ok:
        print(f"  agent.cordis.yml: {name} ✓")
    else:
        errors.append(f"agent.cordis.yml: missing {name}")

if errors:
    print("\nERRORS:")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
else:
    print("\nPhase 2 ALL OK")

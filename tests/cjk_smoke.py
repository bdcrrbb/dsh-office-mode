"""matplotlib 中文渲染冒烟测试 — P0 硬门槛。
用 font_manager.addfont 直接加载 OTF（服务器无 fontconfig）。
产物 cjk-smoke.png 用 read_image 目视确认无豆腐块。
"""
import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, pyplot as plt
import pathlib

FONT_DIR = pathlib.Path.home() / "office-toolchain/fonts"
for weight in ["Regular", "Bold"]:
    font_manager.fontManager.addfont(FONT_DIR / f"NotoSansCJKsc-{weight}.otf")

plt.rcParams["font.family"] = "Noto Sans CJK SC"
plt.rcParams["axes.unicode_minus"] = False

OUT = pathlib.Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 4))
ax.set_title("中文字体冒烟测试：销售额（万元）", fontsize=16, fontweight="bold")
ax.bar(["一季度", "二季度", "三季度", "四季度"], [120, 150, 90, 180], color="#1F4E79")
ax.set_ylabel("销售额（万元）")
ax.set_xlabel("季度")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "cjk-smoke.png", dpi=150)
print(f"saved → {OUT / 'cjk-smoke.png'}")

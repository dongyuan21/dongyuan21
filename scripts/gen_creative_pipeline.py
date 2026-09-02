#!/usr/bin/env python3
"""Generate creative-pipeline.excalidraw for the GitHub profile README."""

from __future__ import annotations

import json
import random
import string
import time
from pathlib import Path

random.seed(21)
NOW = int(time.time() * 1000)
INDEX = 0


def nid() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=12))


def next_index() -> str:
    global INDEX
    INDEX += 1
    return f"a{INDEX}"


def base(**kw):
    el = {
        "id": nid(),
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0,
        "angle": 0,
        "strokeColor": "#1e293b",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "index": next_index(),
        "roundness": None,
        "seed": random.randint(1, 2**31 - 1),
        "version": 1,
        "versionNonce": random.randint(1, 2**31 - 1),
        "isDeleted": False,
        "boundElements": None,
        "updated": NOW,
        "link": None,
        "locked": False,
    }
    el.update(kw)
    return el


def rect(x, y, w, h, bg, stroke, dashed=False, link=None):
    return base(
        type="rectangle",
        x=x,
        y=y,
        width=w,
        height=h,
        backgroundColor=bg,
        strokeColor=stroke,
        strokeStyle="dashed" if dashed else "solid",
        roundness={"type": 3},
        link=link,
        boundElements=[],
    )


def text(x, y, w, h, content, size=18, color="#0f172a", align="center", valign="middle", container=None, family=1):
    return base(
        type="text",
        x=x,
        y=y,
        width=w,
        height=h,
        text=content,
        originalText=content,
        fontSize=size,
        fontFamily=family,
        textAlign=align,
        verticalAlign=valign,
        baseline=size,
        lineHeight=1.25,
        containerId=container,
        strokeColor=color,
        backgroundColor="transparent",
        roundness=None,
        autoResize=True,
    )


def bind_text(box, txt):
    txt["containerId"] = box["id"]
    box["boundElements"] = (box.get("boundElements") or []) + [{"id": txt["id"], "type": "text"}]
    txt["x"] = box["x"] + 8
    txt["y"] = box["y"] + 8
    txt["width"] = box["width"] - 16
    txt["height"] = box["height"] - 16


def arrow(x1, y1, x2, y2, start=None, end=None, color="#334155"):
    el = base(
        type="arrow",
        x=x1,
        y=y1,
        width=x2 - x1,
        height=y2 - y1,
        strokeColor=color,
        backgroundColor="transparent",
        fillStyle="solid",
        strokeWidth=2,
        roundness={"type": 2},
        points=[[0, 0], [x2 - x1, y2 - y1]],
        lastCommittedPoint=None,
        startBinding=None,
        endBinding=None,
        startArrowhead=None,
        endArrowhead="arrow",
        elbowed=False,
    )
    if start:
        el["startBinding"] = {"elementId": start["id"], "focus": 0, "gap": 6}
        start["boundElements"] = (start.get("boundElements") or []) + [{"id": el["id"], "type": "arrow"}]
    if end:
        el["endBinding"] = {"elementId": end["id"], "focus": 0, "gap": 6}
        end["boundElements"] = (end.get("boundElements") or []) + [{"id": el["id"], "type": "arrow"}]
    return el


def labeled(box, content, size=16, color="#0f172a"):
    t = text(0, 0, 10, 10, content, size=size, color=color)
    bind_text(box, t)
    return t


def main():
    elements = []

    title = text(40, 24, 1000, 36, "Match-3 Ad Creative Pipeline", size=28, color="#0f172a", align="center")
    subtitle = text(
        40,
        64,
        1000,
        28,
        "素材结构  ·  片头 Hook  +  主体玩法 Gameplay",
        size=18,
        color="#475569",
        align="center",
    )
    elements += [title, subtitle]

    hook = rect(40, 120, 250, 250, "#f8fafc", "#64748b", dashed=True)
    hook_t = labeled(
        hook,
        "Hook / Intro\n片头批量复刻\n\nC-end workflow\n调 C 端批量生产\n\n(not in GitHub)",
        size=16,
        color="#475569",
    )
    elements += [hook, hook_t]

    plus = text(300, 220, 36, 36, "+", size=28, color="#94a3b8", align="center")
    elements.append(plus)

    bcs = rect(
        340,
        120,
        390,
        250,
        "#dbeafe",
        "#2563eb",
        link="https://dongyuan21.github.io/block-creative-studio/",
    )
    bcs_t = labeled(
        bcs,
        "block-creative-studio\n主体玩法模拟器骨架\n\nImport assets\nStoryboard / 牌面编排\n3D render  →  Export video\nCLI for agents",
        size=16,
        color="#1e3a8a",
    )
    elements += [bcs, bcs_t]

    json_box = rect(780, 120, 260, 70, "#fef9c3", "#ca8a04")
    json_t = labeled(json_box, "Render 不够？\nBCS 导出 JSON", size=15, color="#854d0e")
    elements += [json_box, json_t]

    agent = rect(780, 210, 260, 70, "#ffedd5", "#ea580c")
    agent_t = labeled(agent, "Agent 解析 JSON\n→ AE / Blender 工程", size=15, color="#9a3412")
    elements += [agent, agent_t]

    skills = rect(
        780,
        300,
        260,
        70,
        "#dcfce7",
        "#16a34a",
        link="https://github.com/dongyuan21/ae-c4d-skills",
    )
    skills_t = labeled(skills, "ae-c4d-skills\n原子化元素 → 资产回 BCS", size=15, color="#166534")
    elements += [skills, skills_t]

    a1 = arrow(730, 155, 780, 155, start=bcs, end=json_box, color="#ca8a04")
    a2 = arrow(910, 190, 910, 210, start=json_box, end=agent, color="#ea580c")
    a3 = arrow(910, 280, 910, 300, start=agent, end=skills, color="#16a34a")
    back = arrow(780, 335, 730, 335, start=skills, end=bcs, color="#2563eb")
    back_label = text(560, 310, 160, 20, "assets 回流", size=13, color="#2563eb", align="center")
    elements += [a1, a2, a3, back, back_label]

    audio = rect(
        340,
        410,
        390,
        90,
        "#f3e8ff",
        "#7c3aed",
        link="https://github.com/dongyuan21/nanoAuralRuntime",
    )
    audio_t = labeled(
        audio,
        "nanoAuralRuntime\n面向消除游戏的 Foley / SFX 生成  →  混入成片",
        size=16,
        color="#5b21b6",
    )
    mix = arrow(535, 370, 535, 410, start=bcs, end=audio, color="#7c3aed")
    elements += [audio, audio_t, mix]

    p1 = rect(40, 530, 320, 56, "#ecfeff", "#0e7490")
    p1t = labeled(p1, "拆解动画元素  ·  不再手搓每一帧", size=14, color="#155e75")
    p2 = rect(380, 530, 320, 56, "#ecfeff", "#0e7490")
    p2t = labeled(p2, "编排剧本 / 牌面  ·  不再手动摆格子", size=14, color="#155e75")
    p3 = rect(720, 530, 320, 56, "#ecfeff", "#0e7490")
    p3t = labeled(p3, "BCS CLI  ·  Agent 可直接接入", size=14, color="#155e75")
    elements += [p1, p1t, p2, p2t, p3, p3t]

    doc = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff",
        },
        "files": {},
    }
    root = Path(__file__).resolve().parents[1]
    out = root / "creative-pipeline.excalidraw"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out} ({len(elements)} elements)")

    svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 640" width="1080" height="640" role="img" aria-labelledby="title desc">
  <title id="title">Match-3 Ad Creative Pipeline</title>
  <desc id="desc">片头 Hook 加主体玩法 Gameplay 的素材生产链路：BCS 编排渲染，JSON 转 AE/Blender，ae-c4d-skills 沉淀资产，nanoAuralRuntime 生成音效。</desc>
  <defs>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb"/>
    </marker>
    <marker id="arrow-gold" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#ca8a04"/>
    </marker>
    <marker id="arrow-orange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#ea580c"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#16a34a"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed"/>
    </marker>
  </defs>

  <rect x="0" y="0" width="1080" height="640" fill="#ffffff"/>

  <text x="540" y="36" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="26" font-weight="700" fill="#0f172a">Match-3 Ad Creative Pipeline</text>
  <text x="540" y="64" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="15" fill="#64748b">素材结构 · 片头 Hook  +  主体玩法 Gameplay</text>

  <rect x="40" y="96" width="250" height="268" rx="16" fill="#f8fafc" stroke="#64748b" stroke-width="2" stroke-dasharray="7 5"/>
  <text x="165" y="132" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="16" font-weight="700" fill="#334155">Hook / Intro</text>
  <text x="165" y="158" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="14" fill="#475569">片头批量复刻</text>
  <text x="165" y="210" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="14" fill="#64748b">C-end workflow</text>
  <text x="165" y="232" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="14" fill="#64748b">调 C 端批量生产</text>
  <text x="165" y="274" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" fill="#94a3b8">(not in GitHub)</text>

  <text x="315" y="240" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="28" fill="#94a3b8">+</text>

  <a href="https://dongyuan21.github.io/block-creative-studio/" target="_blank">
    <rect x="340" y="96" width="400" height="268" rx="16" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
    <text x="540" y="132" text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="16" font-weight="700" fill="#1e3a8a">block-creative-studio</text>
    <text x="540" y="158" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="14" fill="#1d4ed8">主体玩法模拟器骨架</text>
    <text x="540" y="202" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="14" fill="#1e3a8a">Import assets</text>
    <text x="540" y="224" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="14" fill="#1e3a8a">Storyboard / 牌面编排</text>
    <text x="540" y="246" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="14" fill="#1e3a8a">3D render  →  Export video</text>
    <text x="540" y="268" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="14" fill="#1e3a8a">CLI for agents</text>
  </a>

  <rect x="780" y="96" width="260" height="70" rx="12" fill="#fef9c3" stroke="#ca8a04" stroke-width="2"/>
  <text x="910" y="124" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" font-weight="700" fill="#854d0e">Render 不够？</text>
  <text x="910" y="144" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" fill="#854d0e">BCS 导出 JSON</text>

  <rect x="780" y="196" width="260" height="70" rx="12" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>
  <text x="910" y="224" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" font-weight="700" fill="#9a3412">Agent 解析 JSON</text>
  <text x="910" y="244" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" fill="#9a3412">→ AE / Blender 工程</text>

  <a href="https://github.com/dongyuan21/ae-c4d-skills" target="_blank">
    <rect x="780" y="296" width="260" height="68" rx="12" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
    <text x="910" y="322" text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="13" font-weight="700" fill="#166534">ae-c4d-skills</text>
    <text x="910" y="344" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" fill="#166534">原子化元素 → 资产回 BCS</text>
  </a>

  <line x1="740" y1="131" x2="778" y2="131" stroke="#ca8a04" stroke-width="2" marker-end="url(#arrow-gold)"/>
  <line x1="910" y1="166" x2="910" y2="194" stroke="#ea580c" stroke-width="2" marker-end="url(#arrow-orange)"/>
  <line x1="910" y1="266" x2="910" y2="294" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>
  <line x1="780" y1="330" x2="742" y2="330" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <text x="760" y="318" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="12" fill="#2563eb">assets 回流</text>

  <a href="https://github.com/dongyuan21/nanoAuralRuntime" target="_blank">
    <rect x="340" y="430" width="400" height="80" rx="14" fill="#f3e8ff" stroke="#7c3aed" stroke-width="2"/>
    <text x="540" y="462" text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="15" font-weight="700" fill="#5b21b6">nanoAuralRuntime</text>
    <text x="540" y="486" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" fill="#6b21a8">面向消除游戏的 Foley / SFX  →  混入成片</text>
  </a>
  <line x1="540" y1="364" x2="540" y2="428" stroke="#7c3aed" stroke-width="2" marker-end="url(#arrow-purple)"/>

  <rect x="40" y="542" width="320" height="56" rx="12" fill="#ecfeff" stroke="#0e7490" stroke-width="1.5"/>
  <text x="200" y="576" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" fill="#155e75">拆解动画元素 · 不再手搓每一帧</text>

  <rect x="380" y="542" width="320" height="56" rx="12" fill="#ecfeff" stroke="#0e7490" stroke-width="1.5"/>
  <text x="540" y="576" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" fill="#155e75">编排剧本 / 牌面 · 不再手动摆格子</text>

  <rect x="720" y="542" width="320" height="56" rx="12" fill="#ecfeff" stroke="#0e7490" stroke-width="1.5"/>
  <text x="880" y="576" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" fill="#155e75">BCS CLI · Agent 可直接接入</text>
</svg>
"""
    svg_path = root / "creative-pipeline.svg"
    svg_path.write_text(svg, encoding="utf-8")
    print(f"wrote {svg_path}")


if __name__ == "__main__":
    main()

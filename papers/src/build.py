"""Build explicitly labelled reading editions from recovered final manuscript text.
All five diagrams are explanatory schematics, not original case screenshots.
"""
from pathlib import Path
import html,json,re,hashlib
from weasyprint import HTML
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent
DATA=json.loads((ROOT/'data.json').read_text(encoding='utf-8'))
E=html.escape
CSS='''
@page {size:A4; margin:19mm 19mm 20mm;
 @top-left{content:"MELO GCS  /  TECHNICAL REPORT";font:8pt "Noto Sans";color:#71808c;letter-spacing:0.8pt;}
 @bottom-left{content:"FINAL TEXT: 2026-09-20  ·  READING EDITION: 2026-10-16";font:7.1pt "Noto Sans";color:#77828a;}
 @bottom-right{content:counter(page);font:9pt "Noto Sans";color:#344854;}
}
@page:first{@top-left{content:none}}
*{box-sizing:border-box}body{margin:0;color:#24323b;font-family:"Noto Serif CJK SC","Noto Serif",serif;font-size:10.7pt;line-height:1.66}
body.en{font-family:"Noto Serif","Noto Serif CJK SC",serif;font-size:10.4pt;line-height:1.55}
p{margin:0 0 8pt;orphans:3;widows:3;text-align:justify;hyphens:none}
h1,h2,h3,.sans{font-family:"Noto Sans CJK SC","Noto Sans",sans-serif;}
h1{font-size:18pt;line-height:1.32;color:#163e50;margin:22pt 0 12pt;padding-top:8pt;border-top:1.1pt solid #b7c7d0;break-after:avoid;bookmark-level:1;}
h2{font-size:12.3pt;line-height:1.4;color:#234c60;margin:15pt 0 7pt;break-after:avoid;bookmark-level:2;}
h3{font-size:10.4pt;line-height:1.5;margin:11pt 0 6pt;break-after:avoid;bookmark-level:none;}
a{color:#225d78;text-decoration:none}.cover{break-after:page}
.kicker{font-family:"Noto Sans",sans-serif;font-size:9pt;letter-spacing:1.2pt;color:#517180;margin:0 0 8pt}
.title{font-size:25pt;line-height:1.27;margin:0 0 11pt;border:0;padding:0;bookmark-level:none;letter-spacing:-.2pt}
.en .title{font-size:23pt}.subtitle{font:13pt "Noto Sans CJK SC","Noto Sans",sans-serif;color:#526570;margin-bottom:12pt}
.authors{font:11pt "Noto Sans",sans-serif;margin-bottom:3pt}.contact{font:8.7pt "Noto Sans CJK SC","Noto Sans",sans-serif;color:#657681;margin-bottom:11pt}
.edition{background:#f0f5f7;border-left:3pt solid #597e90;padding:8pt 10pt;margin:10pt 0 12pt;font-family:"Noto Sans CJK SC","Noto Sans",sans-serif;font-size:8.1pt;line-height:1.48}
.edition strong{font-weight:700;color:#244b5e}.abstract{font-size:9.6pt;line-height:1.48}.abstract h2{font-size:12pt;margin-top:0;bookmark-level:none}.keywords{font-size:8.3pt;line-height:1.5;color:#596c79;text-align:left}
.toc-title{font:10pt "Noto Sans CJK SC","Noto Sans",sans-serif;color:#244b5e;margin:10pt 0 5pt}.toc{font:8.1pt "Noto Sans CJK SC","Noto Sans",sans-serif;line-height:1.65;column-count:2;column-gap:18pt;}
.toc a{display:block;break-inside:avoid;color:#3f5561}.toc a::after{content:leader(dotted) target-counter(attr(href), page);padding-left:5pt}
section{margin:0}.table-title{font-family:"Noto Sans CJK SC","Noto Sans",sans-serif;font-size:9.6pt;color:#254a5d;margin-top:12pt;margin-bottom:5pt;break-after:avoid;text-align:left}
table{break-inside:avoid;border-collapse:collapse;width:100%;table-layout:fixed;font-family:"Noto Sans CJK SC","Noto Sans",sans-serif;font-size:9pt;line-height:1.52;margin:0 0 12pt}
.en table{font-size:8.5pt;line-height:1.45}th{background:#244a5d;color:#fff;font-weight:600;text-align:left;padding:7pt 8pt;vertical-align:top;}td{padding:7pt 8pt;border-bottom:.55pt solid #d2dde3;vertical-align:top;overflow-wrap:break-word}td:first-child{font-weight:500;}th:first-child,td:first-child{width:26%}th:nth-child(2),td:nth-child(2){width:34%}th:nth-child(3),td:nth-child(3){width:40%}tbody tr:nth-child(even){background:#f2f6f8}tr{break-inside:avoid}thead{display:table-header-group}
figure{margin:14pt 0 15pt;break-inside:avoid;border-top:1pt solid #c4d3dc;padding-top:9pt}
.fig-title{font:10.6pt "Noto Sans CJK SC","Noto Sans",sans-serif;color:#1b5066;margin-bottom:7pt}
.fig-note{font:8.4pt "Noto Sans CJK SC","Noto Sans",sans-serif;color:#6a7880;line-height:1.55;margin:7pt 0}
.source-caption{font:8.5pt "Noto Sans CJK SC","Noto Sans",sans-serif;color:#485d69;line-height:1.55;margin-top:7pt;text-align:left}
.source-caption strong{color:#314c5b}.diagram{width:100%;display:block;background:#fbfdfe;border:0}
.references p{font-size:8.8pt;line-height:1.5;text-align:left;margin-bottom:8pt}
'''
class Svg:
    def __init__(self,h):
        self.h=h;self.a=[f'<svg class="diagram" viewBox="0 0 900 {h}" xmlns="http://www.w3.org/2000/svg"><defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#638293"/></marker></defs>']
    def text(self,x,y,lines,size=19,bold=False,color='#344e5d',anchor='middle'):
        if isinstance(lines,str):lines=[lines]
        for k,line in enumerate(lines):
            self.a.append(f'<text x="{x}" y="{y+k*(size+9)}" font-family="Noto Sans CJK SC, Noto Sans, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{E(line)}</text>')
    def box(self,x,y,w,h,title,lines=(),tint='#edf4f8'):
        self.a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{tint}" stroke="#b9ccd6" stroke-width="1.6"/>')
        self.text(x+w/2,y+31,title,20,True)
        self.text(x+w/2,y+63,lines,17)
    def arrow(self,pts,label=None,lxy=None,dash=False):
        path=' '.join(f'{"M" if i==0 else "L"}{x},{y}' for i,(x,y) in enumerate(pts))
        self.a.append(f'<path d="{path}" fill="none" stroke="#638293" stroke-width="2.2" marker-end="url(#arr)" '+('stroke-dasharray="7 5"' if dash else '')+'/>')
        if label and lxy:self.text(*lxy,label,16,color='#667e8c')
    def done(self):return ''.join(self.a)+'</svg>'
def diagram(n,lang):
    z=lang=='zh'
    def T(zh,en):return zh if z else en
    if n==1:
        s=Svg(565)
        s.text(450,25,T('设计师：提出要求、使用工具、审阅结果和决定交付','Designer: brief, use tools, review, and decide delivery'),20,True)
        s.box(265,49,370,95,T('外部 Agent（如 Codex）','External agent (e.g. Codex)'),[T('理解参考、规划、选材与工具调用','Interpret, plan, select, call tools'),T('根据预览和检查反馈修订','Revise from previews and checks')])
        for x in [145,450,755]:s.arrow([(450,144),(450,165),(x,165),(x,183)],dash=True)
        s.box(15,183,260,119,T('专业源工程与工具','Source projects / DCC'),[T('整体工程定向改造','Targeted source edits'),T('适用元素提取与复用','Extract reusable elements'),T('保留原生制作关系','Native authoring relations')])
        s.box(320,183,260,119,'melo-gcs / CLI',[T('玩法记录 · 演出 · 元素关联','Gameplay · timing · assets'),T('原子操作 · 校验 · 保存','Atomic edits · validate · save'),T('Studio 或无头调用','Studio or headless invocation')],tint='#e4f1f5')
        s.box(625,183,260,119,T('元素库','Element library'),[T('来源 · 依赖 · 使用信息','Provenance and dependencies'),T('多模态召回与选材','Multimodal retrieval / selection'),T('绑定到适用项目','Bind to compatible projects')])
        s.arrow([(625,270),(580,270)])
        s.arrow([(450,302),(450,332)])
        s.box(320,332,260,82,'Chromium + GPU',[T('逐帧渲染与视频输出','Render frames and video')])
        s.arrow([(580,373),(625,373)])
        s.box(625,332,260,82,T('设计审阅','Design review'),[T('结果是否满足任务要求','Assess task requirements')])
        s.arrow([(755,414),(755,466)],T('满足','Meets needs'),(821,446))
        s.box(625,466,260,83,T('视频 + 可复用项目','Video + reusable project'),[T('保留项目，继续后续制作','Retain for later production')],tint='#eaf4ee')
        s.box(15,466,430,83,T('AE／Blender 原生工程与视频','Native AE / Blender output'),[T('直接制作，或按需经 Agent + Skill 导入','Direct editing or Agent + Skill import')])
        s.arrow([(145,302),(145,466)],T('直接制作','Direct production'),(225,389))
        s.arrow([(665,414),(665,440),(390,440),(390,466)],T('表现不足：专用导入 Skill','Visuals fall short: dedicated import Skill'),(477,433),dash=True)
        return s.done()
    if n==2:
        s=Svg(550)
        s.text(20,31,T('A  源工程入口','A  Source-project intake'),21,True,anchor='start')
        s.box(20,52,255,90,T('已有 DCC 工程','Existing DCC project'),[T('工程与媒体依赖','Project and media dependencies')])
        s.box(325,52,255,90,T('定向改造','Targeted editing'),[T('在工程副本中修改','Modify a project copy')])
        s.box(630,52,250,90,T('原生渲染与交付','Native rendering / delivery'),[T('可直接完成，无需先转格式','Direct completion is possible')],tint='#eaf4ee')
        s.arrow([(275,97),(325,97)]);s.arrow([(580,97),(630,97)])
        s.text(450,183,T('适用内容可另行拆分入库；完整源工程仍可整体保留','Suitable elements may be extracted; complete projects may remain intact'),17)
        s.text(20,225,T('B  参考视频入口','B  Reference-video intake'),21,True,anchor='start')
        s.box(20,247,255,90,T('参考视频','Reference video'),[T('可见布局、动作与表现','Visible layout, actions, appearance')])
        s.box(325,247,255,90,'Agent + melo-gcs CLI',[T('建立、渲染和修订候选项目','Build, render, compare, revise')])
        s.box(630,247,250,90,T('保存 melo-gcs 项目','Save melo-gcs project'),[T('成为后续变体的起点','Starting point for later variants')])
        s.arrow([(275,292),(325,292)]);s.arrow([(580,292),(630,292)])
        s.arrow([(755,337),(755,379),(170,379),(170,418)])
        s.box(20,418,300,99,T('继续编辑与检查','Edit and check'),[T('外观、布局、动作、节奏','Appearance, layout, actions, pacing'),T('检查玩法与资源','Validate gameplay and resources')])
        s.box(365,418,250,99,'Chromium + GPU',[T('渲染和媒体检查','Render and check media')])
        s.box(660,418,220,99,T('设计审阅与交付','Review and delivery'),[T('不足时按需 DCC 精修','On-demand DCC refinement')])
        s.arrow([(320,467),(365,467)]);s.arrow([(615,467),(660,467)])
        return s.done()
    if n==3:
        s=Svg(350)
        s.box(20,22,250,108,T('已有 AEP 工程','Existing AEP project'),[T('界面框架 · 牌体 · 手势','Interface · tile bodies · gestures'),T('已完成的专业设计','Existing professional design')])
        s.box(20,183,250,95,T('目标布局参考','Target layout reference'),[T('仅提供目标结构要求','Supplies layout requirements only')])
        s.box(325,85,270,147,T('After Effects 定向改造','After Effects edits'),[T('位置与整体轮廓','Positions and overall outline'),T('层级与遮挡关系','Layering and occlusion'),T('保留未受影响的原工程内容','Retain unaffected content')],tint='#e4f1f5')
        s.box(650,108,230,101,T('修改后的 AEP','Modified AEP'),[T('直接由原生工程渲染','Render the native project'),T('视频与可编辑工程','Video and editable project')],tint='#eaf4ee')
        s.arrow([(270,76),(297,76),(297,125),(325,125)])
        s.arrow([(270,230),(297,230),(297,195),(325,195)])
        s.arrow([(595,156),(650,156)])
        s.text(450,325,T('流程示意，不包含原稿图 3 的真实渲染画面','Workflow schematic; original Figure 3 renderings are not reproduced'),18)
        return s.done()
    if n==4:
        s=Svg(405)
        s.box(20,18,250,95,T('A001：已有项目','A001: existing project'),[T('保存前的项目输出','Project output before saving')])
        s.box(325,18,250,95,T('保存 JSON → 重新载入','Save JSON → reload'),[T('同一项目的保存重载检查','Reload the same project')],tint='#e4f1f5')
        s.box(630,18,250,95,T('重载后的输出','Reloaded output'),[T('与保存前抽检帧比较','Compare sampled frames')])
        s.arrow([(270,65),(325,65)]);s.arrow([(575,65),(630,65)])
        s.box(100,151,700,87,T('原稿记录：第 0、58、434 帧的像素比较一致','Reported checks: frames 0, 58, and 434 matched'),[T('结论限于抽检帧；不证明全片一致性或参考重建精度','Limited to those frames; not full-video identity or reconstruction accuracy')],tint='#edf5ef')
        s.arrow([(450,238),(450,281)])
        s.box(60,281,780,105,T('后续变体：改变堆叠，保留牌面、背景和点击顺序','Later variant: edit stacks; keep appearance and click order'),[T('重排棋盘堆叠并调整手势位置','Rearrange board stacks and adjust gesture positions'),T('输出 1080 × 1920 · 30 fps','Export: 1080 × 1920 · 30 fps')])
        return s.done()
    s=Svg(390)
    s.box(115,15,670,86,T('原创透明图案和背景 → 导入、绑定、保存与重载','Original assets → import, bind, save, reload'),[T('通过 melo-gcs 公共 CLI 执行','Executed through the public melo-gcs CLI')])
    s.box(150,144,600,92,T('共享的制作基础','Shared production basis'),[T('36 张牌 · 棋盘布局 · 玩法配置 · 同一 Take','36 tiles · same layout · same gameplay configuration · same Take')],tint='#e4f1f5')
    s.arrow([(450,101),(450,144)])
    s.box(45,283,360,85,T('青绿版本','Teal version'),[T('配色、背景与标题颜色','Motif, background, and title colours')],tint='#edf5f4')
    s.box(495,283,360,85,T('暖珊瑚版本','Warm-coral version'),[T('修改外观，保留玩法与布局','Change appearance; retain play and layout')],tint='#fbf0ed')
    s.arrow([(450,236),(450,258),(225,258),(225,283)])
    s.arrow([(450,236),(450,258),(675,258),(675,283)])
    return s.done()
def fig(n,lang):
    z=lang=='zh'
    title=(['系统角色与交付路径','两类入口与持续制作','源工程布局改造的修改边界','A001 保存重载与后续编辑','原创素材变体：保持与变化'][n-1] if z else ['System roles and delivery paths','Two intake paths and continued production','Editing boundaries for source-project layouts','A001: save, reload, and continue editing','Original-asset variants: preserved and changed content'][n-1])
    label=f'阅读示意 {n} · {title}' if z else f'Reading schematic {n} · {title}'
    note=('根据最终稿正文重绘。不是原始截图，不构成新的实验验证。' if z else 'Redrawn from the final text. Not an original screenshot or a new experimental validation.')
    caplabel=(f'原稿图 {n} 图注（原图未重现）：' if z else f'Original Figure {n} caption (original image not reproduced): ')
    return f'<figure><div class="fig-title">{E(label)}</div>{diagram(n,lang)}<p class="fig-note">{E(note)}</p><p class="source-caption"><strong>{E(caplabel)}</strong>{E(DATA["captions"][lang][n-1])}</p></figure>'
def table(n,lang):
    title,headers,rows=DATA['tables'][lang][n-1]
    prefix=f'表 {n}　' if lang=='zh' else f'Table {n}. '
    return '<div class="table-title">'+E(prefix+title)+'</div><table><thead><tr>'+''.join('<th>'+E(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'
def build(lang):
    z=lang=='zh';meta=DATA['meta'][lang];text=(ROOT/f'{lang}.txt').read_text(encoding='utf-8')
    body=[];toc=[];refs=False;hcount=0
    blocks=re.split(r'\n\n+',re.sub(r'(?m)^(#{1,2} .+)\n(?!\n)',r'\1\n\n',text.strip()))
    for block in blocks:
        block=block.strip()
        if not block:continue
        if block.startswith('## '):body.append('<h2>'+E(block[3:])+'</h2>')
        elif block.startswith('# '):
            hcount+=1;title=block[2:];anchor=f'section-{hcount}'
            if title in ['References','参考文献']:refs=True;body.append('<div class="references">')
            body.append(f'<h1 id="{anchor}">'+E(title)+'</h1>');toc.append(f'<a href="#{anchor}">'+E(title)+'</a>')
        elif re.fullmatch(r'@@TABLE\d@@',block):body.append(table(int(block[-3]),lang))
        elif re.fullmatch(r'@@FIG\d@@',block):body.append(fig(int(block[-3]),lang))
        else:
            p=E(block.replace('\n',' '))
            p=re.sub(r'(https://doi\.org/10\.48550/arXiv\.\d+\.\d+)',r'<a href="\1">\1</a>',p)
            body.append('<p>'+p+'</p>')
    if refs:body.append('</div>')
    note=('<strong>排版与配图说明。</strong>依据 2026 年 9 月 20 日中文定稿恢复正文，保留章节、表格数据、原图图注及限制说明。因原始附件无法完整导出，本版的五幅图均为根据正文重绘的解释性示意图，未复原原始案例截图，也不是对实验结果的新验证。本文件为作者技术报告的重排阅读版，并非 arXiv 公布版。' if z else '<strong>Typesetting and figure note.</strong> This reading edition recovers the text of the final manuscript dated 20 September 2026, retaining its sections, tabulated data, original figure captions, and limitations. Original attachment bytes could not be fully exported. All five figures in this edition are explanatory schematics redrawn from the text, not original case screenshots or new experimental validation. This is a re-typeset reading edition of the authors’ technical report, not an arXiv-published PDF.')
    cover_title=E(meta['title']) if not z else '面向消除类游戏广告素材的<br>可复用生产系统'
    cover=f'''<div class="cover"><div class="kicker">MELO GAME CREATIVE STUDIO / TECHNICAL REPORT</div><h1 class="title">{cover_title}</h1><div class="subtitle">{E(meta['subtitle'])}</div><div class="authors">Dongyuan Li &nbsp;&nbsp; Yuwei Liu</div><div class="contact">{'独立研究人员 · 联系作者' if z else 'Independent Researchers · Contact'}: Dongyuan Li · lzyzsere@gmail.com</div><div class="edition">{note}</div><div class="abstract"><h2>{'摘要' if z else 'Abstract'}</h2><p>{E(meta['abstract'])}</p></div><p class="keywords"><strong>{'关键词' if z else 'Keywords'}:</strong> {E(meta['keywords'])}</p><div class="toc-title">{'目录' if z else 'Contents'}</div><nav class="toc">{''.join(toc)}</nav></div>'''
    page=f'<!DOCTYPE html><html lang="{"zh-CN" if z else "en"}"><head><meta charset="utf-8"><meta name="author" content="Dongyuan Li; Yuwei Liu"><title>{E(meta["title"])} — reading edition</title><style>{CSS}</style></head><body class="{lang}">{cover}{"".join(body)}</body></html>'
    target=OUT/f'melo-gcs-technical-report-{lang}.pdf'
    (OUT/f'melo-gcs-technical-report-{lang}.html').write_text(page,encoding='utf-8')
    HTML(string=page,base_url=str(ROOT)).write_pdf(target)
    print(target.name,target.stat().st_size,'bytes',hashlib.sha256(target.read_bytes()).hexdigest())
    return target
if __name__=='__main__':
    for lang in ['en','zh']:build(lang)

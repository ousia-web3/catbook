from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "nyangnyang-chur-manuscript-v3-complete.md"
WEB_DIR = ROOT / "web"
OUT = WEB_DIR / "manuscript.html"

CHECKLIST_CSS = r"""
      /* 30초 체크 Checklist */
      .checklist-status {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        align-items: center;
        gap: 8px 12px;
        margin: 0 0 12px;
      }

      .checklist-progress {
        color: var(--muted);
        font-size: clamp(0.82rem, 0.78rem + 0.16vw, 0.9rem);
        font-weight: 800;
        line-height: 1.4;
      }

      .checklist-reset {
        min-height: 32px;
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 6px 12px;
        background: var(--surface);
        color: var(--muted);
        font-size: clamp(0.82rem, 0.78rem + 0.16vw, 0.9rem);
        font-weight: 800;
        cursor: pointer;
      }

      .checklist-reset:hover,
      .checklist-reset:focus-visible {
        border-color: rgba(0, 113, 227, 0.35);
        color: var(--accent);
      }

      .checklist-reset:disabled {
        cursor: default;
        opacity: 0.45;
      }

      .checklist-bar {
        grid-column: 1 / -1;
        height: 5px;
        overflow: hidden;
        border-radius: 999px;
        background: rgba(0, 113, 227, 0.12);
      }

      .checklist-bar span {
        display: block;
        width: 0%;
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, var(--accent), #0f766e);
        transition: width 0.2s ease;
      }

      .chapter ul.checklist {
        list-style: none;
        margin: 0 0 28px;
        padding-left: 0;
        display: grid;
        gap: 12px;
      }

      .chapter ul.checklist li {
        padding-left: 0;
      }

      .checklist-item {
        display: grid;
        grid-template-columns: 22px minmax(0, 1fr);
        align-items: start;
        gap: 12px;
        min-height: 48px;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 12px 14px;
        background: rgba(255, 255, 255, 0.86);
        cursor: pointer;
        transition: border-color 0.2s ease, background 0.2s ease;
      }

      .checklist-item:hover {
        border-color: rgba(0, 113, 227, 0.28);
        background: rgba(255, 255, 255, 0.96);
      }

      .checklist-item input {
        width: 20px;
        height: 20px;
        margin: 2px 0 0;
        accent-color: var(--accent);
        cursor: pointer;
      }

      .checklist-item-text {
        min-width: 0;
        color: var(--ink);
        font-size: clamp(0.92rem, 0.86rem + 0.22vw, 1rem);
        font-weight: 650;
        line-height: 1.58;
        word-break: keep-all;
        overflow-wrap: anywhere;
      }

      .chapter ul.checklist li.is-checked .checklist-item {
        border-color: rgba(15, 118, 110, 0.22);
        background: rgba(15, 118, 110, 0.06);
      }

      .chapter ul.checklist li.is-checked .checklist-item-text {
        color: var(--muted);
      }
"""

CONTENT_GUARD_CSS = r"""
      .ai-generated-media {
        position: relative;
        isolation: isolate;
      }

      .ai-generated-media::after {
        content: attr(data-ai-label);
        position: absolute;
        z-index: 2;
        right: 12px;
        bottom: 12px;
        max-width: calc(100% - 24px);
        border: 1px solid rgba(255, 255, 255, 0.38);
        border-radius: 999px;
        padding: 6px 10px;
        background: rgba(28, 30, 33, 0.72);
        color: #ffffff;
        font-size: clamp(0.72rem, 0.68rem + 0.18vw, 0.84rem);
        font-weight: 800;
        line-height: 1.2;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
        pointer-events: none;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
      }

      .ai-generated-media img {
        user-select: none;
        -webkit-user-drag: none;
        -webkit-touch-callout: none;
      }

      @media (max-width: 560px) {
        .ai-generated-media::after {
          right: 10px;
          bottom: 10px;
          padding: 5px 9px;
        }
      }
"""

CHECKLIST_SCRIPT = r"""
    <script>
      const initChecklists = () => {
        const storagePrefix = "nyangnyang-chur:reader-check:v1:";

        const hashText = (value) => {
          let hash = 0;
          for (let index = 0; index < value.length; index += 1) {
            hash = ((hash << 5) - hash + value.charCodeAt(index)) | 0;
          }
          return Math.abs(hash).toString(36);
        };

        const readSaved = (key) => {
          try {
            return window.localStorage.getItem(key) === "1";
          } catch {
            return false;
          }
        };

        const writeSaved = (key, checked) => {
          try {
            if (checked) {
              window.localStorage.setItem(key, "1");
            } else {
              window.localStorage.removeItem(key);
            }
          } catch {
            // 체크 기능은 저장소가 막혀도 현재 화면에서는 계속 동작한다.
          }
        };

        document.querySelectorAll(".chapter h4").forEach((heading) => {
          if (heading.textContent.trim() !== "30초 체크") return;

          const list = heading.nextElementSibling;
          if (!list || list.tagName !== "UL" || list.dataset.checklistReady === "true") return;

          const chapter = heading.closest(".chapter");
          const chapterId = chapter?.id || `chapter-${Date.now()}`;
          const chapterTitle = chapter?.querySelector("h3")?.textContent.trim() || "이 장";
          const items = Array.from(list.children).filter((child) => child.tagName === "LI");
          if (!items.length) return;

          list.classList.add("checklist");
          list.dataset.checklistReady = "true";
          list.setAttribute("aria-label", `${chapterTitle} 30초 체크`);

          const status = document.createElement("div");
          status.className = "checklist-status";

          const progressText = document.createElement("span");
          progressText.className = "checklist-progress";
          progressText.setAttribute("aria-live", "polite");

          const resetButton = document.createElement("button");
          resetButton.className = "checklist-reset";
          resetButton.type = "button";
          resetButton.textContent = "초기화";

          const progressBar = document.createElement("span");
          progressBar.className = "checklist-bar";
          progressBar.setAttribute("aria-hidden", "true");
          const progressFill = document.createElement("span");
          progressBar.append(progressFill);

          status.append(progressText, resetButton, progressBar);
          heading.insertAdjacentElement("afterend", status);

          const checkboxes = items.map((item, itemIndex) => {
            const text = item.textContent.trim();
            const inputId = `${chapterId}-check-${itemIndex + 1}`;
            const storageKey = `${storagePrefix}${chapterId}:${itemIndex}:${hashText(text)}`;

            item.textContent = "";
            const label = document.createElement("label");
            label.className = "checklist-item";
            label.setAttribute("for", inputId);

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.id = inputId;
            checkbox.dataset.storageKey = storageKey;
            checkbox.checked = readSaved(storageKey);

            const textNode = document.createElement("span");
            textNode.className = "checklist-item-text";
            textNode.textContent = text;

            label.append(checkbox, textNode);
            item.append(label);
            item.classList.toggle("is-checked", checkbox.checked);

            checkbox.addEventListener("change", () => {
              item.classList.toggle("is-checked", checkbox.checked);
              writeSaved(storageKey, checkbox.checked);
              updateProgress();
            });

            return checkbox;
          });

          const updateProgress = () => {
            const checkedCount = checkboxes.filter((checkbox) => checkbox.checked).length;
            const total = checkboxes.length;
            const percent = total ? Math.round((checkedCount / total) * 100) : 0;
            progressText.textContent = `${checkedCount}/${total} 완료`;
            progressFill.style.width = `${percent}%`;
            resetButton.disabled = checkedCount === 0;
            resetButton.setAttribute("aria-label", `${chapterTitle} 30초 체크 초기화`);
          };

          resetButton.addEventListener("click", () => {
            checkboxes.forEach((checkbox) => {
              checkbox.checked = false;
              checkbox.closest("li")?.classList.remove("is-checked");
              writeSaved(checkbox.dataset.storageKey, false);
            });
            updateProgress();
          });

          updateProgress();
        });
      };

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initChecklists, { once: true });
      } else {
        initChecklists();
      }
    </script>
"""

CONTENT_GUARD_SCRIPT = r"""
    <script>
      const initContentGuards = () => {
        const generatedImages = Array.from(document.querySelectorAll('img[src*="assets/generated/"]'));

        generatedImages.forEach((image) => {
          const media = image.closest("figure, picture, .chapter-visual") || image.parentElement;
          if (media) {
            media.classList.add("ai-generated-media");
            media.dataset.aiLabel = "AI 생성";
          }

          image.dataset.aiGenerated = "true";
          image.draggable = false;
          image.setAttribute("draggable", "false");
          image.addEventListener("dragstart", (event) => event.preventDefault());
        });

        document.addEventListener("contextmenu", (event) => {
          event.preventDefault();
        });
      };

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initContentGuards, { once: true });
      } else {
        initContentGuards();
      }
    </script>
"""


def slug_chapter(title: str) -> str:
    match = re.match(r"^(\d+)\.", title)
    if match:
        return f"chapter-{match.group(1)}"
    return "chapter"


def flush_list(items: list[str], out: list[str]) -> None:
    if not items:
        return
    out.append("<ul>")
    for item in items:
        out.append(f"<li>{html.escape(item)}</li>")
    out.append("</ul>")
    items.clear()


def render_markdown(md: str) -> tuple[str, list[tuple[str, str]], list[tuple[str, str]]]:
    out: list[str] = []
    list_items: list[str] = []
    parts: list[tuple[str, str]] = []
    chapters: list[tuple[str, str]] = []
    open_article = False
    open_part = False

    for raw_line in md.splitlines():
        line = raw_line.strip()

        if not line or line == "---":
            flush_list(list_items, out)
            continue

        if line.startswith("# "):
            flush_list(list_items, out)
            out.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
        elif line.startswith("## Part"):
            flush_list(list_items, out)
            if open_article:
                out.append("</article>")
                open_article = False
            if open_part:
                out.append("</section>")
            part_title = line[3:].strip()
            part_id = f"part-{len(parts) + 1}"
            parts.append((part_id, part_title))
            out.append(f'<section class="part" id="{part_id}">')
            out.append(f"<h2>{html.escape(part_title)}</h2>")
            open_part = True
        elif line.startswith("## "):
            flush_list(list_items, out)
            out.append(f'<div class="intro-block"><h2>{html.escape(line[3:].strip())}</h2></div>')
        elif line.startswith("### "):
            flush_list(list_items, out)
            if open_article:
                out.append("</article>")
            chapter_title = line[4:].strip()
            chapter_id = slug_chapter(chapter_title)
            chapters.append((chapter_id, chapter_title))
            out.append(f'<article class="chapter" id="{chapter_id}">')
            out.append(f"<h3>{html.escape(chapter_title)}</h3>")
            open_article = True
        elif line.startswith("#### "):
            flush_list(list_items, out)
            heading = line[5:].strip()
            out.append(f"<h4>{html.escape(heading)}</h4>")
        elif line.startswith(">"):
            flush_list(list_items, out)
            quote = line.lstrip(">").strip()
            out.append(f"<blockquote>{html.escape(quote)}</blockquote>")
        elif line.startswith("- "):
            list_items.append(line[2:].strip())
        else:
            flush_list(list_items, out)
            out.append(f"<p>{html.escape(line)}</p>")

    flush_list(list_items, out)
    if open_article:
        out.append("</article>")
    if open_part:
        out.append("</section>")

    return "\n".join(out), parts, chapters


def main() -> None:
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    body_html, parts, chapters = render_markdown(manuscript)

    toc_parts = "\n".join(
        f'<a href="#{part_id}">{html.escape(title.replace("Part ", ""))}</a>'
        for part_id, title in parts
    )
    toc_chapters = "\n".join(
        f'<a href="#{chapter_id}">{html.escape(title)}</a>'
        for chapter_id, title in chapters
    )

    page = f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>냥냥츄르 관찰일지 | 집사용 이야기 노트</title>
    <meta name="description" content="고양이 츄르의 장면을 소설처럼 읽고 집사노트처럼 남기는 42개의 관찰일지" />
    <style>
      :root {{
        --bg: #f5f5f7;
        --surface: #ffffff;
        --ink: #1d1d1f;
        --muted: #6e6e73;
        --line: rgba(29, 29, 31, 0.12);
        --accent: #0071e3;
        --page-x: clamp(18px, 5vw, 64px);
        --reader-text: clamp(1.05rem, 0.98rem + 0.34vw, 1.22rem);
        --reader-lead: clamp(1.06rem, 0.95rem + 0.52vw, 1.34rem);
        --reader-title: clamp(2.35rem, 1.35rem + 4.8vw, 5.25rem);
        --reader-chapter: clamp(1.85rem, 1.2rem + 3vw, 3.6rem);
        --reader-mobile-heading: clamp(0.92rem, 4.3vw, 1.2rem);
      }}

      * {{ box-sizing: border-box; }}

      html {{ scroll-behavior: smooth; }}

      body {{
        margin: 0;
        background: var(--bg);
        color: var(--ink);
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif;
        letter-spacing: 0;
      }}

      a {{ color: inherit; text-decoration: none; }}

      button,
      input,
      textarea,
      select {{ font: inherit; letter-spacing: 0; }}

      .reader-header {{
        position: sticky;
        z-index: 10;
        top: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        min-height: 56px;
        border-bottom: 1px solid var(--line);
        padding: 0 var(--page-x);
        background: rgba(245, 245, 247, 0.82);
        backdrop-filter: blur(20px) saturate(1.2);
      }}

      .reader-header a {{ font-size: clamp(0.88rem, 0.82rem + 0.22vw, 1rem); font-weight: 820; }}

      .reader-shell {{
        display: grid;
        grid-template-columns: minmax(220px, 300px) minmax(0, 780px);
        gap: clamp(34px, 6vw, 96px);
        width: min(1200px, calc(100% - (var(--page-x) * 2)));
        margin: 0 auto;
        padding: clamp(44px, 6vw, 82px) 0 clamp(64px, 8vw, 108px);
      }}

      .reader-strip {{
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: clamp(20px, 5vw, 72px);
        width: min(1200px, calc(100% - (var(--page-x) * 2)));
        margin: 0 auto;
        border-bottom: 1px solid var(--line);
        padding: clamp(42px, 6vw, 76px) 0 clamp(24px, 4vw, 34px);
      }}

      .reader-strip strong {{
        display: block;
        max-width: 12ch;
        font-size: clamp(2rem, 1.2rem + 3.6vw, 4.2rem);
        line-height: 1.06;
        font-weight: 860;
        text-wrap: balance;
        word-break: keep-all;
        overflow-wrap: break-word;
      }}

      .reader-strip span {{
        display: block;
        max-width: 520px;
        color: var(--muted);
        font-size: var(--reader-lead);
        font-weight: 650;
        line-height: 1.7;
        text-wrap: pretty;
        word-break: keep-all;
        overflow-wrap: break-word;
      }}

      .toc {{
        position: sticky;
        top: 84px;
        align-self: start;
        max-height: calc(100vh - 110px);
        overflow: auto;
        border-right: 1px solid var(--line);
        padding-right: 22px;
      }}

      .toc h2 {{
        margin: 0 0 18px;
        font-size: clamp(1rem, 0.92rem + 0.34vw, 1.18rem);
      }}

      .toc-section {{
        display: grid;
        gap: 8px;
        margin-bottom: 24px;
      }}

      .toc a {{
        color: var(--muted);
        font-size: clamp(0.9rem, 0.84rem + 0.22vw, 1rem);
        font-weight: 700;
        line-height: 1.5;
      }}

      .toc a:hover {{ color: var(--accent); }}

      .manuscript {{
        min-width: 0;
      }}

      .manuscript h1 {{
        margin: 0 0 18px;
        max-width: 10ch;
        font-size: var(--reader-title);
        line-height: 1.02;
        font-weight: 860;
        text-wrap: balance;
        word-break: keep-all;
        overflow-wrap: break-word;
      }}

      .manuscript blockquote {{
        margin: 0 0 16px;
        border-left: 3px solid var(--line);
        padding-left: 16px;
        color: var(--muted);
        font-size: var(--reader-lead);
        line-height: 1.74;
      }}

      .intro-block,
      .part,
      .chapter {{
        border-top: 1px solid var(--line);
        scroll-margin-top: 82px;
      }}

      .intro-block {{
        padding: 28px 0 10px;
      }}

      .part {{
        margin-top: 72px;
        padding-top: 42px;
      }}

      .part h2 {{
        margin: 0 0 34px;
        width: 100%;
        max-width: 100%;
        min-width: 0;
        font-size: clamp(2.2rem, 1.3rem + 4vw, 4.5rem);
        line-height: 1.08;
        white-space: nowrap;
        text-wrap: nowrap;
        word-break: keep-all;
        overflow-wrap: normal;
      }}

      .chapter {{
        padding: 46px 0 54px;
      }}

      .chapter h3 {{
        margin: 0 0 24px;
        width: 100%;
        max-width: 100%;
        min-width: 0;
        font-size: var(--reader-chapter);
        line-height: 1.15;
        white-space: nowrap;
        text-wrap: nowrap;
        word-break: keep-all;
        overflow-wrap: normal;
      }}

      .chapter h4 {{
        margin: 34px 0 12px;
        color: var(--accent);
        font-size: clamp(1rem, 0.92rem + 0.25vw, 1.1rem);
      }}

      .manuscript p,
      .manuscript li {{
        color: #2b2b2f;
        font-size: var(--reader-text);
        line-height: 1.92;
        text-wrap: pretty;
      }}

      .manuscript p {{ margin: 0 0 18px; }}

      .manuscript ul {{
        margin: 0 0 24px;
        padding-left: 22px;
      }}

{CHECKLIST_CSS}
{CONTENT_GUARD_CSS}

      .reader-footer {{
        border-top: 1px solid var(--line);
        padding: 28px var(--page-x);
        color: var(--muted);
        font-size: clamp(0.82rem, 0.78rem + 0.16vw, 0.9rem);
        font-weight: 700;
      }}

      @media (max-width: 880px) {{
        .part h2,
        .chapter h3 {{
          font-size: clamp(1.25rem, 4.3vw, 2.15rem);
        }}

        .reader-shell {{
          grid-template-columns: 1fr;
          width: min(760px, calc(100% - (var(--page-x) * 2)));
        }}

        .toc {{
          position: static;
          max-height: none;
          border-right: 0;
          border-bottom: 1px solid var(--line);
          padding-right: 0;
          padding-bottom: 22px;
        }}

        .toc-chapters {{
          display: none;
        }}

        .reader-strip {{
          display: grid;
          align-items: start;
        }}
      }}

      @media (max-width: 560px) {{
        :root {{
          --page-x: 18px;
          --reader-text: clamp(1.02rem, 4.4vw, 1.16rem);
          --reader-lead: clamp(1rem, 4.2vw, 1.18rem);
          --reader-mobile-heading: clamp(0.92rem, 4.3vw, 1.2rem);
        }}

        .reader-header {{
          min-height: 52px;
        }}

        .reader-shell {{
          padding-top: 38px;
        }}

        .toc {{
          display: none;
        }}

        .manuscript h1 {{
          max-width: 9ch;
        }}

        .chapter {{
          padding: 40px 0 48px;
        }}

        .part h2,
        .chapter h3 {{
          font-size: var(--reader-mobile-heading);
          line-height: 1.24;
        }}
      }}

      @media (max-width: 359px) {{
        :root {{
          --reader-mobile-heading: clamp(0.82rem, 4.25vw, 0.96rem);
        }}
      }}
    </style>
  </head>
  <body>
    <header class="reader-header">
      <a href="./index.html">냥냥츄르</a>
      <a href="./nyangnyang-chur-landing-standalone.html">신호별 소개</a>
    </header>
    <section class="reader-strip" aria-label="읽기 안내">
      <strong>츄르의 관찰일지</strong>
      <span>오늘 자꾸 떠오르는 고양이의 신호가 있다면, 그 장부터 펼쳐도 좋다. 한 장은 짧은 이야기와 30초 체크, 집사 메모로 조용히 닫힌다.</span>
    </section>
    <main class="reader-shell">
      <aside class="toc" aria-label="냥냥노트 목차">
        <h2>냥냥노트 목차</h2>
        <nav class="toc-section" aria-label="파트별 신호">
          {toc_parts}
        </nav>
        <nav class="toc-section toc-chapters" aria-label="장면별 노트">
          {toc_chapters}
        </nav>
      </aside>
      <article class="manuscript">
        {body_html}
      </article>
    </main>
    <footer class="reader-footer">냥냥츄르 집사용 이야기 노트</footer>
{CONTENT_GUARD_SCRIPT}
{CHECKLIST_SCRIPT}
  </body>
</html>
"""

    OUT.write_text(page, encoding="utf-8")
    print({"output": str(OUT), "parts": len(parts), "chapters": len(chapters), "characters": len(page)})


if __name__ == "__main__":
    main()

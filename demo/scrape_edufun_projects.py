#!/usr/bin/env python3
"""Scrape all AI20K Demo Day projects from demo.edufun.ai."""

from __future__ import annotations

import html as html_lib
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://demo.edufun.ai"
COHORT = "Cohort 3"
USER_AGENT = "Mozilla/5.0 (compatible; AIEnginnerCatalog/1.0)"


@dataclass
class ProjectCard:
    slug: str
    url: str
    title: str
    short_description: str
    team: str
    members: str
    issue_number: str | None = None


@dataclass
class ProjectDetail(ProjectCard):
    full_description: str = ""
    demo_url: str | None = None
    video_url: str | None = None
    slide_url: str | None = None
    tags: list[str] | None = None


def fetch(url: str, retries: int = 3) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError) as exc:
            last_err = exc
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_err}")


def strip_tags(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_homepage_cards(page_html: str) -> list[ProjectCard]:
    cards: list[ProjectCard] = []
    seen: set[str] = set()

    for match in re.finditer(
        r'<a[^>]+href="(/p/[^"#?]+)"[^>]*>([\s\S]*?)</a>',
        page_html,
        flags=re.I,
    ):
        slug_path = match.group(1)
        if slug_path in seen:
            continue
        seen.add(slug_path)

        block = match.group(2)
        slug = slug_path.removeprefix("/p/")

        issue_match = re.search(r"№\s*(\d+)", block)
        issue_number = issue_match.group(1) if issue_match else None

        title_match = re.search(r"<h3[^>]*>([\s\S]*?)</h3>", block, flags=re.I)
        title = strip_tags(title_match.group(1)) if title_match else slug

        desc_match = re.search(
            r'<p[^>]*font-size:13\.5px[^>]*>([\s\S]*?)</p>',
            block,
            flags=re.I,
        )
        short_description = strip_tags(desc_match.group(1)) if desc_match else ""

        team_match = re.search(
            r'font-size:12px;text-transform:uppercase[^>]*>([^<]+)</span>',
            block,
            flags=re.I,
        )
        team = strip_tags(team_match.group(1)) if team_match else ""

        members_match = re.search(
            r'class="line-clamp-1"[^>]*style="[^"]*opacity:0\.7[^"]*"[^>]*>([\s\S]*?)</p>',
            block,
            flags=re.I,
        )
        members = strip_tags(members_match.group(1)) if members_match else ""

        cards.append(
            ProjectCard(
                slug=slug,
                url=f"{BASE_URL}{slug_path}",
                title=title,
                short_description=short_description,
                team=team,
                members=members,
                issue_number=issue_number,
            )
        )

    return cards


def parse_json_ld(page_html: str) -> dict | None:
    for match in re.finditer(
        r'<script type="application/ld\+json">(.*?)</script>',
        page_html,
        flags=re.I | re.S,
    ):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "CreativeWork":
            return data
    return None


def clean_description(text: str) -> str:
    text = re.sub(
        r"^(?:Facebook X LinkedIn Telegram Copy link\s*)+",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_links(page_html: str) -> tuple[str | None, str | None, str | None]:
    demo_url = video_url = slide_url = None

    sidebar_match = re.search(r"Đường dẫn</p>([\s\S]*?)</div>\s*<div>\s*<div style=\"border-top", page_html, flags=re.I)
    sidebar = sidebar_match.group(1) if sidebar_match else page_html

    link_map = {
        "demo_url": r">Demo\s*→<",
        "video_url": r">Video\s*→<",
        "slide_url": r">Slide\s*→<",
    }
    for key, label_pattern in link_map.items():
        m = re.search(rf'href="(https?://[^"]+)"[^>]*{label_pattern}', sidebar, flags=re.I)
        if m:
            if key == "demo_url":
                demo_url = m.group(1)
            elif key == "video_url":
                video_url = m.group(1)
            else:
                slide_url = m.group(1)

    appendix_match = re.search(r"Phụ lục — Demo &amp; Slides([\s\S]*?)</section>", page_html, flags=re.I)
    appendix = appendix_match.group(1) if appendix_match else ""

    if not video_url:
        m = re.search(r'<iframe[^>]+src="(https?://(?:www\.)?youtube[^"]+)"', appendix, flags=re.I)
        if m:
            video_url = m.group(1)
    if not demo_url:
        m = re.search(r'Bản demo trực tiếp[\s\S]{0,400}?<iframe[^>]+src="(https?://[^"]+)"', appendix, flags=re.I)
        if m:
            demo_url = m.group(1)
    if not slide_url:
        m = re.search(r'Slide trình bày[\s\S]{0,400}?<a[^>]+href="(https?://[^"]+)"', appendix, flags=re.I)
        if m:
            slide_url = m.group(1)

    return demo_url, video_url, slide_url


def infer_tags(text: str) -> list[str]:
    keywords = {
        "RAG": r"\bRAG\b|retrieval",
        "Agent": r"\bAgent\b|LangGraph|multi-agent|Multi-Agent",
        "Computer Vision": r"computer vision|thị giác|YOLO|camera|CV\b|LiDAR|2D|3D",
        "Voice/Speech": r"giọng nói|STT|TTS|speech|voice",
        "Healthcare": r"y tế|bác sĩ|bệnh nhân|health|medical|clinical|thuốc|dinh dưỡng",
        "Fintech": r"ví điện tử|tín dụng|gian lận|fraud|AML|ngân hàng|thanh toán",
        "EV/Mobility": r"xe điện|VinFast|sạc|trạm sạc|EV\b|lái thử",
        "Legal/Compliance": r"pháp luật|hợp đồng|compliance|quy chế|luật",
        "Recruitment/HR": r"tuyển dụng|CV|JD|HR\b|phỏng vấn",
        "Education": r"sinh viên|giáo dục|tuyển sinh|học|STEM",
        "Data Engineering": r"data lineage|dbt|OpenMetadata|data quality|catalog|profiling",
        "Security": r"an ninh|SOC|red team|pentest|OWASP|bảo mật",
        "Robotics": r"robot|AMR|AGV|VLA|ROS|MuJoCo|Franka",
        "Smart Home/IoT": r"nhà thông minh|smart home|cư dân|IoT",
        "Observability/MLOps": r"observability|monitor|eval|benchmark|MLOps",
        "Real Estate": r"bất động sản|cho thuê|nhà|căn hộ",
        "Customer Support": r"CSKH|helpdesk|ticket|khiếu nại",
    }
    tags: list[str] = []
    lower = text.lower()
    for tag, pattern in keywords.items():
        if re.search(pattern, text, flags=re.I) or re.search(pattern, lower, flags=re.I):
            tags.append(tag)
    return tags


def parse_detail_page(card: ProjectCard) -> ProjectDetail:
    page_html = fetch(card.url)
    ld = parse_json_ld(page_html)

    short_description = card.short_description
    if ld and ld.get("description"):
        short_description = clean_description(ld["description"])

    desc_parts: list[str] = []
    for m in re.finditer(r"<p[^>]*>([\s\S]*?)</p>", page_html, flags=re.I):
        txt = clean_description(strip_tags(m.group(1)))
        if len(txt) < 80:
            continue
        if txt in {short_description, card.short_description}:
            continue
        if re.search(r"graph TD|subgraph|^\+\-+\+", txt):
            continue
        if "Facebook X LinkedIn" in txt and len(txt) < 300:
            continue
        desc_parts.append(txt)

    full_description = short_description
    if desc_parts:
        full_description = max(desc_parts, key=len)

    demo_url, video_url, slide_url = extract_links(page_html)
    combined = " ".join([card.title, short_description, full_description])
    tags = infer_tags(combined)

    return ProjectDetail(
        slug=card.slug,
        url=card.url,
        title=(ld or {}).get("name") or card.title,
        short_description=short_description,
        team=card.team,
        members=card.members,
        issue_number=card.issue_number,
        full_description=full_description,
        demo_url=demo_url,
        video_url=video_url,
        slide_url=slide_url,
        tags=tags,
    )


def write_markdown(projects: list[ProjectDetail], out_path: Path) -> None:
    lines: list[str] = [
        "# AI20K Demo Day — Danh mục dự án (Cohort 3)",
        "",
        f"> Nguồn: [{BASE_URL}]({BASE_URL})",
        f"> Tổng số dự án: **{len(projects)}**",
        f"> Cập nhật: auto-scrape",
        "",
        "## Mục lục theo tag",
        "",
    ]

    tag_index: dict[str, list[str]] = {}
    for p in projects:
        for tag in p.tags or ["Khác"]:
            tag_index.setdefault(tag, []).append(p.title)

    for tag in sorted(tag_index):
        titles = ", ".join(f"[{t}](#{slugify(t)})" for t in tag_index[tag][:8])
        extra = f" (+{len(tag_index[tag]) - 8} khác)" if len(tag_index[tag]) > 8 else ""
        lines.append(f"- **{tag}** ({len(tag_index[tag])}): {titles}{extra}")

    lines.extend(["", "---", ""])

    for p in sorted(projects, key=lambda x: (x.issue_number or "999", x.title)):
        anchor = slugify(p.title)
        lines.extend(
            [
                f"## {p.title} {{#{anchor}}}",
                "",
                f"- **URL**: [{p.url}]({p.url})",
                f"- **Số**: № {p.issue_number}" if p.issue_number else "- **Số**: —",
                f"- **Đội**: {p.team or '—'}",
                f"- **Thành viên**: {p.members or '—'}",
                f"- **Tags**: {', '.join(p.tags) if p.tags else '—'}",
            ]
        )
        if p.demo_url:
            lines.append(f"- **Demo**: [{p.demo_url}]({p.demo_url})")
        if p.video_url:
            lines.append(f"- **Video**: [{p.video_url}]({p.video_url})")
        if p.slide_url:
            lines.append(f"- **Slide**: [{p.slide_url}]({p.slide_url})")
        lines.extend(["", "### Mô tả ngắn", "", p.short_description or "—", ""])
        if p.full_description and p.full_description != p.short_description:
            lines.extend(["### Mô tả chi tiết", "", p.full_description, ""])
        lines.append("---")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text[:80]


def main() -> int:
    demo_dir = Path(__file__).resolve().parent
    out_md = demo_dir / "ai20k-demo-day-projects.md"
    out_json = demo_dir / "ai20k-demo-day-projects.json"
    demo_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching homepage...")
    homepage = fetch(BASE_URL + "/")
    cards = parse_homepage_cards(homepage)
    print(f"Found {len(cards)} project cards")

    if not cards:
        print("No projects found — aborting", file=sys.stderr)
        return 1

    projects: list[ProjectDetail] = []
    errors: list[str] = []

    print("Fetching detail pages...")
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(parse_detail_page, card): card for card in cards}
        for i, future in enumerate(as_completed(futures), 1):
            card = futures[future]
            try:
                projects.append(future.result())
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{card.slug}: {exc}")
                projects.append(
                    ProjectDetail(**asdict(card), full_description=card.short_description, tags=infer_tags(card.short_description))
                )
            if i % 25 == 0 or i == len(cards):
                print(f"  {i}/{len(cards)} done")

    projects.sort(key=lambda x: (int(x.issue_number) if x.issue_number else 999, x.title))

    write_markdown(projects, out_md)
    out_json.write_text(
        json.dumps([asdict(p) for p in projects], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {out_md}")
    print(f"Wrote {out_json}")
    if errors:
        print(f"Warnings: {len(errors)} pages had fetch/parse issues", file=sys.stderr)
        for err in errors[:5]:
            print(f"  - {err}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from bs4 import BeautifulSoup, SoupStrainer
from livereload import Server as LiveReloadServer

# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class BlogConfig:
    site_title: str
    site_url: str
    site_base_path: str
    site_description: str
    author: str
    content_dir: Path
    assets_dir: Path
    config_file: Path
    out_dir: Path
    feed_dirs: set[Path]


cfg = BlogConfig(
    site_title="Peoxin's Blog",
    site_url="https://peoxin.github.io/blog",
    site_base_path="/blog",
    site_description="Personal blog by peoxin",
    author="peoxin",
    content_dir=Path("content"),
    assets_dir=Path("assets"),
    config_file=Path("content/config.typ"),
    out_dir=Path("_site"),
    feed_dirs={Path("post")},
)

# ============================================================================
# Dependency Graph
# ============================================================================


@dataclass(slots=True)
class DependencyGraph:
    pages: set[Path]
    direct_deps: dict[Path, set[Path]]
    reverse_deps: dict[Path, set[Path]]

    @classmethod
    def build(cls, typ_files: list[Path]) -> "DependencyGraph":
        pages = {path.resolve() for path in typ_files}
        direct_deps: dict[Path, set[Path]] = {}
        reverse_deps: dict[Path, set[Path]] = defaultdict(set)

        for typ_file in pages:
            deps = set(find_typ_dependencies(typ_file))
            direct_deps[typ_file] = deps
            for dep in deps:
                reverse_deps[dep].add(typ_file)

        return cls(
            pages=pages, direct_deps=direct_deps, reverse_deps=dict(reverse_deps)
        )

    def all_dependencies(self, typ_file: Path) -> set[Path]:
        """All dependencies of a .typ file, including transitive ones."""
        abs_path = typ_file.resolve()
        visited: set[Path] = set()
        stack = list(self.direct_deps.get(abs_path, set()))

        while stack:
            dep = stack.pop()
            if dep in visited:
                continue
            visited.add(dep)
            stack.extend(self.direct_deps.get(dep, set()))

        return visited

    def pages_depending_on(self, path: Path) -> set[Path]:
        """All pages that depend on a given file, directly or indirectly."""
        abs_path = path.resolve()
        affected: set[Path] = set()
        queue = [abs_path]
        seen = {abs_path}

        if abs_path in self.pages:
            affected.add(abs_path)

        while queue:
            current = queue.pop()
            for dependent in self.reverse_deps.get(current, set()):
                if dependent in seen:
                    continue
                seen.add(dependent)
                queue.append(dependent)
                if dependent in self.pages:
                    affected.add(dependent)

        return affected

    def pages_for_resource(self, resource_path: Path) -> set[Path]:
        """All pages in the same directory as the resource, for content assets."""
        resource_dir = resource_path.resolve().parent
        return {page for page in self.pages if page.parent == resource_dir}

    def affected_pages(self, changed_paths: set[Path]) -> set[Path]:
        """All pages affected by the change of given files."""
        affected: set[Path] = set()
        project_root = Path(__file__).parent.resolve()
        config_path = (project_root / cfg.config_file).resolve()
        content_root = (project_root / cfg.content_dir).resolve()

        for path in changed_paths:
            resolved = path.resolve()

            if resolved == config_path:
                affected.update(self.pages)
                continue

            if resolved.suffix == ".typ":
                if resolved.exists() and resolved not in self.pages:
                    affected.add(resolved)
                affected.update(self.pages_depending_on(resolved))
                continue

            if content_root in resolved.parents:
                affected.update(self.pages_for_resource(resolved))

        return affected


@lru_cache(maxsize=None)
def find_typ_dependencies(typ_file: Path) -> frozenset[Path]:
    dependencies: set[Path] = set()

    try:
        content = typ_file.read_text(encoding="utf-8")
    except Exception:
        return frozenset(dependencies)

    base_dir = typ_file.parent
    patterns = [
        r'#import\s+"([^"]+)"',
        r"#import\s+'([^']+)'",
        r'#include\s+"([^"]+)"',
        r"#include\s+'([^']+)'",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content):
            dep_path_str = match.group(1)

            # Skip package imports (e.g., @preview/xxx)
            if dep_path_str.startswith("@"):
                continue

            if dep_path_str.startswith("/"):
                dep_path = Path(dep_path_str.lstrip("/"))  # absolute path
            else:
                dep_path = base_dir / dep_path_str  # relative path

            # Only track .typ files, ignore other resources handled by copy_content_assets
            try:
                dep_path = dep_path.resolve()
                if dep_path.exists() and dep_path.suffix == ".typ":
                    dependencies.add(dep_path)
            except Exception:
                pass

    return frozenset(dependencies)


def find_typ_files() -> list[Path]:
    """Find all .typ files under the content directory."""
    typ_files = []
    for typ_file in cfg.content_dir.rglob("*.typ"):
        # Exclude hidden files
        parts = typ_file.relative_to(cfg.content_dir).parts
        if not any(part.startswith("_") for part in parts):
            typ_files.append(typ_file)
    return typ_files


_dependency_graph_cache: DependencyGraph | None = None


def get_dependency_graph(force_rebuild: bool = False) -> DependencyGraph:
    global _dependency_graph_cache, _dependency_graph_dirty

    if force_rebuild or _dependency_graph_cache is None:
        _dependency_graph_cache = DependencyGraph.build(find_typ_files())
        _dependency_graph_dirty = False

    return _dependency_graph_cache


# ============================================================================
# Live Preview Server
# ============================================================================


def get_file_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except Exception:
        return 0.0


def snapshot_source_files() -> dict[Path, float]:
    paths: set[Path] = set()

    if cfg.content_dir.exists():
        for item in cfg.content_dir.rglob("*"):
            if item.is_file():
                paths.add(item.resolve())

    if cfg.assets_dir.exists():
        for item in cfg.assets_dir.rglob("*"):
            if item.is_file():
                paths.add(item.resolve())

    if cfg.config_file.exists():
        paths.add(cfg.config_file.resolve())

    return {path: get_file_mtime(path) for path in paths}


def detect_changed_paths(
    previous: dict[Path, float], current: dict[Path, float]
) -> set[Path]:
    changed = set()

    for path, mtime in current.items():
        if previous.get(path) != mtime:
            changed.add(path)

    for path in previous:
        if path not in current:
            changed.add(path)

    return changed


def preview(port: int = 8000) -> bool:
    build()

    graph = get_dependency_graph(force_rebuild=True)
    previous_snapshot = snapshot_source_files()

    def rebuild_on_change() -> None:
        nonlocal graph, previous_snapshot

        current_snapshot = snapshot_source_files()
        changed_paths = detect_changed_paths(previous_snapshot, current_snapshot)

        if not changed_paths:
            return

        previous_snapshot = current_snapshot

        try:
            config_path = cfg.config_file.resolve()
            if any(path.resolve() == config_path for path in changed_paths):
                build()

            else:
                affected_pages = graph.affected_pages(changed_paths)
                if not affected_pages:
                    return

                def normalize_content_path(path: Path) -> Path:
                    project_root = Path(__file__).parent.resolve()
                    resolved = path.resolve()
                    try:
                        return resolved.relative_to(project_root)
                    except ValueError:
                        return path

                html_pages = [
                    normalize_content_path(page)
                    for page in affected_pages
                    if "pdf" not in page.stem.lower()
                ]
                pdf_pages = [
                    normalize_content_path(page)
                    for page in affected_pages
                    if "pdf" in page.stem.lower()
                ]

                if html_pages:
                    build_html(files=html_pages)

                if pdf_pages:
                    build_pdf(files=pdf_pages)

                assets_changed = any(
                    path.resolve().is_relative_to(cfg.assets_dir.resolve())
                    for path in changed_paths
                )
                content_resource_changed = any(
                    path.resolve().suffix != ".typ"
                    and path.resolve().is_relative_to(cfg.content_dir.resolve())
                    for path in changed_paths
                )

                if assets_changed:
                    copy_assets()
                if content_resource_changed:
                    copy_content_assets()

            generate_sitemap()
            generate_robots_txt()
            generate_rss()

        except Exception:
            import traceback

            traceback.print_exc()

    server = LiveReloadServer()
    server.watch(str(cfg.content_dir), rebuild_on_change)
    server.watch(str(cfg.assets_dir), rebuild_on_change)
    if cfg.config_file.exists():
        server.watch(str(cfg.config_file), rebuild_on_change)

    print(f"Preview starting at http://localhost:{port}")
    try:
        server.serve(
            host="127.0.0.1",
            port=port,
            open_url=True,
            root=str(cfg.out_dir),
        )
        return True
    except KeyboardInterrupt:
        return True
    except Exception as e:
        print(f"Preview server error: {e}")
        return False


# ============================================================================
# SEO & RSS
# ============================================================================


def inject_seo_rss_tags(output_html: Path) -> bool:
    def parse_html_metadata(soup: BeautifulSoup) -> dict[str, str]:
        metadata: dict[str, str] = {"title": ""}

        if soup.title and soup.title.string:
            metadata["title"] = soup.title.string

        if meta_description := soup.find("meta", attrs={"name": "description"}):
            metadata["description"] = meta_description.get("content", "")

        return metadata

    def html_url_path(path: Path) -> str:
        rel_path = path.relative_to(cfg.out_dir).as_posix()
        if rel_path == "index.html":
            return ""
        if rel_path.endswith("/index.html"):
            return rel_path.removesuffix("index.html")
        if rel_path.endswith(".html"):
            return rel_path.removesuffix(".html") + "/"
        return rel_path

    def canonical_url(site_url: str | None, path: Path) -> str | None:
        if not site_url:
            return None
        url_path = html_url_path(path)
        base = site_url.rstrip("/")
        if not url_path:
            return f"{base}/"
        return f"{base}/{url_path.lstrip('/')}"

    if not output_html.exists():
        return False

    try:
        html_text = output_html.read_text(encoding="utf-8")
        soup = BeautifulSoup(html_text, "lxml")
        if soup.head is None:
            return False

        # Extract all info from HTML head (set by Typst)
        metadata = parse_html_metadata(soup)
        title = metadata.get("title", "").strip()
        description = metadata.get("description", "").strip()
        author = cfg.author or ""
        site_title = cfg.site_title
        site_url = cfg.site_url or None
        canonical = canonical_url(site_url, output_html)

        is_home = html_url_path(output_html) == ""
        og_type = "website" if is_home else "article"

        # Clean up old SEO-related tags before adding new ones
        property_tags = {
            "og:title",
            "og:type",
            "og:description",
            "og:site_name",
            "og:url",
            "article:author",
        }
        name_tags = {
            "twitter:card",
            "twitter:title",
        }

        for meta in list(soup.head.find_all("meta")):
            name = (meta.get("name") or "").strip().lower()
            prop = (meta.get("property") or "").strip().lower()
            if name in name_tags or prop in property_tags:
                meta.decompose()

        for link in list(soup.head.find_all("link")):
            rel = link.get("rel") or []
            rel_set = {str(r).lower() for r in rel}
            if "canonical" in rel_set:
                link.decompose()
                continue
            if (
                "alternate" in rel_set
                and (link.get("type") or "").lower() == "application/rss+xml"
            ):
                link.decompose()

        def append_meta(
            *, name: str | None = None, prop: str | None = None, content: str
        ) -> None:
            tag = soup.new_tag("meta")
            if name is not None:
                tag["name"] = name
            if prop is not None:
                tag["property"] = prop
            tag["content"] = content
            soup.head.append(tag)

        def append_link(
            *,
            rel: str,
            href: str,
            type_value: str | None = None,
            title_value: str | None = None,
        ) -> None:
            tag = soup.new_tag("link")
            tag["rel"] = rel
            tag["href"] = href
            if type_value is not None:
                tag["type"] = type_value
            if title_value is not None:
                tag["title"] = title_value
            soup.head.append(tag)

        # Add RSS link
        if cfg.feed_dirs:
            rss_title = site_title or title
            append_link(
                rel="alternate",
                href=f"{cfg.site_base_path}/feed.xml" if args.deploy else "/feed.xml",
                type_value="application/rss+xml",
                title_value=f"{rss_title} RSS Feed",
            )

        # Add canonical link
        if canonical:
            append_link(rel="canonical", href=canonical)

        # Add OG tags
        if title:
            append_meta(prop="og:title", content=title)
        append_meta(prop="og:type", content=og_type)

        if description:
            append_meta(prop="og:description", content=description)

        if site_title:
            append_meta(prop="og:site_name", content=site_title)

        if canonical:
            append_meta(prop="og:url", content=canonical)

        if author and og_type == "article":
            append_meta(prop="article:author", content=author)

        # Add twitter card tags
        append_meta(name="twitter:card", content="summary")
        if title:
            append_meta(name="twitter:title", content=title)

        output_html.write_text(str(soup), encoding="utf-8")
        return True
    except Exception as e:
        print(f"SEO/RSS tag injection failed: {e}")
        return False


def _append_xml_text_tag(soup: BeautifulSoup, parent, name: str, text: str) -> None:
    tag = soup.new_tag(name)
    tag.string = text
    parent.append(tag)


def _render_xml_document(soup: BeautifulSoup) -> str:
    xml_str = soup.prettify(formatter="minimal")
    if xml_str.lstrip().startswith("<?xml"):
        xml_str = xml_str.lstrip().split("\n", 1)[1]
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'


@dataclass(slots=True)
class PostMetadata:
    title: str
    description: str
    link: str
    pub_date: datetime | None
    mod_date: datetime | None
    category: str


def extract_post_metadata(index_html: Path) -> PostMetadata:
    soup = BeautifulSoup(
        index_html.read_text(encoding="utf-8"), "lxml", parse_only=SoupStrainer("head")
    )

    def get_pub_date():
        meta = soup.find("meta", attrs={"name": "pub-date"})
        if not meta:
            return None

        try:
            content = meta.get("content", "").split("T")[0]
            return datetime.strptime(content, "%Y-%m-%d")
        except Exception:
            return None

    def get_mod_date():
        meta = soup.find("meta", attrs={"name": "mod-date"})
        if not meta:
            return None

        try:
            content = meta.get("content", "").split("T")[0]
            return datetime.strptime(content, "%Y-%m-%d")
        except Exception:
            return None

    def get_link():
        canonical = soup.find("link", rel=lambda rel: rel and "canonical" in rel)
        if canonical:
            return canonical.get("href", "").strip()
        else:
            return ""

    return PostMetadata(
        title=soup.title.string,
        description="",
        link=get_link(),
        pub_date=get_pub_date(),
        mod_date=get_mod_date(),
        category="Blog",
    )


def build_rss_xml(posts: list[PostMetadata]) -> str:
    from email.utils import format_datetime

    ATOM_NS = "http://www.w3.org/2005/Atom"

    soup = BeautifulSoup(features="xml")
    rss = soup.new_tag("rss", version="2.0")
    rss["xmlns:atom"] = ATOM_NS
    soup.append(rss)

    channel = soup.new_tag("channel")
    rss.append(channel)

    _append_xml_text_tag(soup, channel, "title", cfg.site_title)
    _append_xml_text_tag(soup, channel, "link", cfg.site_url)
    _append_xml_text_tag(soup, channel, "description", cfg.site_description)
    _append_xml_text_tag(soup, channel, "language", "zh")
    _append_xml_text_tag(
        soup, channel, "lastBuildDate", format_datetime(datetime.now(timezone.utc))
    )

    atom_link = soup.new_tag(
        "atom:link",
        href=f"{cfg.site_url}/feed.xml",
        rel="self",
        type="application/rss+xml",
    )
    channel.append(atom_link)

    for post in posts:
        item = soup.new_tag("item")
        channel.append(item)

        _append_xml_text_tag(soup, item, "title", post.title)
        _append_xml_text_tag(soup, item, "link", post.link)
        guid = soup.new_tag("guid", isPermaLink="true")
        guid.string = post.link
        item.append(guid)
        _append_xml_text_tag(
            soup,
            item,
            "pubDate",
            format_datetime(post.pub_date)
            if post.pub_date
            else format_datetime(datetime.now(timezone.utc)),
        )
        _append_xml_text_tag(soup, item, "category", post.category)

        if des := post.description:
            _append_xml_text_tag(soup, item, "description", des)

    return _render_xml_document(soup)


def generate_rss() -> bool:
    dirs = set(cfg.feed_dirs)
    if not dirs:
        print("No feed directories configured, skipping RSS generation")
        return True

    html_dirs = [cfg.out_dir / d for d in dirs]
    posts = sorted(
        [extract_post_metadata(f) for d in html_dirs for f in d.rglob("index.html")],
        key=lambda x: x.pub_date or datetime.min if x else datetime.min,
        reverse=True,
    )
    if not posts:
        print("No posts found for RSS feed, skipping generation")
        return True

    try:
        rss_content = build_rss_xml(posts)
        rss_file = cfg.out_dir / "feed.xml"
        rss_file.write_text(rss_content, encoding="utf-8")
        print("Generated RSS feed.xml")
        return True
    except Exception as e:
        print(f"Generate RSS failed: {e}")
        return False


def generate_sitemap() -> bool:
    sitemap_path = cfg.out_dir / "sitemap.xml"
    sitemap_ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    site_url = cfg.site_url

    soup = BeautifulSoup(features="xml")
    urlset = soup.new_tag("urlset")
    urlset["xmlns"] = sitemap_ns
    soup.append(urlset)

    for file_path in sorted(cfg.out_dir.rglob("*.html")):
        rel_path = file_path.relative_to(cfg.out_dir).as_posix()

        if rel_path == "index.html":
            url_path = ""
        elif rel_path.endswith("/index.html"):
            url_path = rel_path.removesuffix("index.html")
        elif rel_path.endswith(".html"):
            url_path = rel_path.removesuffix(".html") + "/"
        else:
            url_path = rel_path

        full_url = f"{site_url}/{url_path}"

        mtime = file_path.stat().st_mtime
        lastmod = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

        url_elem = soup.new_tag("url")
        urlset.append(url_elem)
        _append_xml_text_tag(soup, url_elem, "loc", full_url)
        _append_xml_text_tag(soup, url_elem, "lastmod", lastmod)

    sitemap_content = _render_xml_document(soup)

    try:
        sitemap_path.write_text(sitemap_content, encoding="utf-8")
        print("Generated sitemap.xml")
        return True
    except Exception as e:
        print(f"Generate sitemap.xml failed: {e}")
        return False


def generate_robots_txt() -> bool:
    robots_content = f"""User-agent: *
Allow: /

Sitemap: {cfg.site_url}/sitemap.xml
"""

    try:
        (cfg.out_dir / "robots.txt").write_text(robots_content, encoding="utf-8")
        print("Generated robots.txt")
        return True
    except Exception as e:
        print(f"Generate robots.txt failed: {e}")
        return False


# ============================================================================
# Build Functions
# ============================================================================


def clean() -> bool:
    if not cfg.out_dir.exists():
        return True

    try:
        shutil.rmtree(cfg.out_dir)
        print("Clean task completed")
        return True
    except Exception as e:
        print(f"Clean task failed: {e}")
        return False


def copy_assets() -> bool:
    if not cfg.assets_dir.exists():
        return True

    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    try:
        target_dir = cfg.out_dir / "assets"
        shutil.copytree(cfg.assets_dir, target_dir, dirs_exist_ok=True)
        return True
    except Exception as e:
        print(f"Copying assets failed: {e}")
        return False


def copy_content_assets() -> bool:
    if not cfg.content_dir.exists():
        return True

    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    try:
        for item in cfg.content_dir.rglob("*"):
            if item.is_dir() or item.suffix == ".typ":
                continue

            relative_path = item.relative_to(cfg.content_dir)
            if any(part.startswith("_") for part in relative_path.parts):
                continue

            target_path = cfg.out_dir / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_path)

        return True
    except Exception as e:
        print(f"Copying content assets failed: {e}")
        return False


@dataclass
class BuildStats:
    success: int = 0
    skipped: int = 0
    failed: int = 0

    def format_summary(self) -> str:
        parts = []
        if self.success > 0:
            parts.append(f"Success {self.success}")
        if self.skipped > 0:
            parts.append(f"Skipped {self.skipped}")
        if self.failed > 0:
            parts.append(f"Failed {self.failed}")
        return ", ".join(parts) if parts else "No files processed"

    @property
    def has_failures(self) -> bool:
        return self.failed > 0


def run_typst_command(args: list[str]) -> bool:
    try:
        result = subprocess.run(
            ["typst"] + args, capture_output=True, text=True, encoding="utf-8"
        )
        if result.returncode != 0:
            print(f"Typst error: {result.stderr.strip()}")
            return False
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def _compile_worker(
    typ_file: Path,
    output_path_fn,
    build_args_func,
    post_hook=None,
) -> tuple[Path, bool, str]:
    try:
        output_path = output_path_fn(typ_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        args = build_args_func(typ_file, output_path)
        if run_typst_command(args):
            if post_hook is not None and not post_hook(output_path):
                return (typ_file, False, "X")
            else:
                return (typ_file, True, "O")
        else:
            return (typ_file, False, "X")
    except Exception as e:
        print(f"Worker error for {typ_file}: {e}")
        return (typ_file, False, "X")


def compile_files(
    files: list[Path],
    output_path_fn,
    build_args_func,
    post_hook=None,
) -> BuildStats:
    stats = BuildStats()

    if not files:
        return stats

    max_workers = min(len(files), os.cpu_count() or 1)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                _compile_worker, typ_file, output_path_fn, build_args_func, post_hook
            )
            for typ_file in files
        ]

        for future in futures:
            typ_file, success, status_char = future.result()
            if status_char == "O":
                print(f"[{status_char}] {typ_file}")
                stats.success += 1
            else:
                print(f"[{status_char}] {typ_file}")
                stats.failed += 1

    return stats


def build_html(
    files: list[Path] | None = None,
) -> bool:
    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    typ_files = files if files is not None else find_typ_files()
    typ_files = [
        f
        for f in typ_files
        if "pdf" not in f.stem.lower() and f.stem != cfg.config_file.stem
    ]

    if not typ_files:
        return True

    def get_output_path(typ_file: Path) -> Path:
        relative_path = typ_file.relative_to(cfg.content_dir)
        return cfg.out_dir / relative_path.with_suffix(".html")

    def build_args(typ_file: Path, output_path: Path) -> list[str]:
        return [
            "compile",
            "--root",
            ".",
            "--font-path",
            str(cfg.assets_dir),
            "--input",
            f"base-path={cfg.site_base_path if args.deploy else ''}",
            "--features",
            "html",
            "--format",
            "html",
            str(typ_file),
            str(output_path),
        ]

    def post_hook(output_path: Path) -> bool:
        # Apply enhanced SEO/RSS tags based on HTML head info
        return inject_seo_rss_tags(output_path)

    stats = compile_files(
        typ_files,
        get_output_path,
        build_args,
        post_hook,
    )

    print(f"HTML build: {stats.format_summary()}")
    return not stats.has_failures


def build_pdf(
    files: list[Path] | None = None,
) -> bool:
    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    typ_files = files if files is not None else find_typ_files()
    pdf_files = [f for f in typ_files if "pdf" in f.stem.lower()]

    if not pdf_files:
        return True

    def get_output_path(typ_file: Path) -> Path:
        relative_path = typ_file.relative_to(cfg.content_dir)
        return cfg.out_dir / relative_path.with_suffix(".pdf")

    def build_args(typ_file: Path, output_path: Path) -> list[str]:
        return [
            "compile",
            "--root",
            ".",
            "--font-path",
            str(cfg.assets_dir),
            "--input",
            f"base-path={cfg.site_base_path if args.deploy else ''}",
            str(typ_file),
            str(output_path),
        ]

    stats = compile_files(
        pdf_files,
        get_output_path,
        build_args,
    )

    print(f"PDF build: {stats.format_summary()}")
    return not stats.has_failures


def build() -> bool:
    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    results.append(build_html())
    results.append(build_pdf())
    results.append(copy_assets())
    results.append(copy_content_assets())

    results.append(generate_robots_txt())
    results.append(generate_sitemap())
    results.append(generate_rss())

    if all(results):
        print("All tasks succeeded")
    else:
        print("Some tasks failed")

    return all(results)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest="command", title="Available commands", metavar="<command>"
    )

    subparsers.add_parser("build", help="Full build (HTML + PDF + assets)")
    subparsers.add_parser("html", help="Build only HTML files")
    subparsers.add_parser("pdf", help="Build only PDF files")
    subparsers.add_parser("assets", help="Copy static assets")
    subparsers.add_parser("clean", help="Clean generated files")

    preview_parser = subparsers.add_parser("preview", help="Preview with auto-rebuild")
    preview_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Preview server port (default: 8000)",
    )

    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Build for deployment (GitHub Pages)",
    )

    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    root_dir = Path(__file__).parent.absolute()
    os.chdir(root_dir)

    match args.command:
        case "build":
            success = build()
        case "html":
            success = build_html()
        case "pdf":
            success = build_pdf()
        case "assets":
            success = copy_assets()
        case "preview":
            success = preview(args.port)
        case "clean":
            success = clean()
        case _:
            print(f"Unknown command: {args.command}")
            success = False

    sys.exit(0 if success else 1)

# python  .\scripts\docs.py --help
import json
import logging
import os
import shutil
import subprocess
from functools import lru_cache
from http.server import HTTPServer, SimpleHTTPRequestHandler
from importlib import metadata
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import mkdocs.utils
import typer
import yaml
from ruff.__main__ import find_ruff_bin

logging.basicConfig(level=logging.INFO)

app = typer.Typer()

mkdocs_name = "mkdocs.yml"

missing_translation_snippet = """
{!../../docs/missing-translation.md!}
"""

non_translated_sections = [
    "reference/",
    "release-notes.md",
    "dev-people.md",
    "external-links.md",
    "newsletter.md",
    "management-tasks.md",
    "management.md",
]

docs_path = Path("docs")
zh_docs_path = Path("docs/zh")
zh_config_path: Path = zh_docs_path / mkdocs_name
site_path = Path("site").absolute()
build_site_path = Path("site_build").absolute()  # 这个之后得改成根据一个版本修改的


@lru_cache
def is_mkdocs_insiders() -> bool:
    version = metadata.version("mkdocs-material")
    return "insiders" in version


def get_zh_config() -> Dict[str, Any]:
    return mkdocs.utils.yaml_load(zh_config_path.read_text(encoding="utf-8"))


def get_lang_paths() -> List[Path]:
    return sorted(docs_path.iterdir())


def lang_callback(lang: Optional[str]) -> Union[str, None]:
    if lang is None:
        return None
    lang = lang.lower()
    return lang


def complete_existing_lang(incomplete: str):
    lang_path: Path
    for lang_path in get_lang_paths():
        if lang_path.is_dir() and lang_path.name.startswith(incomplete):
            yield lang_path.name


@app.callback()
def callback() -> None:
    if is_mkdocs_insiders():
        os.environ["INSIDERS_FILE"] = "../zh/mkdocs.insiders.yml"
    # For MacOS with insiders and Cairo
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/homebrew/lib"


@app.command()
def new_lang(lang: str = typer.Argument(..., callback=lang_callback)):
    """
    Generate a new docs translation directory for the language LANG.
    """
    new_path: Path = Path("docs") / lang
    if new_path.exists():
        typer.echo(f"The language was already created: {lang}")
        raise typer.Abort()
    new_path.mkdir()
    new_config_path: Path = Path(new_path) / mkdocs_name
    new_config_path.write_text("INHERIT: ../zh/mkdocs.yml\n", encoding="utf-8")
    new_config_docs_path: Path = new_path / "docs"
    new_config_docs_path.mkdir()
    zh_index_path: Path = zh_docs_path / "docs" / "index.md"
    new_index_path: Path = new_config_docs_path / "index.md"
    zh_index_content = zh_index_path.read_text(encoding="utf-8")
    new_index_content = f"{missing_translation_snippet}\n\n{zh_index_content}"
    new_index_path.write_text(new_index_content, encoding="utf-8")
    typer.secho(f"Successfully initialized: {new_path}", color=typer.colors.GREEN)
    update_languages()


@app.command()
def build_lang(
    lang: str = typer.Argument(
        ..., callback=lang_callback, autocompletion=complete_existing_lang
    ),
) -> None:
    """
    Build the docs for a language.
    : 生成一种语言的文档。build-all的单个任务
    """
    insiders_env_file = os.environ.get("INSIDERS_FILE")
    print(f"Insiders file {insiders_env_file}")
    if is_mkdocs_insiders():
        print("Using insiders")
    lang_path: Path = Path("docs") / lang
    if not lang_path.is_dir():
        typer.echo(f"The language translation doesn't seem to exist yet: {lang}")
        raise typer.Abort()
    typer.echo(f"Building docs for: {lang}")
    build_site_dist_path = build_site_path / lang
    if lang == "zh":
        dist_path = site_path
        # Don't remove zh dist_path as it might already contain other languages.
        # When running build_all(), that function already removes site_path.
        # All this is only relevant locally, on GitHub Actions all this is done through
        # artifacts and multiple workflows, so it doesn't matter if directories are
        # removed or not.
    else:
        dist_path = site_path / lang
        shutil.rmtree(dist_path, ignore_errors=True)
    current_dir = os.getcwd()
    os.chdir(lang_path)
    shutil.rmtree(build_site_dist_path, ignore_errors=True)
    subprocess.run(["mkdocs", "build", "--site-dir", build_site_dist_path], check=True)
    shutil.copytree(build_site_dist_path, dist_path, dirs_exist_ok=True)
    os.chdir(current_dir)
    typer.secho(f"Successfully built docs for: {lang}", color=typer.colors.GREEN)


index_sponsors_template = """
{% if sponsors %}
{% for sponsor in sponsors.gold -%}
<a href="{{ sponsor.url }}" target="_blank" title="{{ sponsor.title }}"><img src="{{ sponsor.img }}"></a>
{% endfor -%}
{%- for sponsor in sponsors.silver -%}
<a href="{{ sponsor.url }}" target="_blank" title="{{ sponsor.title }}"><img src="{{ sponsor.img }}"></a>
{% endfor %}
{% endif %}
"""


def generate_readme_content() -> str:
    zh_index = zh_docs_path / "docs" / "index.md"
    content = zh_index.read_text("utf-8")
    # match_pre = re.search(r"</style>\n\n", content)
    # match_start = re.search(r"<!-- sponsors -->", content)
    # match_end = re.search(r"<!-- /sponsors -->", content)
    # sponsors_data_path = zh_docs_path / "data" / "sponsors.yml"
    # sponsors = mkdocs.utils.yaml_load(sponsors_data_path.read_text(encoding="utf-8"))
    # if not (match_start and match_end):
    #     raise RuntimeError("Couldn't auto-generate sponsors section")
    # if not match_pre:
    #     raise RuntimeError("Couldn't find pre section (<style>) in index.md")
    # frontmatter_end = match_pre.end()
    # pre_end = match_start.end()
    # post_start = match_end.start()
    # template = Template(index_sponsors_template)
    # message = template.render(sponsors=sponsors)
    # pre_content = content[frontmatter_end:pre_end]
    # post_content = content[post_start:]
    # new_content = pre_content + message + post_content
    # new_content = pre_content + post_content
    # Remove content between <!-- only-mkdocs --> and <!-- /only-mkdocs -->
    # new_content = re.sub(
    #     r"<!-- only-mkdocs -->.*?<!-- /only-mkdocs -->",
    #     "",
    #     new_content,
    #     flags=re.DOTALL,
    # )
    # return new_content
    return content


# @app.command()
def generate_readme() -> None:
    """
    Generate README.md content from main index.md
    : 从主index.md生成README.md内容
    """
    typer.echo("Generating README")
    readme_path = Path("README.md")
    new_content = generate_readme_content()
    readme_path.write_text(new_content, encoding="utf-8")


# @app.command()
def verify_readme() -> None:
    """
    Verify README.md content from main index.md
    : 验证主index.md中的README.md内容
    """
    typer.echo("Verifying README")
    readme_path = Path("README.md")
    generated_content = generate_readme_content()
    readme_content = readme_path.read_text("utf-8")
    if generated_content != readme_content:
        typer.secho(
            "README.md outdated from the latest index.md", color=typer.colors.RED
        )
        raise typer.Abort()
    typer.echo("Valid README ✅")


@app.command()
def build_all() -> None:
    """
    Build mkdocs site for zh, and then build each language inside, end result is located
    at directory ./site/ with each language inside.
    : 为zh构建mkdocs站点，然后在内部构建每种语言，最终结果位于
    在目录中。/site/里面的每种语言。
    """
    update_languages()
    shutil.rmtree(site_path, ignore_errors=True)
    langs = [lang.name for lang in get_lang_paths() if lang.is_dir()]
    cpu_count = os.cpu_count() or 1
    # Windows has a limit of 64 handles for WaitForMultipleObjects
    # But my local Windows is usually smaller than this value
    # Reduce pool size further to avoid hitting the handle limit
    max_pool_size = 60 if os.name == 'nt' else cpu_count * 4
    process_pool_size = min(cpu_count * 4, max_pool_size)
    typer.echo(f"Using process pool size: {process_pool_size}")
    with Pool(process_pool_size) as p:
        p.map(build_lang, langs)


@app.command()
def update_languages() -> None:
    """
    Update the mkdocs.yml file Languages section including all the available languages.
    : 更新mkdocs.yml文件语言部分，包括所有可用的语言。 只保留有用到的yaml数据信息
    """
    update_config()


@app.command()
def serve() -> None:
    """
    A quick server to preview a built site with translations.

    For development, prefer the command live (or just mkdocs serve).

    This is here only to preview a site with translations already built.

    Make sure you run the build-all command first.
    : 在build-all-langs后启动预览服务
    """
    typer.echo("Warning: this is a very simple server.")
    typer.echo("For development, use the command live instead.")
    typer.echo("This is here only to preview a site with translations already built.")
    typer.echo("Make sure you run the build-all command first.")
    os.chdir("site")
    server_address = ("", 8008)
    server = HTTPServer(server_address, SimpleHTTPRequestHandler)
    typer.echo("Serving at: http://127.0.0.1:8008")
    server.serve_forever()


@app.command()
def live(
    lang: str = typer.Argument(
        None, callback=lang_callback, autocompletion=complete_existing_lang
    ),
    dirty: bool = False,
) -> None:
    """
    Serve with livereload a docs site for a specific language.

    This only shows the actual translated files, not the placeholders created with
    build-all.

    Takes an optional LANG argument with the name of the language to serve, by default
    zh.
    """
    # Enable line numbers during local development to make it easier to highlight
    if lang is None:
        lang = "zh"
    lang_path: Path = docs_path / lang
    # Enable line numbers during local development to make it easier to highlight
    args = ["mkdocs", "serve", "--dev-addr", "127.0.0.1:8008"]
    if dirty:
        args.append("--dirty")
    subprocess.run(
        args, env={**os.environ, "LINENUMS": "true"}, cwd=lang_path, check=True
    )


def get_updated_config_content() -> Dict[str, Any]:
    config = get_zh_config()
    languages = [{"zh": "/"}]
    new_alternate: List[Dict[str, str]] = []
    # Language names sourced from https://quickref.me/iso-639-1
    # Contributors may wish to update or change these, e.g. to fix capitalization.
    language_names_path = Path(__file__).parent / "../docs/language_names.yml"
    local_language_names: Dict[str, str] = mkdocs.utils.yaml_load(
        language_names_path.read_text(encoding="utf-8")
    )
    for lang_path in get_lang_paths():
        if lang_path.name in {"zh", "em"} or not lang_path.is_dir():
            continue
        code = lang_path.name
        languages.append({code: f"/{code}/"})
    for lang_dict in languages:
        code = list(lang_dict.keys())[0]
        url = lang_dict[code]
        if code not in local_language_names:
            print(
                f"Missing language name for: {code}, "
                "update it in docs/language_names.yml"
            )
            raise typer.Abort()
        use_name = f"{code} - {local_language_names[code]}"
        new_alternate.append({"link": url, "name": use_name})
    # new_alternate.append({"link": "/em/", "name": "😉"})
    config["extra"]["alternate"] = new_alternate
    return config


def update_config() -> None:
    config = get_updated_config_content()
    zh_config_path.write_text(
        yaml.dump(config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )


@app.command()
def verify_config() -> None:
    """
    Verify main mkdocs.yml content to make sure it uses the latest language names.
    : 验证主要的mkdocs.yml内容，以确保它使用最新的语言名称。
    """
    typer.echo("Verifying mkdocs.yml")
    config = get_zh_config()
    updated_config = get_updated_config_content()
    if config != updated_config:
        typer.secho(
            "docs/zh/mkdocs.yml outdated from docs/language_names.yml, "
            "update language_names.yml and run "
            "python ./scripts/docs.py update-languages",
            color=typer.colors.RED,
        )
        raise typer.Abort()
    typer.echo("Valid mkdocs.yml ✅")


# @app.command()
def verify_non_translated() -> None:
    """
    Verify there are no files in the non translatable pages.
    : 验证不（允许）可翻译的页面中没有被翻译. 备注：non_translated_sections中是不需要被翻译的文件因为时常变动
    """
    print("Verifying non translated pages")
    lang_paths = get_lang_paths()
    error_paths = []
    for lang in lang_paths:
        if lang.name == "zh":
            continue
        for non_translatable in non_translated_sections:
            non_translatable_path = lang / "docs" / non_translatable
            if non_translatable_path.exists():
                error_paths.append(non_translatable_path)
    if error_paths:
        print("Non-translated pages found, remove them:")
        for error_path in error_paths:
            print(error_path)
        raise typer.Abort()
    print("No non-translated pages found ✅")


# @app.command()
def verify_docs():
    verify_readme()
    verify_config()
    verify_non_translated()


@app.command()
def langs_json():
    """
    Output the existing translation language
    : 输出已有的翻译语种
    """
    langs = []
    for lang_path in get_lang_paths():
        if lang_path.is_dir():
            langs.append(lang_path.name)
    print(json.dumps(langs))


@app.command()
def generate_docs_src_versions_for_file(file_path: Path) -> None:
    target_versions = ["py39", "py310"]
    base_content = file_path.read_text(encoding="utf-8")
    previous_content = {base_content}
    for target_version in target_versions:
        version_result = subprocess.run(
            [
                find_ruff_bin(),
                "check",
                "--target-version",
                target_version,
                "--fix",
                "--unsafe-fixes",
                "-",
            ],
            input=base_content.encode("utf-8"),
            capture_output=True,
        )
        content_target = version_result.stdout.decode("utf-8")
        format_result = subprocess.run(
            [find_ruff_bin(), "format", "-"],
            input=content_target.encode("utf-8"),
            capture_output=True,
        )
        content_format = format_result.stdout.decode("utf-8")
        if content_format in previous_content:
            continue
        previous_content.add(content_format)
        version_file = file_path.with_name(
            file_path.name.replace(".py", f"_{target_version}.py")
        )
        logging.info(f"Writing to {version_file}")
        version_file.write_text(content_format, encoding="utf-8")


if __name__ == "__main__":
    app()

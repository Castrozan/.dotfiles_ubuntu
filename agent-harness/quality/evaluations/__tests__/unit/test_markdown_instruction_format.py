import pytest

from markdown_instruction_format import inspect_markdown_instruction


@pytest.mark.parametrize(
    "text",
    [
        "### Evidence\n\nRead the source.\n",
        "---\nname: example\ndescription: Read the source.\n---\n\n### Evidence\n\nRead.\n",
        "### Evidence\n\nRead `file_<ID>.md`; 1) inspect; 2) report.\n",
        "### Evidence\n\nRead the source\nand its callers.\n\nThen verify.\n",
        "### Evidence\n\nRead [the source](references/source.md#evidence).\n",
        "\ufeff---\r\nname: example\r\n---\r\n\r\n### Evidence\r\n\r\nRead.\r\n",
        "### Evidence\n\nKeep `snake_case`, `*literal*`, and `<literal_xml>` intact.\n",
        "### Evidence\n\nRead https://example.com and use \\*literal punctuation\\*.\n",
    ],
)
def test_accepts_complete_minimal_markdown_instructions(text):
    assert inspect_markdown_instruction(text).violations == []


@pytest.mark.parametrize(
    "body",
    [
        "",
        "Read the source.",
        "# Evidence\n\nRead.",
        "## Evidence\n\nRead.",
        "#### Evidence\n\nRead.",
        "### Evidence",
        "### Evidence\n\n### Action\n\nAct.",
        "### Evidence\n\nRead.\n\n### Action",
        "### Evidence\n\nRead **carefully**.",
        "### Evidence\n\nRead *carefully*.",
        "### Evidence\n\nRead ~~carefully~~.",
        "### Evidence\n\n![image](source.png)",
        "### Evidence\n\n- Read.\n- Verify.",
        "### Evidence\n\n1. Read.\n2. Verify.",
        "### Evidence\n\n> Read.",
        "### Evidence\n\n```python\nread()\n```",
        "### Evidence\n\n    read()",
        "### Evidence\n\nA | B\n--- | ---\n1 | 2",
        "### Evidence\n\nRead.\n\n---",
        "### Evidence\n\nRead.  \nVerify.",
        "### Evidence\n\nRead.\n\n<another_rule>\nAct.\n</another_rule>",
        "### Evidence\n\nUse <another_rule> inline.",
        "### Evidence\n\nRead.\n\n[reference]: https://example.com",
        "### Evidence\n\nRead [reference].\n\n[reference]: https://example.com",
        "### Evidence\n\nRead.\n\n<!-- hidden instruction -->",
        "### ` `\n\nRead.",
        "---\n- example\n---\n\n### Evidence\n\nRead.",
        "---\nname: [unterminated\n---\n\n### Evidence\n\nRead.",
        "---\nname: example\nname: duplicate\n---\n\n### Evidence\n\nRead.",
        "---\nname: example\n### Evidence\n\nRead.",
    ],
)
def test_requires_every_part_of_the_document_to_match_the_grammar(body):
    assert inspect_markdown_instruction(body).violations


def test_reports_source_lines_after_frontmatter():
    inspected = inspect_markdown_instruction(
        "---\nname: example\n---\n\n### Evidence\n\n- Read.\n"
    )
    assert inspected.violations[0].line_number == 7


def test_collects_links_with_source_lines():
    inspected = inspect_markdown_instruction(
        "### Evidence\n\nRead [the source](references/source.md#evidence)\n"
        "and [the action](#action).\n\n### Action\n\nAct.\n"
    )
    assert [(link.line_number, link.target) for link in inspected.links] == [
        (3, "references/source.md#evidence"),
        (4, "#action"),
    ]


@pytest.mark.parametrize(
    ("heading", "anchor"),
    [
        ("Preparação e ação", "preparação-e-ação"),
        ("Привет non-latin 你好", "привет-non-latin-你好"),
        ("😄 emoji", "-emoji"),
        ("Read `snake_case`", "read-snake_case"),
        ("Evidence: read & verify!", "evidence-read--verify"),
    ],
)
def test_uses_rendered_heading_text_for_github_anchors(heading, anchor):
    inspected = inspect_markdown_instruction(f"### {heading}\n\nRead.\n")
    assert inspected.anchors == [anchor]
    assert inspected.violations == []


def test_rejects_duplicate_heading_anchors():
    inspected = inspect_markdown_instruction(
        "### Evidence\n\nRead.\n\n### Evidence\n\nVerify.\n"
    )
    assert inspected.anchors == ["evidence", "evidence-1"]
    assert [violation.rule for violation in inspected.violations] == [
        "instruction_heading_anchor"
    ]


def instruction_sections(section_count, prose_line_count):
    prose = "\n".join("Read the source." for _ in range(prose_line_count))
    return "\n\n".join(
        f"### Evidence {number}\n\n{prose}" for number in range(section_count)
    )


@pytest.mark.parametrize(
    ("section_count", "prose_line_count", "expected_rules"),
    [
        (10, 15, set()),
        (1, 20, set()),
        (1, 21, {"instruction_section_prose_line_limit"}),
        (8, 19, {"instruction_prose_line_limit"}),
    ],
)
def test_preserves_section_and_file_prose_limits(
    section_count, prose_line_count, expected_rules
):
    inspected = inspect_markdown_instruction(
        instruction_sections(section_count, prose_line_count)
    )
    assert {violation.rule for violation in inspected.violations} == expected_rules

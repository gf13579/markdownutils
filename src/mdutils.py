# from markdownify import markdownify as md
import re
from markdownify import MarkdownConverter


# subclassing MarkdownConverter to implement oneline (single tickets) translation of <pre> content - where the pre content has no linebreaks
class OnelinePreConverter(MarkdownConverter):
    def convert_pre(self, el, text, convert_as_inline):
        if not text:
            return ""
        code_language = self.options["code_language"]

        if self.options["code_language_callback"]:
            code_language = self.options["code_language_callback"](el) or code_language

        if "\n" in text:
            return "\n```%s\n%s\n```\n" % (code_language, text)
        else:
            return f"`{text}`"


# Create shorthand method for conversion
def md(html, **options):
    return OnelinePreConverter(**options).convert(html)


def convert_html_to_md(
    html_text: str, defang_urls=True, defang_mailto=True, strip_comments=True
):
    if defang_urls:
        # insert X into the middle of uri handlers of 2+ chars - and bracket the first dot of the fqdn
        html_text = re.sub(
            r"(\w)\w(\w*):\/\/([^\.]+)\.",
            r"\1X\2://\3[.]",
            html_text,
            flags=re.IGNORECASE,
        )
        # replace single-char URI handlers with X - and bracket the first dot of the fqdn
        html_text = re.sub(
            r"(^|\W)\w:\/\/([^\.]+)\.", r"\1X://\2[.]", html_text, flags=re.IGNORECASE
        )
        # deal with www explicitly
        html_text = re.sub(r"www\.", r"wXw[.]", html_text, flags=re.IGNORECASE)

    if strip_comments:
        html_text = re.sub(
            pattern=r"<!--.*?-->", repl=r"", string=html_text, flags=re.DOTALL
        )

    markdown_text = md(html_text)

    if defang_mailto:
        markdown_text = re.sub(
            pattern=r"mailto:", repl=r"mailXXto:", string=markdown_text
        )

    return markdown_text


def translate_img_names_to_ids(markdown_text, name_to_id_dict):
    # do replacements like ](image001.png) -> ](/view?id=3)
    for image_name, image_id in name_to_id_dict.items():
        str_to_replace = r"\]\((?:cid:)?" + re.escape(image_name) + r"(?:@[^\)]+)?\)"
        replacement = "](/view?id=" + str(image_id) + ")"
        markdown_text = re.sub(str_to_replace, replacement, markdown_text)
    return markdown_text

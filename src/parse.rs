use std::{borrow::Cow, sync::LazyLock};

use pcre2::bytes::{Match, Regex};
use pyo3::prelude::*;

#[derive(Debug, PartialEq, Eq)]
pub struct Token<'a> {
    pub kind: Cow<'a, str>,
    pub value: Cow<'a, [u8]>,
    pub byte_range: (usize, usize),
}

/// A code block extracted from a Markdown source.
#[pyclass(eq, get_all, module = "zig_codeblocks._core")]
#[derive(PartialEq, Eq)]
pub struct CodeBlock {
    pub lang: Option<String>,
    pub body: String,
}

#[pymethods]
impl CodeBlock {
    #[new]
    pub fn new(lang: Option<String>, body: &str) -> Self {
        Self {
            lang,
            body: body.to_owned(),
        }
    }

    fn __repr__(&self) -> String {
        let lang_repr = if let Some(lang) = &self.lang {
            format!("{lang:?}")
        } else {
            String::from("None")
        };
        format!("CodeBlock(lang={lang_repr}, body={:?})", self.body)
    }

    fn __str__(&self) -> String {
        self.to_string()
    }
}

impl std::fmt::Display for CodeBlock {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if let Some(lang) = &self.lang {
            write!(f, "```{lang}\n{}```", self.body)
        } else {
            write!(f, "```{}```", self.body)
        }
    }
}

static CODE_BLOCK_PATTERN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?s)```(?:([A-Za-z0-9\-_\+\.#]+)(?:\r?\n)+([^\r\n].*?)|(.*?))```")
        .expect("guaranteed to be valid")
});
static INLINE_CODE_PATTERN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?<!`)(``?)[^`].*?[^`]\1(?!`)").expect("guaranteed to be valid"));

fn get_parser() -> tree_sitter::Parser {
    let mut parser = tree_sitter::Parser::new();
    let language = tree_sitter_zig::LANGUAGE;
    parser
        .set_language(&language.into())
        .expect("tree-sitter-zig should work correctly");
    parser
}

pub fn tokenize_zig(src: &[u8]) -> Vec<Token> {
    let mut parser = get_parser();
    let tree = parser
        .parse(src, None)
        .expect("should be Some, the parser was assigned a language");
    traverse(tree.root_node(), src)
}

fn traverse<'a>(root: tree_sitter::Node, src: &'a [u8]) -> Vec<Token<'a>> {
    let mut tokens = Vec::new();
    let mut stack = vec![root];

    while let Some(node) = stack.pop() {
        if node.child_count() > 0 {
            stack.extend(
                (0..node.child_count())
                    .rev()
                    .map(|i| node.child(i).expect("should be in-bounds")),
            );
            continue;
        }
        tokens.push(Token {
            kind: Cow::Borrowed(node.kind()),
            value: Cow::Borrowed(&src[node.start_byte()..node.end_byte()]),
            byte_range: (node.start_byte(), node.end_byte()),
        });
    }
    tokens
}

fn match_to_utf8(r#match: Match<'_>) -> Cow<'_, str> {
    String::from_utf8_lossy(r#match.as_bytes())
}

pub fn extract_codeblocks(source: &[u8]) -> Vec<CodeBlock> {
    let slices: Vec<_> = INLINE_CODE_PATTERN
        .find_iter(source)
        .map(|m| {
            let m = m.expect("there should be a match");
            (m.start(), m.end())
        })
        .collect();
    let source: Cow<'_, [u8]> = if slices.is_empty() {
        Cow::Borrowed(source)
    } else {
        let mut source = source.to_vec();
        for (a, b) in slices.iter().rev() {
            source.drain(a..b);
        }
        Cow::Owned(source)
    };
    CODE_BLOCK_PATTERN
        .captures_iter(&source)
        .map(|m| {
            let m = m.expect("capture should be ok");
            let (lang, body, no_lang_body) = (m.get(1), m.get(2), m.get(3));
            if lang.is_some() {
                CodeBlock::new(
                    lang.map(|m| match_to_utf8(m).to_string()),
                    &match_to_utf8(body.expect("should be present when lang is present")),
                )
            } else {
                CodeBlock::new(
                    None,
                    &match_to_utf8(no_lang_body.expect("should be present when lang is absent")),
                )
            }
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use std::fs::read_to_string;

    use super::{tokenize_zig, Cow, Token};

    #[derive(serde::Serialize, serde::Deserialize)]
    struct OutputToken {
        kind: String,
        value: Option<String>,
        range: (usize, usize),
    }

    macro_rules! make_test {
        ($name:ident) => {
            #[test]
            fn $name() {
                let src_path = concat!("tests/sources/zig_inputs/", stringify!($name), ".zig");
                let out_path =
                    concat!("tests/sources/parsing_results/", stringify!($name), ".json");
                let source = read_to_string(src_path)
                    .expect("the file should be valid")
                    .replace("\r\n", "\n")
                    .into_bytes();
                let out_json = read_to_string(out_path).expect("the file should be valid");
                assert_eq!(tokenize_zig(&source), read_expected_tokens(&out_json));
            }
        };
    }

    fn read_expected_tokens(content: &str) -> Vec<Token> {
        let t: Vec<OutputToken> =
            serde_json::from_str(content).expect("the output json should be valid");
        t.into_iter()
            .map(|ot| Token {
                value: Cow::Owned(ot.value.unwrap_or(ot.kind.clone()).as_bytes().to_vec()),
                kind: Cow::Owned(ot.kind),
                byte_range: ot.range,
            })
            .collect::<Vec<_>>()
    }

    make_test!(assign_undefined);
    make_test!(comments);
    make_test!(emoji);
    make_test!(global_assembly);
    make_test!(hello_again);
    make_test!(identifiers);
}

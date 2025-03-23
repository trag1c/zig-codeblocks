use std::{borrow::Cow, collections::HashMap};

use pyo3::{exceptions::PyValueError, prelude::*};

use crate::{
    parse::{extract_codeblocks, tokenize_zig, Token},
    style::{Style, Theme, TokenType},
};

pub const RESET: &str = "\x1b[0m";
const CODEBLOCK_START: &[u8] = b"```zig\n";
const KEYWORDS: [&str; 49] = [
    "addrspace",
    "align",
    "allowzero",
    "and",
    "anyframe",
    "anytype",
    "asm",
    "async",
    "await",
    "break",
    "callconv",
    "catch",
    "comptime",
    "const",
    "continue",
    "defer",
    "else",
    "enum",
    "errdefer",
    "error",
    "export",
    "extern",
    "fn",
    "for",
    "if",
    "inline",
    "linksection",
    "noalias",
    "noinline",
    "nosuspend",
    "opaque",
    "or",
    "orelse",
    "packed",
    "pub",
    "resume",
    "return",
    "struct",
    "suspend",
    "switch",
    "test",
    "threadlocal",
    "try",
    "union",
    "unreachable",
    "usingnamespace",
    "var",
    "volatile",
    "while",
];
const IDENTIFIERS: [&str; 2] = ["identifier", "c"];
const NUMERIC_LITERALS: [&str; 2] = ["integer", "float"];
const PRIMITIVE_VALUES: [&str; 4] = ["true", "false", "null", "undefined"];
const STRINGLIKE: [&str; 5] = [
    "string_content",
    "multiline_string",
    "\"",
    "'",
    "character_content",
];
const TYPES: [&str; 26] = [
    "anyerror",
    "anyopaque",
    "bool",
    "builtin_type",
    "c_char",
    "c_int",
    "c_long",
    "c_longdouble",
    "c_longlong",
    "c_short",
    "c_uint",
    "c_ulong",
    "c_ulonglong",
    "c_ushort",
    "comptime_float",
    "comptime_int",
    "f128",
    "f16",
    "f32",
    "f64",
    "f80",
    "isize",
    "noreturn",
    "type",
    "usize",
    "void",
];

#[derive(Clone, PartialEq, Eq)]
enum Frag<'a> {
    Text(Cow<'a, str>),
    Sgr(Style),
}

impl std::fmt::Display for Frag<'_> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let str = match self {
            Self::Text(t) => t.to_string(),
            Self::Sgr(s) => s.to_string(),
        };
        write!(f, "{str}")
    }
}

fn last_applied_style<'a>(body: &[Frag<'a>]) -> Option<Frag<'a>> {
    body.iter()
        .rev()
        .find(|item| match item {
            Frag::Text(s) => s == RESET,
            Frag::Sgr(_) => true,
        })
        .cloned()
}

fn get_style<'a>(kind: &str, theme: &'a Theme) -> Option<&'a Style> {
    let variants: [(&[&str], TokenType); 6] = [
        (&IDENTIFIERS, TokenType::Identifier),
        (&KEYWORDS, TokenType::Keyword),
        (&NUMERIC_LITERALS, TokenType::Numeric),
        (&PRIMITIVE_VALUES, TokenType::PrimitiveValue),
        (&STRINGLIKE, TokenType::String),
        (&TYPES, TokenType::Type),
    ];
    for (options, token_type) in variants {
        if options.contains(&kind) {
            return theme.get(&token_type);
        }
    }
    match kind {
        "comment" => theme.get(&TokenType::Comment),
        "builtin_identifier" => theme.get(&TokenType::BuiltinIdentifier),
        _ => None,
    }
}

fn skip_to_token(source: &[u8], pointer: &mut usize, body: &mut Vec<Frag>, current_token: &Token) {
    let filler = String::from_utf8_lossy(&source[*pointer..current_token.byte_range.0]).to_string();
    let last_style = last_applied_style(body);

    match (filler.trim().is_empty(), last_style) {
        (
            true,
            Some(Frag::Sgr(
                Style {
                    underline: true, ..
                }
                | Style { bold: true, .. },
            )),
        )
        | (false, Some(Frag::Sgr(Style { .. }))) => body.push(Frag::Text(RESET.into())),
        _ => (),
    };
    body.push(Frag::Text(filler.into()));
    *pointer = current_token.byte_range.0;
}

fn check_end_index(body: &[Frag], idx: usize, target: &Frag) -> bool {
    body.len()
        .checked_sub(idx)
        .is_some_and(|idx| body[idx] == *target)
}

fn adjust_string_idents(body: &mut Vec<Frag>, token: &Token, theme: &Theme) {
    // Special case for `whatever.@"something here"`,
    // which is an identifier, so should have no string highlighting
    let identifier_style = theme.get(&TokenType::Identifier);
    let string_style = theme.get(&TokenType::String);
    if !((identifier_style.is_some() || string_style.is_some()) && token.kind == "\"") {
        return;
    }
    let at = Frag::Text("@".into());
    if let Some(style) = string_style {
        if last_applied_style(body) == Some(Frag::Sgr(*style)) && check_end_index(body, 4, &at) {
            let idx = body.len() - 3;
            if let Some(style) = identifier_style {
                body[idx] = Frag::Sgr(*style);
            } else {
                body.remove(idx);
            }
        }
    } else if check_end_index(body, 3, &at) {
        body.insert(
            body.len() - 2,
            Frag::Sgr(*identifier_style.expect("guaranteed by prior logic")),
        );
    }
}

fn process_zig_tokens(source: &[u8], tokens: Vec<Token>, theme: &Theme) -> String {
    let mut body: Vec<Frag> = Vec::with_capacity(tokens.len() * 2);
    let mut pointer = 0;
    let mut tokens = tokens.into_iter().peekable();
    let Some(mut token) = tokens.next() else {
        return String::from_utf8_lossy(source).into();
    };

    while pointer < source.len() {
        if token.byte_range.0 > pointer {
            skip_to_token(source, &mut pointer, &mut body, &token);
            continue;
        }

        let style =
            if token.kind == "identifier" && tokens.peek().map(|v| v.kind == "(") == Some(true) {
                theme.get(&TokenType::Call)
            } else {
                get_style(&token.kind, theme)
            };
        match style {
            None => {
                if matches!(last_applied_style(&body), Some(Frag::Sgr(_))) {
                    body.push(Frag::Text(RESET.into()));
                }
            }
            Some(style) => {
                if last_applied_style(&body) != Some(Frag::Sgr(*style)) {
                    body.push(Frag::Sgr(*style));
                }
            }
        }

        adjust_string_idents(&mut body, &token, theme);

        body.push(Frag::Text(Cow::Owned(
            String::from_utf8_lossy(&token.value).into_owned(),
        )));
        pointer = token.byte_range.1;
        if let Some(next_token) = tokens.next() {
            token = next_token;
        } else {
            break;
        }
    }
    body.into_iter().map(|x| x.to_string()).collect::<String>()
}

pub fn build_theme(theme: HashMap<String, Style>) -> PyResult<Theme> {
    theme
        .into_iter()
        .map(|(k, v)| (TokenType::try_from(k), v))
        .map(|(res, u)| res.map(|t| (t, u)))
        .collect::<Result<HashMap<_, _>, _>>()
        .map_err(|key| PyValueError::new_err(format!("Invalid theme key: {key:?}")))
}

pub fn highlight_zig_code(source: &[u8], theme: &Theme) -> String {
    process_zig_tokens(source, tokenize_zig(source), theme)
}

pub fn process_markdown(source: &[u8], theme: &Theme, only_code: bool) -> String {
    let zig_codeblocks = extract_codeblocks(source)
        .into_iter()
        .filter_map(|cb| (cb.lang == Some("zig".into())).then_some(cb.body.as_bytes().to_vec()));
    if only_code {
        return zig_codeblocks
            .map(|cb| format!("```ansi\n{}\n```", highlight_zig_code(&cb, theme)))
            .collect::<Vec<_>>()
            .join("\n");
    }

    // Deduplicating the codeblocks
    let mut seen = std::collections::HashSet::new();
    let zig_codeblocks = zig_codeblocks.filter(|item| seen.insert(item.clone()));

    let mut new_source = source.to_vec();
    for cb in zig_codeblocks {
        let needle = CODEBLOCK_START
            .iter()
            .copied()
            .chain(cb.iter().copied())
            .chain(b"```".iter().copied())
            .collect::<Vec<_>>();
        let start_positions = new_source
            .windows(needle.len())
            .enumerate()
            .filter_map(|(i, w)| if w == needle { Some(i) } else { None })
            .rev()
            .collect::<Vec<_>>();

        let mut highlighted = highlight_zig_code(&cb, theme);
        highlighted.insert_str(0, "```ansi\n");
        highlighted.push_str("\n```");
        let highlighted_bytes = highlighted.as_bytes();

        let end_pos_offset = needle.len();
        for start_pos in start_positions {
            new_source.splice(
                start_pos..start_pos + end_pos_offset,
                highlighted_bytes.to_vec(),
            );
        }
    }
    String::from_utf8_lossy(&new_source).to_string()
}

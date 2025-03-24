use std::collections::HashMap;

use pyo3::prelude::*;

mod format;
mod parse;
mod style;

#[derive(FromPyObject)]
pub enum StrOrBytes {
    #[pyo3(transparent)]
    Str(String),
    #[pyo3(transparent)]
    Bytes(Vec<u8>),
}

impl StrOrBytes {
    fn resolve(&self) -> &[u8] {
        match self {
            Self::Str(s) => s.as_bytes(),
            Self::Bytes(b) => b,
        }
    }
}

/// Return an ANSI syntax-highlighted version of the given Zig source code. Assumes UTF-8.
#[pyfunction]
#[pyo3(signature = (source, theme=style::DEFAULT_THEME_PREPROCESSED.clone()))]
pub fn highlight_zig_code(
    source: StrOrBytes,
    theme: HashMap<String, style::Style>,
) -> PyResult<String> {
    Ok(format::highlight_zig_code(
        source.resolve(),
        &format::build_theme(theme)?,
    ))
}

/// Return a Markdown source with Zig code blocks syntax-highlighted.
/// If `only_code` is True, only processed Zig code blocks will be returned. Assumes UTF-8.
#[pyfunction]
#[pyo3(signature = (source, theme=style::DEFAULT_THEME_PREPROCESSED.clone(), *, only_code=false))]
pub fn process_markdown(
    source: StrOrBytes,
    theme: HashMap<String, style::Style>,
    only_code: bool,
) -> PyResult<String> {
    Ok(format::process_markdown(
        source.resolve(),
        &format::build_theme(theme)?,
        only_code,
    ))
}

/// Return CodeBlocks from a Markdown source. Assumes UTF-8.
#[pyfunction]
pub fn extract_codeblocks(source: StrOrBytes) -> Vec<parse::CodeBlock> {
    parse::extract_codeblocks(source.resolve())
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_codeblocks, m)?)?;
    m.add_function(wrap_pyfunction!(highlight_zig_code, m)?)?;
    m.add_function(wrap_pyfunction!(process_markdown, m)?)?;
    m.add_class::<parse::CodeBlock>()?;
    m.add_class::<style::Color>()?;
    m.add_class::<style::Style>()?;
    Ok(())
}

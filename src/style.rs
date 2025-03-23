use std::{collections::HashMap, sync::LazyLock};

use pyo3::{exceptions::PyValueError, prelude::*};

#[pyclass(eq, eq_int, module = "zig_codeblocks._core")]
#[derive(PartialEq, Eq, Clone, Copy, Debug)]
pub enum Color {
    Gray,
    Red,
    Green,
    Orange,
    Blue,
    Magenta,
    Cyan,
    White,
}

#[pymethods]
impl Color {
    #[staticmethod]
    fn from_string(value: &str) -> PyResult<Self> {
        match &value.to_lowercase()[..] {
            "gray" => Ok(Self::Gray),
            "red" => Ok(Self::Red),
            "green" => Ok(Self::Green),
            "orange" => Ok(Self::Orange),
            "blue" => Ok(Self::Blue),
            "magenta" => Ok(Self::Magenta),
            "cyan" => Ok(Self::Cyan),
            "white" => Ok(Self::White),
            _ => Err(PyValueError::new_err(format!("Invalid color: {value:?}"))),
        }
    }
}

impl Color {
    const fn code(self) -> &'static str {
        match self {
            Self::Gray => "30",
            Self::Red => "31",
            Self::Green => "32",
            Self::Orange => "33",
            Self::Blue => "34",
            Self::Magenta => "35",
            Self::Cyan => "36",
            Self::White => "37",
        }
    }
}

const fn python_bool_repr(value: bool) -> &'static str {
    if value { "True" } else { "False" }
}

#[pyclass(module = "zig_codeblocks._core")]
#[derive(PartialEq, Eq, Clone, Copy, Debug)]
pub struct Style {
    #[pyo3(get, set)]
    color: Color,
    #[pyo3(get, set)]
    pub bold: bool,
    #[pyo3(get, set)]
    pub underline: bool,
}

#[pymethods]
impl Style {
    #[new]
    #[pyo3(signature = (color, *, bold=false, underline=false))]
    fn new(color: Color, bold: bool, underline: bool) -> Self {
        Self {
            color,
            bold,
            underline,
        }
    }

    #[staticmethod]
    fn from_string(value: &str) -> PyResult<Self> {
        let mut color: Option<Color> = None;
        let mut bold = false;
        let mut underline = false;

        for part in value.to_lowercase().split('+') {
            match part {
                "bold" => bold = true,
                "underline" => underline = true,
                c => {
                    let Ok(valid_color) = Color::from_string(c) else {
                        return Err(PyValueError::new_err(format!("Invalid color {c:?}")));
                    };
                    if let Some(applied) = color {
                        return Err(PyValueError::new_err(format!(
                            "Multiple colors found: {applied:?} and {valid_color:?}"
                        )));
                    }
                    color = Some(valid_color);
                }
            }
        }
        if let Some(color) = color {
            Ok(Self {
                color,
                bold,
                underline,
            })
        } else {
            Err(PyValueError::new_err("Missing color in input string"))
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "Style({}, bold={}, underline={})",
            self.color.__pyo3__repr__(),
            python_bool_repr(self.bold),
            python_bool_repr(self.underline)
        )
    }

    fn __str__(&self) -> String {
        self.to_string()
    }
}

impl std::fmt::Display for Style {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let values = [self.color.code(), "1", "4"]
            .iter()
            .zip([true, self.bold, self.underline])
            .filter_map(|(code, enabled)| enabled.then_some(*code))
            .collect::<Vec<_>>();
        write!(f, "\x1b[{}m", values.join(";"))
    }
}

impl From<Color> for Style {
    fn from(color: Color) -> Self {
        Self {
            color,
            bold: false,
            underline: false,
        }
    }
}

#[derive(Hash, Eq, PartialEq, Clone, Copy)]
pub enum TokenType {
    BuiltinIdentifier,
    Call,
    Comment,
    Identifier,
    Keyword,
    Numeric,
    String,
    PrimitiveValue,
    Type,
}

impl TryFrom<String> for TokenType {
    type Error = String;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        match value.as_str() {
            "BuiltinIdentifier" => Ok(Self::BuiltinIdentifier),
            "Call" => Ok(Self::Call),
            "Comment" => Ok(Self::Comment),
            "Identifier" => Ok(Self::Identifier),
            "Keyword" => Ok(Self::Keyword),
            "Numeric" => Ok(Self::Numeric),
            "String" => Ok(Self::String),
            "PrimitiveValue" => Ok(Self::PrimitiveValue),
            "Type" => Ok(Self::Type),
            _ => Err(value),
        }
    }
}

pub type Theme = HashMap<TokenType, Style>;

pub static DEFAULT_THEME_PREPROCESSED: LazyLock<HashMap<String, Style>> = LazyLock::new(|| {
    HashMap::from([
        (
            "BuiltinIdentifier".into(),
            Style {
                color: Color::Blue,
                bold: true,
                underline: false,
            },
        ),
        ("Call".into(), Style::from(Color::Blue)),
        ("Comment".into(), Style::from(Color::Gray)),
        ("Keyword".into(), Style::from(Color::Magenta)),
        ("Numeric".into(), Style::from(Color::Cyan)),
        ("PrimitiveValue".into(), Style::from(Color::Cyan)),
        ("String".into(), Style::from(Color::Green)),
        ("Type".into(), Style::from(Color::Orange)),
    ])
});

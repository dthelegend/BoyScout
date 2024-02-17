use std::borrow::Cow;
use std::fmt::format;
use std::io::{Read, Write};
use pyo3::exceptions::PyIOError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use crate::sfss::SFSSManager;

mod sfss;
#[cfg(test)]
mod test;

/// Formats the sum of two numbers as string.
#[pyclass]
struct PySFSSConnection(SFSSManager);

#[pymethods]
impl PySFSSConnection {
    #[new]
    fn py_new() -> PyResult<Self> {
        Ok(PySFSSConnection(SFSSManager::new().map_err(|e| PyErr::new::<PyIOError, _>(format!("Failed to initialise SFSS Connection. Reason {}", e)))?))
    }

    fn read_n(&mut self, n: usize, py: Python) -> PyResult<PyObject> {
        let mut buf = vec![0u8; n];

        let amount = self.0.read(&mut buf)
            .map_err(|x| PyErr::new::<PyIOError, _>(format!("Could not read tunnel. Reason: {}", x.kind())))?;

        Ok(PyBytes::new(py, &buf[0..amount]).into())
    }

    fn write(&mut self, b: Vec<u8>, py: Python) -> PyResult<usize> {

        let amount = self.0.write(&b)
            .map_err(|x| PyErr::new::<PyIOError, _>(format!("Could not write to tunnel. Reason: {}", x.kind())))?;

        Ok(amount)
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn boyscout(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySFSSConnection>()?;
    Ok(())
}

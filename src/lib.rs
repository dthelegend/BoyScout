use std::io::{Read, Write};
use pyo3::exceptions::{PyIOError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use regex::Regex;
use crate::ChecksumType::CcittCrc16;
use crate::FrameProtocol::IPv4;
use crate::sfss::SFSSManager;

mod sfss;

/// Formats the sum of two numbers as string.
#[pyclass]
struct PySFSSConnection(SFSSManager);

#[derive(Copy, Clone)]
#[repr(u8)]
enum FrameProtocol {
    None = 0,
    IPv4 = 1,
    IPv6 = 2,
    IPv4gzip = 3,
    IPv6gzip = 4
}

#[derive(Copy, Clone)]
#[repr(u8)]
enum ChecksumType {
    None = 0,
    CcittCrc16 = 1
}

#[derive(Clone)]
struct Frame {
    protocol: FrameProtocol,
    checksum_type: ChecksumType,
    frame_number: u8,
    data: Vec<u8>,
    checksum: u16
}

fn sfs_from_u8(x: u8) -> (char, char) {
    (sfs_from_u4(x >> 4), sfs_from_u4(x))
}

fn sfs_from_u4(x: u8) -> char {
    let last_four = x & 0x0F;
    match last_four {
        0x00 => 'A',
        0x01 => 'B',
        0x02 => 'C',
        0x03 => 'D',
        0x04 => 'E',
        0x05 => 'F',
        0x06 => 'G',
        0x07 => 'H',
        0x08 => 'I',
        0x09 => 'J',
        0x0A => 'K',
        0x0B => 'L',
        0x0C => 'M',
        0x0D => 'N',
        0x0E => 'O',
        0x0F => 'P',
        _ => unreachable!()
    }
}

fn u4_to_sfs(x: char) -> u8 {
    match x {
        'A' => 0x00,
        'B' => 0x01,
        'C' => 0x02,
        'D' => 0x03,
        'E' => 0x04,
        'F' => 0x05,
        'G' => 0x06,
        'H' => 0x07,
        'I' => 0x08,
        'J' => 0x09,
        'K' => 0x0A,
        'L' => 0x0B,
        'M' => 0x0C,
        'N' => 0x0D,
        'O' => 0x0E,
        'P' => 0x0F,
        _ => unreachable!()
    }
}

impl Frame {
    fn to_sfs(&self) -> Vec<char> {
        let mut x = Vec::with_capacity(10 + self.data.len());

        x.push('Q');
        x.push(sfs_from_u4(self.protocol as u8));
        x.push(sfs_from_u4(self.checksum_type as u8));
        {
            let (a, b) = sfs_from_u8(self.frame_number);
            x.push(a);
            x.push(b);
        }
        for data in &self.data {
            let (a, b) = sfs_from_u8(*data);
            x.push(a);
            x.push(b);
        }
        {
            let (a, b) = sfs_from_u8((self.checksum >> 8) as u8);
            let (c, d) = sfs_from_u8(self.checksum as u8);
            x.push(a);
            x.push(b);
            x.push(c);
            x.push(d);
        }
        x.push('R');

        x
    }

    fn recalculate_checksum(&mut self) -> () {
        unimplemented!()
    }
}

#[pyfunction]
fn py_bytes_to_frames(bytes: Vec<u8>) -> Vec<Vec<char>> {
    let data_sections = bytes.chunks(255);
    data_sections.into_iter().enumerate().map(|(i, x)| {
        Frame {
            protocol: IPv4,
            checksum_type: CcittCrc16,
            frame_number: i as u8,
            data: Vec::from(x),
            checksum: 0xFFFF
        }.to_sfs()
    }).collect()
}

#[pyfunction]
fn py_frame_to_bytes(frame_array: String, py: Python) -> PyResult<(PyObject, u8)> {
    let re = Regex::new(r"Q(?P<proto>[A-P])(?P<cksum_typ>[A-P])(?P<frame_no>[A-P][A-P])(?P<data>[A-PST]*)(?P<cksum>[A-P][A-P][A-P][A-P])R").unwrap();

    let caps = re.captures(&frame_array).ok_or_else(|| PyErr::new::<PyValueError,_>("Failed to parse frame"))?;

    let data = &caps["data"];
    let frame_number_vec : Vec<char> = caps["frame_no"].chars().collect();
    let frame_number : u8 = match frame_number_vec[..] {
        [a,b] => (u4_to_sfs(a) << 4) | u4_to_sfs(b),
        _ => unreachable!()
    };

    let mut buffer = Vec::new();
    for character in data.chars() {
        match character {
            'A' => buffer.push(0x00),
            'B' => buffer.push(0x01),
            'C' => buffer.push(0x02),
            'D' => buffer.push(0x03),
            'E' => buffer.push(0x04),
            'F' => buffer.push(0x05),
            'G' => buffer.push(0x06),
            'H' => buffer.push(0x07),
            'I' => buffer.push(0x08),
            'J' => buffer.push(0x09),
            'K' => buffer.push(0x0A),
            'L' => buffer.push(0x0B),
            'M' => buffer.push(0x0C),
            'N' => buffer.push(0x0D),
            'O' => buffer.push(0x0E),
            'P' => buffer.push(0x0F),
            'S' => { buffer.pop(); },
            'R' => { buffer.clear(); },
            _ => unreachable!()
        };
    }
    buffer = buffer.chunks(2).map(|x| match x {
        [upper, lower] => (upper << 4) | lower,
        _ => unreachable!()
    }).collect();

    Ok((PyBytes::new(py, &buffer).into(), frame_number))
}

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

    fn write(&mut self, b: Vec<u8>) -> PyResult<usize> {

        let amount = self.0.write(&b)
            .map_err(|x| PyErr::new::<PyIOError, _>(format!("Could not write to tunnel. Reason: {}", x.kind())))?;

        Ok(amount)
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn boyscout(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySFSSConnection>()?;
    m.add_function(wrap_pyfunction!(py_bytes_to_frames, m)?)?;
    m.add_function(wrap_pyfunction!(py_frame_to_bytes, m)?)?;
    Ok(())
}

use std::io::{BufReader, BufWriter};
use tun::platform::posix::{Reader, Writer};

pub struct SFSSManager(BufReader<Reader>, BufWriter<Writer>);

impl SFSSManager {
    pub fn new() -> Result<Self, tun::Error> {
        Self::new_helper(0)
    }

    fn new_helper(id: usize) -> Result<Self, tun::Error> {
        match Self::new_with_id(id) {
            Ok(x) => Ok(x),
            Err(e) => match e {
                tun::Error::InvalidName => Self::new_helper(id + 1),
                a => Err(a)
            }
        }
    }

    pub fn new_with_id(id: usize) -> Result<Self,tun::Error> {
        let mut config = tun::Configuration::default();
        config
            .name(format!("sfss{}", id))
            .address((10, 0, 0, 1))
            .netmask((255, 255, 255, 0))
            .up();

        #[cfg(target_os = "linux")]
        config.platform(|config| {
            config.packet_information(true);
        });

        let (d_read, d_write) = tun::create(&config)?.split();
        Ok(Self(BufReader::new(d_read), BufWriter::new(d_write)))
    }
}

impl <'a> SFSSManager {
    pub fn get_reader(&'a mut self) -> &'a mut BufReader<Reader> {
        &mut self.0
    }

    pub fn get_writer(&'a mut self) -> &'a mut BufWriter<Writer> {
        &mut self.1
    }
}
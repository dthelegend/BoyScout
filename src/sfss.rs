use std::io::{Read, Write};
use tun::platform::Device;

pub struct SFSSManager(Device);

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

        let d = tun::create(&config)?;
        Ok(Self(d))
    }
}

impl Read for SFSSManager {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        self.0.read(buf)
    }
}

impl Write for SFSSManager {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        self.0.write(buf)
    }

    fn flush(&mut self) -> std::io::Result<()> {
        self.0.flush()
    }
}

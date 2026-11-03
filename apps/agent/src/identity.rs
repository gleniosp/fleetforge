use std::fmt;
use std::str::FromStr;
use std::time::{SystemTime, UNIX_EPOCH};

const ALPHABET: &[u8] = b"0123456789ABCDEFGHJKMNPQRSTVWXYZ";

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct CanonicalId(ulid::Ulid);

impl FromStr for CanonicalId {
    type Err = String;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        let bytes = value.as_bytes();
        if bytes.len() != 26 || bytes[0] > b'7' || !bytes.iter().all(|b| ALPHABET.contains(b)) {
            return Err(
                "expected a canonical uppercase 26-character ULID (first character 0–7)".into(),
            );
        }
        value.parse().map(Self).map_err(|_| "invalid ULID".into())
    }
}

impl fmt::Display for CanonicalId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}

impl CanonicalId {
    pub fn generate() -> Result<Self, String> {
        let millis = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(|_| "clock precedes Unix epoch")?
            .as_millis();
        if millis > 0xffff_ffff_ffff {
            return Err("clock exceeds ULID timestamp range".into());
        }
        let mut random = [0u8; 16];
        getrandom::fill(&mut random).map_err(|_| "secure randomness unavailable")?;
        Ok(Self(ulid::Ulid::from_parts(
            millis as u64,
            u128::from_be_bytes(random),
        )))
    }
}

macro_rules! identity_type {
    ($name:ident) => {
        #[derive(Clone, Debug, Eq, PartialEq, serde::Deserialize)]
        #[serde(try_from = "String")]
        pub struct $name(CanonicalId);
        impl TryFrom<String> for $name {
            type Error = String;
            fn try_from(value: String) -> Result<Self, Self::Error> {
                value.parse().map(Self)
            }
        }
        impl fmt::Display for $name {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                self.0.fmt(f)
            }
        }
    };
}
identity_type!(AssetId);
identity_type!(DeviceId);
identity_type!(TenantId);
identity_type!(AuthorityId);
identity_type!(AssignmentId);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn canonical_boundaries_and_rejections() {
        for valid in [
            "00000000000000000000000000",
            "7ZZZZZZZZZZZZZZZZZZZZZZZZZ",
            "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        ] {
            assert_eq!(valid.parse::<CanonicalId>().unwrap().to_string(), valid);
        }
        for invalid in [
            "",
            "01arz3ndektsv4rrffq69g5fav",
            "8ZZZZZZZZZZZZZZZZZZZZZZZZZ",
            "01ARZ3NDEKTSV4RRFFQ69G5FAI",
            "01ARZ3NDEKTSV4RRFFQ69G5FAL",
            "01ARZ3NDEKTSV4RRFFQ69G5FAO",
            "01ARZ3NDEKTSV4RRFFQ69G5FAU",
            "0000000000000000000000000",
            "000000000000000000000000000",
            "é0000000000000000000000000",
        ] {
            assert!(invalid.parse::<CanonicalId>().is_err(), "{invalid}");
        }
    }

    #[test]
    fn asset_and_device_have_distinct_rust_types() {
        assert_ne!(
            std::any::TypeId::of::<AssetId>(),
            std::any::TypeId::of::<DeviceId>()
        );
    }

    #[test]
    fn secure_generation_produces_distinct_canonical_ids() {
        let first = CanonicalId::generate().unwrap();
        let second = CanonicalId::generate().unwrap();
        assert_ne!(first, second);
        assert_eq!(first.to_string().parse::<CanonicalId>().unwrap(), first);
    }
}

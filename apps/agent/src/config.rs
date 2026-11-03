use crate::identity::{AssetId, AssignmentId, AuthorityId, DeviceId, TenantId};
use serde::Deserialize;
use std::io::Read;
use std::path::{Path, PathBuf};

const MAX_CONFIG_BYTES: u64 = 16 * 1024;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Config {
    pub asset_id: AssetId,
    pub device_id: DeviceId,
    pub assignment: Assignment,
    pub state_dir: PathBuf,
    pub runtime_dir: PathBuf,
    pub authority_endpoint: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Assignment {
    pub asset_id: AssetId,
    pub device_id: DeviceId,
    pub tenant_id: TenantId,
    pub authority_id: AuthorityId,
    pub assignment_id: AssignmentId,
}

impl Config {
    pub fn load(path: &Path) -> Result<Self, String> {
        let file = std::fs::File::open(path).map_err(|e| format!("open configuration: {e}"))?;
        if !file.metadata().map_err(|e| e.to_string())?.is_file() {
            return Err("configuration must be a regular file".into());
        }
        let mut text = String::new();
        file.take(MAX_CONFIG_BYTES + 1)
            .read_to_string(&mut text)
            .map_err(|e| format!("read configuration: {e}"))?;
        if text.len() as u64 > MAX_CONFIG_BYTES {
            return Err("configuration exceeds 16 KiB".into());
        }
        // Do not include TOML parser errors: they may quote sensitive input.
        let config: Self =
            toml::from_str(&text).map_err(|_| "invalid configuration schema or ID")?;
        config.validate()?;
        Ok(config)
    }

    fn validate(&self) -> Result<(), String> {
        if self.asset_id != self.assignment.asset_id || self.device_id != self.assignment.device_id
        {
            return Err("identity does not match assignment".into());
        }
        if self.asset_id.to_string() == self.device_id.to_string() {
            return Err("asset/device uniqueness conflict".into());
        }
        let state = directory(&self.state_dir)?;
        let runtime = directory(&self.runtime_dir)?;
        if state.starts_with(&runtime) || runtime.starts_with(&state) {
            return Err("state and runtime directories must be disjoint".into());
        }
        let uri: http::Uri = self
            .authority_endpoint
            .parse()
            .map_err(|_| "invalid authority endpoint")?;
        let authority = uri
            .authority()
            .ok_or("authority endpoint requires a host")?;
        let raw_authority = authority.as_str();
        let port_text = if raw_authority.starts_with('[') {
            raw_authority
                .split_once(']')
                .map(|(_, rest)| rest)
                .unwrap_or(":invalid")
        } else {
            raw_authority
                .strip_prefix(authority.host())
                .unwrap_or(":invalid")
        };
        if !port_text.is_empty()
            && (!port_text.starts_with(':')
                || port_text[1..].parse::<u16>().ok().is_none_or(|p| p == 0))
        {
            return Err("invalid authority port".into());
        }
        if self.authority_endpoint.contains('#')
            || uri.scheme_str() != Some("wss")
            || authority.host().is_empty()
            || authority.as_str().contains('@')
            || uri
                .path_and_query()
                .is_some_and(|p| p.as_str().contains('#'))
            || authority.port().is_some_and(|p| p.as_u16() == 0)
        {
            return Err("authority endpoint requires wss, a host and a valid optional port; credentials/fragments forbidden".into());
        }
        Ok(())
    }
}

fn directory(path: &Path) -> Result<PathBuf, String> {
    if !path.is_absolute() || !path.is_dir() {
        return Err("state/runtime paths must be existing absolute directories".into());
    }
    let canonical = path
        .canonicalize()
        .map_err(|e| format!("resolve directory: {e}"))?;
    if path != canonical || canonical.parent().is_none() {
        return Err("state/runtime paths must be canonical non-root directories".into());
    }
    Ok(canonical)
}

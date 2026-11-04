use crate::{config::Config, identity::CanonicalId};
use std::time::Duration;
use tracing::Instrument;

pub fn run(path: std::path::PathBuf) -> Result<(), String> {
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .map_err(|e| format!("initialize runtime: {e}"))?;
    let result = runtime.block_on(async {
        let (config, instance) = tokio::time::timeout(
            Duration::from_secs(5),
            tokio::task::spawn_blocking(move || {
                let config = Config::load(&path)?;
                crate::storage::initialize(&config)?;
                Ok::<_, String>((config, CanonicalId::generate()?))
            }),
        )
        .await
        .map_err(|_| "configuration startup exceeded five seconds")?
        .map_err(|_| "configuration worker failed")??;
        serve(config, instance).await
    });
    // Bound waiting for a stalled startup filesystem worker as well.
    runtime.shutdown_timeout(Duration::from_secs(1));
    result
}

async fn serve(config: Config, instance: CanonicalId) -> Result<(), String> {
    let (writer, _guard) = tracing_appender::non_blocking::NonBlockingBuilder::default()
        .buffered_lines_limit(128)
        .lossy(true)
        .finish(std::io::stderr());
    tracing_subscriber::fmt()
        .json()
        .with_writer(writer)
        .with_current_span(true)
        .try_init()
        .map_err(|e| format!("initialize tracing: {e}"))?;
    async {
        let mut terminate = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())
            .map_err(|e| format!("install termination handler: {e}"))?;
        let mut interrupt = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::interrupt())
            .map_err(|e| format!("install interrupt handler: {e}"))?;
        let mut tick = tokio::time::interval(Duration::from_secs(5));
        tick.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Skip);
        tracing::info!(code = "agent_started", liveness = "alive", workload_health = "unknown", workload_process = "absent");
        loop {
            tokio::select! {
                biased;
                _ = terminate.recv() => break,
                _ = interrupt.recv() => break,
                _ = tick.tick() => tracing::info!(code = "agent_liveness", liveness = "alive", workload_health = "unknown", workload_process = "absent"),
            }
        }
        // No child or durable work exists in this slice; there is nothing to drain.
        tracing::info!(code = "agent_stopped", liveness = "stopped", workload_health = "unknown");
        Ok(())
    }.instrument(tracing::info_span!("agent", component = "agent", asset_id = %config.asset_id,
        device_id = %config.device_id, tenant_id = %config.assignment.tenant_id,
        authority_id = %config.assignment.authority_id, assignment_id = %config.assignment.assignment_id,
        agent_instance = %instance)).await
}

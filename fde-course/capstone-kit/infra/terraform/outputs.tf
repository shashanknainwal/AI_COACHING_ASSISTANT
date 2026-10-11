output "service_url" {
  description = "URL of the deployed service"
  value       = google_cloud_run_v2_service.agent.uri
}

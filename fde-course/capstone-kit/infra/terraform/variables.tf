# Skeleton only. Fill these in with your own project, then: terraform init && terraform validate
# Applying creates billable resources. You don't need to apply it for the capstone.

variable "project_id" {
  description = "Google Cloud project id"
  type        = string
}

variable "region" {
  description = "Region for the service"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Name of the service"
  type        = string
  default     = "capstone-agent"
}

variable "image" {
  description = "Container image built from infra/Dockerfile and pushed to a registry"
  type        = string
}

variable "anthropic_key_secret_id" {
  description = "Secret Manager secret id holding ANTHROPIC_API_KEY (create it outside Terraform so the key never lands in state)"
  type        = string
  default     = "anthropic-api-key"
}

variable "max_instances" {
  description = "Upper bound on instances: also an upper bound on spend"
  type        = number
  default     = 2
}

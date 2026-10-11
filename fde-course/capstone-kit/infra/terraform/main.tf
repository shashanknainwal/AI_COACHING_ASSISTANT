# A generic container-service skeleton, written for Google Cloud Run because
# it is the shortest to read. The same shape maps to AWS ECS on Fargate:
#   google_cloud_run_v2_service    -> aws_ecs_service + aws_ecs_task_definition
#   Secret Manager secret          -> AWS Secrets Manager secret in the task's "secrets"
#   service account                -> task execution role + task role (least privilege)
#   ingress / IAM invoker          -> load balancer + security groups or API Gateway
# Check the provider docs for current argument names before you rely on this.

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# A dedicated identity for the service: it may read one secret and nothing else.
resource "google_service_account" "agent" {
  account_id   = "${var.service_name}-sa"
  display_name = "Capstone agent runtime"
}

resource "google_secret_manager_secret_iam_member" "key_reader" {
  secret_id = var.anthropic_key_secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_cloud_run_v2_service" "agent" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL" # tighten to internal + a load balancer for anything real

  template {
    service_account = google_service_account.agent.email

    scaling {
      max_instance_count = var.max_instances
    }

    containers {
      image = var.image

      ports {
        container_port = 8080
      }

      env {
        name = "ANTHROPIC_API_KEY"
        value_source {
          secret_key_ref {
            secret  = var.anthropic_key_secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "CAPSTONE_MODEL"
        value = "claude-haiku-5-5"
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }

  depends_on = [google_secret_manager_secret_iam_member.key_reader]
}

# No public invoker binding on purpose: callers need IAM permission to invoke.
# Add a google_cloud_run_v2_service_iam_member for a specific caller if needed.

variable "kubernetes_context" {
  type = string
  default = "docker-desktop"
}

variable "kubernetes_config_path" {
  type = string
  default = "~/.kube/config"
}
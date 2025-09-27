variable "container_image" {
  type = string
}

variable "vault_addr" {
  type = string
  
}

variable "vault_token" {
  type = string
  sensitive = true
}
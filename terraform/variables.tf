variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_key_path" {}
variable "aws_region" {
    default = "us-east-1"
}
variable "amis" {
    default = {
        us-east-1 = "ami-86562dee"
        us-west-1 = "ami-50120b15"
    }
}

variable "git_repo" {}
variable "app" {}

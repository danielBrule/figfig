az login 
REM az login --use-device-code


REM optional, create resource group
REM  .\create_tf_backend.ps1 -env dev
REM     .\create_tf_backend.ps1 -env prod


cd terraform
terraform init -backend-config="envs/dev/backend.tf"
terraform plan -var-file="envs/dev/terraform.tfvars"
terraform apply -var-file="envs/dev/terraform.tfvars" -auto-approve

REM terraform init -backend-config="envs/prod/backend.tf" -reconfigure
REM terraform plan -var-file="envs/prod/terraform.tfvars"
REM terraform apply -var-file="envs/prod/terraform.tfvars" -auto-approve


cd ..
az acr login --name figfigacrdev

docker build -f docker/Dockerfile --build-arg ENV=dev -t figfigacrdev.azurecr.io/figfig-app:dev .
REM docker build --build-arg ENV=prod -t figfigacr.azurecr.io/figfig-app:latest .


docker push figfigacrdev.azurecr.io/figfig-app:dev
REM az keyvault set-policy --name figfig-key-vault-dev --spn 5809b5c3-c9f6-466b-a200-7e3e03d7ef5b --secret-permissions get list

docker run --env-file .env.dev figfigacrdev.azurecr.io/figfig-app:dev




REM create service principal, one off not to be reused 
REM az ad sp create-for-rbac --name figscraper --role Contributor --scopes /subscriptions/051a6d90-968b-4010-896c-8bdb26a892d0

REM create venv, one off not be reused 
REM py -3.13 -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./venv\Scripts\activate
REM pip install -r requirements.txt
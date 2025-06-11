az login 

az login --use-device-code

cd infra
@REM ../terraform destroy -auto-approve
@REM ../terraform plan 
@REM ../terraform apply  -auto-approve

../terraform destroy -auto-approve; ../terraform init; ../terraform plan ; ../terraform apply  -auto-approve


cd ..
az acr login --name figfigacr 

docker build -t figfigacr.azurecr.io/figfig-app:v1 .

docker push figfigacr.azurecr.io/figfig-app:v1 

az keyvault set-policy --name figfig-key-vault --spn 5809b5c3-c9f6-466b-a200-7e3e03d7ef5b --secret-permissions get list

docker run --env-file .env figfigacr.azurecr.io/figfig-app:v1




REM create service principal, one off not to be reused 
REM az ad sp create-for-rbac --name figscraper --role Contributor --scopes /subscriptions/051a6d90-968b-4010-896c-8bdb26a892d0

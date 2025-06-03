az login 

az login --use-device-code

cd infra
../terraform destroy
../terraform plan 
../terraform apply 

cd ..
az acr login --name figfigacr 

docker build -t figfigacr.azurecr.io/figfig-app:v1 .

docker push figfigacr.azurecr.io/figfig-app:v1 

az acr repository list --name figfigacr --output table

REM Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
REM ./venv\Scripts\activate
REM pip install -r requirements.txt
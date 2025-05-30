../terraform plan 
../terraform apply 

az login 

az acr login --name figfigacr 

docker build -t figfigacr.azurecr.io/figfig-app:v1 .

docker push figfigacr.azurecr.io/figfig-app:v1 .    

az acr repository list --name figfigacr --output table
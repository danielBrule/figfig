az login 

az acr login --name figfigacr --expose-token --output tsv --query accessToken | docker login figfigacr.azurecr.io --username 00000000-0000-0000-0000-000000000000 --password-stdin
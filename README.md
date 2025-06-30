# 1. README
view preview: 
`Ctrl+Shift+V`

# 2. Initialisation 
## 2.1.  figfig-tfstate-rg
The figfig-tfstate-rg resource group is used to store the Terraform state remotely in Azure. This is a best practice to enable collaboration and state locking, especially when multiple people or environments manage the same infrastructure.

### 2.1.1. Usage of figfig-tfstate-rg
It holds:
* A Storage Account – e.g., figfigtfstatedev or figfigtfstateprod
* A Blob Container – usually named tfstate
* A .tfstate file inside the blob container – Terraform uses this to track real infrastructure
This is used in the Terraform backend config to safely manage and persist state.

### 2.1.2. Creation
cf. `create_tf_backend.ps1`
```cmd
.\create_tf_backend.ps1 -env dev
.\create_tf_backend.ps1 -env prod
```

## 2.2. Create service principal 
Azure CLI command that creates a service principal for use with role-based access control (RBAC) in Azure
```cmd
az ad sp create-for-rbac --name figscraper_sp --role Owner --scopes /subscriptions/051a6d90-968b-4010-896c-8bdb26a892d0
REM Return
REM * AppId: The client ID of the service principal
REM * Password: The client secret (used like a password)
REM * Tenant: The Azure AD tenant ID

az role assignment create --assignee <AppID> --role "User Access Administrator" --scope /subscriptions/051a6d90-968b-4010-896c-8bdb26a892d0
  
  
  

REM DELETE SP
az ad sp list --display-name figscraper_sp --query "[].{Name:displayName, AppId:appId, ObjectId:objectId}" -o table
az ad sp delete --id 50e98d58-d5e9-4d9c-b61d-b55791e552df
```

Update terraform/envs/[dev/prod]/terraform.tfvars
Update github [url](https://github.com/danielBrule/figfig/settings/secrets/actions):
* AZURE_CLIENT_ID
* AZURE_CLIENT_SECRET
* AZURE_TENANT_ID


## 2.3. Python env initialisation 
```cmd
py -3.13 -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./venv\Scripts\activate
pip install -r requirements.txt
```


## 2.4. Setting Up Azure Federated Identity for GitHub Actions

This section documents the configuration of federated identity credentials in Azure AD to enable secure, passwordless authentication for GitHub Actions using OpenID Connect (OIDC). It includes steps to link a GitHub repo branch to a service principal via Azure CLI.

```cmd
REM DEV
$json = @{
   name        = "github-actions-dev"
   issuer      = "https://token.actions.githubusercontent.com"
   subject     = "repo:danielBrule/figfig:ref:refs/heads/dev"
   description = "Federated identity for GitHub Actions"
   audiences   = @("api://AzureADTokenExchange")
 } | ConvertTo-Json -Depth 3
REM # Save to a file
$json | Out-File -Encoding utf8 federated.json

az ad app federated-credential create --id <appid> --parameters federated.json


REM prod
$json = @{
>>   name        = "github-actions-prod"
>>   issuer      = "https://token.actions.githubusercontent.com"
>>   subject     = "repo:danielBrule/figfig:ref:refs/heads/main"
>>   description = "Federated identity for GitHub Actions"
>>   audiences   = @("api://AzureADTokenExchange")
>> } | ConvertTo-Json -Depth 3
REM # Save to a file
$json | Out-File -Encoding utf8 federated.json

az ad app federated-credential create --id <appid> --parameters federated.json


```


# 3. Login
```az login ```

Alternatively: 
```az login --use-device-code```

[login URL](https://microsoft.com/devicelogin)


# 4. Creation terraform / docker from vs code 

```cmd
REM DEV
cd terraform
terraform init -backend-config="envs/dev/backend.tf"
terraform destroy -auto-approve -var-file="envs/dev/terraform.tfvars"
terraform apply -target="azurerm_resource_group.main" -target="module.network" -auto-approve -var-file="envs/dev/terraform.tfvars" 
terraform apply -target="module.acr" -var-file="envs/dev/terraform.tfvars" -auto-approve
az acr login --name figfigacrdev
docker build -f docker/Dockerfile --build-arg ENV=dev -t figfigacrdev.azurecr.io/figfig-app:latest .
docker push figfigacrdev.azurecr.io/figfig-app:latest




REM PROD
terraform destroy -auto-approve -var-file="envs/prod/terraform.tfvars"
terraform init -backend-config="envs/prod/backend.tf"
terraform apply -target="azurerm_resource_group.main" -target="module.network" -auto-approve -var-file="envs/prod/terraform.tfvars" 
terraform apply -target="module.acr" -var-file="envs/prod/terraform.tfvars" -auto-approve

az acr login --name figfigacrprod
docker build -f docker/Dockerfile --build-arg ENV=prod -t figfigacrprod.azurecr.io/figfig-app:latest .
docker push figfigacrprod.azurecr.io/figfig-app:latest

terraform apply -target="module.sql" -var-file="envs/prod/terraform.tfvars" -auto-approve
terraform apply -target="module.servicebus" -var-file="envs/prod/terraform.tfvars" -auto-approve
terraform apply -target="module.keyvault" -var-file="envs/prod/terraform.tfvars" -auto-approve
terraform apply -target="module.containers" -var-file="envs/prod/terraform.tfvars" -auto-approve

```




# 5. Azure Useful commands 

```cmd
REM AZURE SUBSCRIPTION 
az account show --query id --output tsv

REM AZURE_CLIENT_ID (appid): 
az ad sp list --display-name figscraper --query [].appId -o tsv

REM AZURE_TENANT_ID (tenantid):
az account show --query tenantId -o tsv

REM AZURE_SUBSCRIPTION_ID: 
az account show --query id -o tsv

REM RESET AZURE_CLIENT_SECRET (pwd): 
az ad app credential reset --id $APP_ID --append --display-name "GitHub Actions Secret" --years 1

```

# 6. Env files 
## 6.1. Root
### 6.1.2. .env.dev
```cmd
# App settings
ENV=dev
DEBUG=True
PORT=8000


DB_SERVER=figfig-sql-dev.database.windows.net
DB_NAME=figfig-db-dev-dev
DB_USER=sqladmin
DB_PASSWORD=Th1s1sAPassw0rd
DB_DRIVER=ODBC Driver 17 for SQL Server

# ACR / Image name
DOCKER_IMAGE_NAME=figfigacr.azurecr.io/figfig-app:v1
PYTHONPATH=.

LOG_DATETIME_FORMAT= "%Y-%m-%d_%H"
LOG_FORMAT="%(asctime)s - %(levelname)s - %(message)s"

KEY_VAULT_NAME=figfig-key-vault-dev

AZURE_CLIENT_ID=<XXX>
AZURE_TENANT_ID=<XXX>
AZURE_CLIENT_SECRET=<XXX>
```

### 6.1.2. .env.prod

# App settings
```cmd
ENV=prod
DEBUG=True
PORT=8000


DB_SERVER=figscraper-sql-prod.database.windows.net
DB_NAME=figfig-db-dev-prod
DB_USER=sqladmin
DB_PASSWORD=Th1s1sAPassw0rd
DB_DRIVER=ODBC Driver 17 for SQL Server

# ACR / Image name
DOCKER_IMAGE_NAME=figfigacr.azurecr.io/figfig-app:v1
PYTHONPATH=.

LOG_DATETIME_FORMAT= "%Y-%m-%d_%H"
LOG_FORMAT="%(asctime)s - %(levelname)s - %(message)s"

KEY_VAULT_NAME=figfig-key-vault-prod

AZURE_CLIENT_ID=<XXX>
AZURE_TENANT_ID=<XXX>
AZURE_CLIENT_SECRET=<XXX>
```

## 6.2. terraform
### 6.2.2. terraform/envs/dev/terraform.tfvars
```cmd
env = "dev"
sql_password = "<XXX>"
keyvault_name = "figfig-kv-dev"
subscription_id = "<XXX>"
client_id = "<XXX>"
tenant_id = "<XXX>"
client_secret ="<XXX>"
```
### 6.2.2. terraform/envs/prod/terraform.tfvars
```cmd
env = "prod"
sql_password = "<XXX>"
keyvault_name = "figfig-kv-prod"
subscription_id = "<XXX>"
client_id = "<XXX>"
tenant_id = "<XXX>"
```

# 6. Github actions secrets 
|Key                        |value|
|---------------------------|-------------------|
|AZURE_CLIENT_ID            | cf 2.2.           |
|AZURE_CLIENT_SECRET        | cf 2.2.           |
|AZURE_SUBSCRIPTION_ID      | cf 5.             |
|AZURE_TENANT_ID            | cf 2.2.           |
|DB_DRIVER                  | ODBC Driver 17 for SQL Server                  |
|KEY_VAULT_NAME             | TODEL??           |
|LOG_DATETIME_FORMAT        | "%Y-%m-%d_%H"     |
|LOG_FORMAT                 | "%(asctime)s - %(levelname)s - %(message)s"                  |
|PYTHONPATH                 | .                 |
|REGISTRY_PASSWORD          | TODEL??           |
|REGISTRY_USERNAME          | TODEL??           |
|TF_DEV_ACR_NAME            | figfigacr      |
|TF_DEV_ENV                 | deb               |
|TF_DEV_IMAGE_NAME          | ??                |
|TF_DEV_KEYVAULT_NAME       | figfig-kv-dev     |
|TF_DEV_LOCATION            | uksouth           |
|TF_DEV_PROJECT_NAME        | FigFigRG-dev      |
|TF_DEV_RESOURCE_GROUP_NAME | FigFigRG??        |
|TF_DEV_SQL_ADMIN           | sqladmin      |
|TF_DEV_SQL_PASSWORD        | up to you         |



# 7. Feature Matrix: ACI, AKS, and App Services
| Feature                 | ACI                          | AKS                          | App Services for Containers       |
|-------------------------|------------------------------|-------------------------------|-----------------------------------|
| Management overhead     | Very Low                     | High                          | Low                               |
| Scaling                 | Manual / via Logic Apps      | Auto (pods, nodes)            | Auto (limited)                    |
| Best for                | Jobs, events, scrapers       | Complex, large systems        | APIs, daemons, long-run           |
| Pricing model           | Per-second while running     | Per node/pod                  | Per-instance/hourly               |
| Start-up time           | Fast                         | Moderate                      | Fast                              |
| Networking control      | Limited (unless in VNet)     | Full VNet, NSG, Ingress       | Limited                           |
| Orchestration features  | None                         | Full Kubernetes               | Minimal                           |

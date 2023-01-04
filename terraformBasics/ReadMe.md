1. Service accounts - accounts created for particular services, used to manage credentials and access for service.
   Note - GOOGLE_APPLICATION_CREDENTIALS env var is the credential gcloud cli will use to login, we change this env var to login as diff user
   We need to enable IAM Apis because that is what our local machine uses to interact with the google cloud resources.

### steps so far

## create project

1. Google cloud dashboad --> iam --> service accounts
2. Create new service account --> viewer role (will be changed later)
3. Context menu on new service account --> manage keys --> create new key --> json (will download json private key)
4. Set GOOGLE_APPLICATION_CREDENTIALS env var to point to path of downloaded json private key
5. login with gcloud auth application-default login
6. Add extra roles to service account to allow us create the resources we want via terraform (we want to create google cloud storage and big query data warehouse resources)
7. go to iam screen, select service account we just created --> pencil icon (edit principal) --> add another role --> add storage admin (read/write gcs buckets)
   --> add storage object admin(read/write objects within gcs) --> add big query admin
8. Next we need to enable apis for this project (Ensure we are enabling apis for our current project)
9. Navigation drawer --> APIS & Services --> Enable APIS and Services --> search for Identity and Access Management (IAM) API --> next search for
   IAM Service Account Credentials API and enable

#### Declarations

- `terraform`: configure basic Terraform settings to provision your infrastructure
  - `required_version`: minimum Terraform version to apply to your configuration
  - `backend`: stores Terraform's "state" snapshots, to map real-world resources to your configuration.
    - `local`: stores state file locally as `terraform.tfstate`
  - `required_providers`: specifies the providers required by the current module
- `provider`:
  - adds a set of resource types and/or data sources that Terraform can manage
  - The Terraform Registry is the main directory of publicly available providers from most major infrastructure platforms.
- `resource`
  - blocks to define components of your infrastructure
  - Project modules/resources: google_storage_bucket, google_bigquery_dataset, google_bigquery_table
- `variable` & `locals`
  - runtime arguments and constants

#### Execution steps

1. `terraform init`:
   - Initializes & configures the backend, installs plugins/providers, & checks out an existing configuration from a version control
2. `terraform plan`:
   - Matches/previews local changes against a remote state, and proposes an Execution Plan.
3. `terraform apply`:
   - Asks for approval to the proposed plan, and applies changes to cloud
4. `terraform destroy`
   - Removes your stack from the Cloud

### In Variables.tf

1. Locals - are constants

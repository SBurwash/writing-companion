### Foreword

- Mention that article may very well be already deprecated, as openflow is changing so quickly. By the time reader reads this, issues may already be solved, but it’s still good to share the knowledge.

### **I. What is OpenFlow, and why should you care?**

- **What is Snowflake Openflow?**
    - Briefly introduce Openflow as a new technology from Snowflake, based on Apache NiFi.
    - Mention its current GA status (AWS) and its evolving nature (as mentioned above).
- **Why Openflow? Solving Data Ingestion Challenges**
    - Explain the core problem: Leveraging data in Snowflake often requires ingesting from diverse sources.
    - Highlight the "missing piece" that Openflow addresses: bringing EL capabilities directly into Snowflake.
    - Contrast with previous approaches (custom integrations, external services like Fivetran/Airbyte) and emphasize Openflow's value proposition.
        - Everything in one place (inside Snowflake)
        - More connectors coming every day
        - No-code interface (easier for non-tech users, although there is a learning curve to understand different component
    - Briefly mention this article is an account of a practical setup journey, including common hurdles.

---

### **II. Setting Up Openflow: A Step-by-Step Walkthrough**

- **A. Initial Setup: Following the Official Tutorial**
    - Start with the official Snowflake tutorial link: https://docs.snowflake.com/en/user-guide/data-integration/openflow/setup-openflow
    - **Crucial Tip:** Emphasize the importance of *thoroughly* reading and following the tutorial steps. Share your personal experience of getting stuck due to skipping steps.
    - **Deployment Options:** Clarify the "no fully managed service" aspect.
        - Option 1: Leverage an existing VPC.
        - Option 2: Let Snowflake create a VPC.
        - Note the main impact: distinction between CloudFormation files.
    - Once you’ve created your deployment in Openflow, you’ll be provided with a cloudformation file which you can leverage in the following step
- **B. Deploying the Stack in AWS: Common Challenges and Solutions**
    - Explain that CloudFormation sets up multiple resources, including an **EC2** instance responsible for orchestrating subsequent resource creation.
    - Detail the `setup-agent.sh` script: It runs at instance start and downloads other necessary scripts from the `host-scripts` directory.
    - **Challenge 1: Snowflake Instance within a VPC**
        - **Problem:** Issues encountered when the Snowflake instance is inside a VPC.
        - **Snowflake's Provision:** Acknowledge that the Snowflake team accounts for this in their docs (https://docs.snowflake.com/en/user-guide/data-integration/openflow/setup-openflow#create-a-deployment-in-your-cloud).
        - **The Catch:** Explain that you only get the NAT gateway IP address *after* stack creation, requiring manual intervention.
        - **Solution:**
            1. Grab the NAT gateway IP from your AWS infrastructure.
            2. Add it to your Network Policy.
            3. Manually re-run the `setup-agents.sh` script *inside* the EC2 instance (requires connecting via terminal/console).
    - **Challenge 2: `host-scripts/initialize.sh` Script Issues**
        - **Problem:** The script's logic, intended to create ECR repositories if they don't exist, fails due to how error output is handled when `set -eo pipefail` is active.
        - **Detailed Explanation:** Show the relevant code snippet and explain *why* the `grep -q RepositoryNotFoundException` fails due to `pipefail`.
        - **Solution:** Remove the `set -eo pipefail` flag from the script.
    - **Monitoring Resource Creation:** Provide the command to track resource creation: `journalctl -u openflow-apply-infrastructure -f -n 500`
- **C. Troubleshooting Dataplane-UI Resource Setup**
    - **Problem:** Resources for `dataplane-ui` (a key service) were not being created as expected.
    - **Diagnostic Process:** Explain how investigation revealed the dependent image couldn't be found in the ECR repository.
    - **Root Cause:** The `host-scripts/sync-images.sh` script was using the `dataplane-ui-chart` tag for the `dataplane-ui` image.
    - **Solution:**
        1. Identify the correct image version (e.g., `0.7.0`) in the `snowflake_images` repository.
        2. Explain the dependency: `dataplane-ui` updates are tied to `dataplane-ui-chart` changes, necessitating the deletion of the existing image in `snowflake-openflow/openflow-dataplane-ui-chart`.
        3. Provide the code snippet illustrating the fix: Hard-set the image version to `0.7.0` within the `sync_image` function for `DPUI_CHART_REPOSITORY`.
        4. **Crucial Step:** Emphasize the need to *manually re-run* `host-scripts/sync-images.sh` after this change.
    - **Verification:** Re-run `journalctl -u openflow-apply-infrastructure -f -n 500` to confirm infrastructure population.

---

### **III. Configuring and Using Openflow**

- **A. Creating Your Runtime:**
    - Follow official documentation for runtime creation.
- **B. Importing Connectors:**
    - Discuss importing a connector, using your HubSpot connector experience as an example, with a link to relevant docs (e.g., Google Sheets connector link provided).
    - **Another Crucial Tip:** Reiterate the importance of reading all documentation *before* starting, reinforcing it with your experience.
- **C. Flow Development and Iteration:**
    - Note that parameter tuning may be required but is generally straightforward.

---

### **IV. Conclusion: Successful Deployment and Beyond**

- Reiterate the successful outcome ("Profit!").
- Briefly mention the benefits achieved by solving data ingestion challenges with Openflow.
- Perhaps a forward-looking statement about leveraging Openflow's capabilities.

### Additional context (for article generation only)

**`setup-agents.sh`**

```bash
#!/bin/bash
source /home/ec2-user/.env

image_name=$AGENT_IMAGE_REPOSITORY

instance_id=$(ec2-metadata -i | cut -d ' ' -f2)
agent_tags=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$instance_id" --query 'Tags[?!contains(Key, `aws:cloudformation`)&&!contains(Key, `Name`)]' | jq -c 'map(del(.ResourceId?, .ResourceType?))')

tags_array=()
while IFS= read -r tag; do
  tags_array+=("$tag")
done < <(echo "$agent_tags" | jq -r '.[] | "Key=\(.Key),Value=\(.Value)"')

repo_arn=$(aws ecr describe-repositories --region $AWS_REGION --repository-names snowflake-openflow/$image_name --query 'repositories[0].repositoryArn' --output text 2>&1)
if [ $? -eq 0 ]; then
  [ ${#tags_array[@]} -gt 0 ] && aws ecr tag-resource --resource-arn $repo_arn --tags "${tags_array[@]}"
elif echo $repo_arn | grep -q RepositoryNotFoundException; then
  aws ecr create-repository --region $AWS_REGION --repository-name snowflake-openflow/$image_name --tags "${tags_array[@]}"
else
  >&2 echo $repo_arn
fi

echo "Logging in to local private ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $IMAGE_REGISTRY

oauth_secret_id="snowflake-oauth2-$UNIQUE_SUFFIX"

oauth2_creds=$(aws secretsmanager get-secret-value --region $AWS_REGION --query SecretString --output text --secret-id $oauth_secret_id)
client_id=$(echo $oauth2_creds | jq -r '.clientID')
client_secret=$(echo $oauth2_creds | jq -r '.clientSecret')

oauth_resp=$(curl -s --request POST --url $SNOWFLAKE_OAUTH_TOKEN_URL \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode grant_type=client_credentials \
  --data-urlencode client_id=$client_id \
  --data-urlencode client_secret=$client_secret)
access_token=$(echo $oauth_resp | jq -er '.access_token')

[ $? -ne 0 ] && echo "Unable to obtain OAuth access token: "$(echo $oauth_resp | jq -r '.message') && exit 1

token_path="/home/ec2-user/access.token"
echo -n $access_token > $token_path

private_link_param=''
if [[ "$USE_IMAGE_REGISTRY_OVER_PRIVATE_LINK" == true ]]; then
  echo "Connecting to image registry using a private link"
  private_link_param='--private-link'
fi

spcs_params="""-x \
  --account=$SNOWFLAKE_ORG-$SNOWFLAKE_ACCOUNT \
  --database=$SNOWFLAKE_DATABASE \
  --schema=$SNOWFLAKE_SCHEMA \
  --host=${SNOWFLAKE_ACCOUNT_URL#"https://"} \
  --authenticator=OAUTH \
  --token-file-path=$token_path \
  --format=JSON
"""

snowflake_registry=$(snow spcs image-registry url $private_link_param $spcs_params | jq -r '.message')

set -e
echo "Logging in to Snowflake Image Registry https://$snowflake_registry ..."
echo $access_token | docker login "https://$snowflake_registry" \
  --username 0auth2accesstoken \
  --password-stdin

if [ -n "$AGENT_IMAGE_VERSION" ]; then
  image_tag=$AGENT_IMAGE_VERSION
else
  echo "Finding latest Agent image version in repo $SNOWFLAKE_IMAGE_REPOSITORY"
  image_tag=$(snow spcs image-repository list-images $SNOWFLAKE_IMAGE_REPOSITORY $spcs_params --like $image_name | jq -r ".[] | .tags" | sed -r 's/-/~/' | sort -Vr | sed -r 's/~/-/' | head -1)
  sed -i'' -E "s|^(AGENT_IMAGE_VERSION=).*|\1$image_tag|g" /home/ec2-user/.env
fi

rm $token_path

echo "Using Agent image version $image_tag"

snow_image_path="$SNOWFLAKE_DATABASE/$SNOWFLAKE_SCHEMA/$SNOWFLAKE_IMAGE_REPOSITORY/$image_name:$image_tag"
local_image_path=$IMAGE_REGISTRY/snowflake-openflow/$image_name:$image_tag
docker pull $snowflake_registry/$snow_image_path >/dev/null
docker tag $snowflake_registry/$snow_image_path $local_image_path
docker push $local_image_path >/dev/null

container_id=$(docker create "$IMAGE_REGISTRY/snowflake-openflow/$image_name:$image_tag")
docker cp "$container_id":/opt/openflow/host-scripts /home/ec2-user/
docker rm "$container_id" >/dev/null

chmod +x /home/ec2-user/host-scripts/*.sh
chown ec2-user:ec2-user /home/ec2-user/host-scripts/*

echo "Retrieved host scripts for $image_name:$image_tag"

sudo /home/ec2-user/host-scripts/initialize.sh

sudo systemctl stop openflow-setup-agent.timer
sudo systemctl disable openflow-setup-agent.timer
```

`host-scripts/initialize.sh`

```bash
#!/bin/bash
#
# Copyright (c) 2025 Snowflake Inc. All rights reserved.
# This software is proprietary and may not be disclosed to third parties without the express written consent of Snowflake Inc.
# Any unauthorized reproduction, distribution, modification, or use is strictly prohibited.
#
set -eo pipefail

source /home/ec2-user/.env

# Apply env vars that might not be present yet
grep -q '^AGENT_IMAGE_UPGRADE_PENDING=' /home/ec2-user/.env || sed -i'' '/^AGENT_IMAGE_VERSION=.*$/a AGENT_IMAGE_UPGRADE_PENDING=' /home/ec2-user/.env

# Create upgrade file, if it doesn't exist
touch /home/ec2-user/.upgrade
chown ec2-user:ec2-user /home/ec2-user/.upgrade
chmod 644 /home/ec2-user/.upgrade

# Add upgrade vars that might not be present yet
for key in \
  AGENT_IMAGE_VERSION_UPGRADE \
  OPERATOR_CHART_VERSION_UPGRADE \
  GATEWAY_IMAGE_VERSION_UPGRADE \
  DPS_CHART_VERSION_UPGRADE \
  DPUI_CHART_VERSION_UPGRADE; do
  grep -q "^$key=" "/home/ec2-user/.upgrade" || echo "$key=" >> "/home/ec2-user/.upgrade"
done

# Set up symbolic links to user-facing scripts
for script in create destroy diagnostics upgrade; do
  ln -sf /home/ec2-user/host-scripts/$script.sh /home/ec2-user/$script.sh
done

# Install helm, if necessary
if ! command -v helm >/dev/null 2>&1 || [[ "$(helm version --short --client 2>/dev/null)" != *"v3.16.4"* ]]; then
  wget https://get.helm.sh/helm-v3.16.4-linux-amd64.tar.gz
  tar -zxvf helm-v3.16.4-linux-amd64.tar.gz
  mv ./linux-amd64/helm /usr/local/bin/helm
  rm -rf helm-v3.16.4-linux-amd64.tar.gz linux-amd64
fi

# If Agent role is capable of tagging resources, get instance tags
agent_tags=''
if aws iam get-role-policy --role-name $(aws sts get-caller-identity --query Arn --output text | cut -d'/' -f2) --policy-name OpenflowAgentPolicy --query "PolicyDocument.Statement[?Effect=='Allow'].[Action]" --output text | fgrep -q 'ecr:TagResource'; then
  instance_id=$(ec2-metadata -i | cut -d ' ' -f2)
  agent_tags=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$instance_id" --query 'Tags[?!contains(Key, `aws:cloudformation`)&&!contains(Key, `Name`)]' | jq -c 'map(del(.ResourceId?, .ResourceType?))')
fi

tags_array=()
while IFS= read -r tag; do
  tags_array+=("$tag")
done < <(echo "$agent_tags" | jq -r '.[] | "Key=\(.Key),Value=\(.Value)"')

# Create other ECR repos, if necessary
declare -a repos=("$AGENT_IMAGE_REPOSITORY" "$EXTENSIONS_IMAGE_REPOSITORY" "$OPERATOR_IMAGE_REPOSITORY" "$OPERATOR_CHART_REPOSITORY" "$SERVER_IMAGE_REPOSITORY" "$DPS_IMAGE_REPOSITORY" "$DPS_CHART_REPOSITORY" "$DPUI_IMAGE_REPOSITORY" "$DPUI_CHART_REPOSITORY" "$GATEWAY_IMAGE_REPOSITORY")
for i in "${repos[@]}"
do
  repo_arn=$(aws ecr describe-repositories --region $AWS_REGION --repository-names snowflake-openflow/$i --query 'repositories[0].repositoryArn' --output text 2>&1)
  if [ $? -eq 0 ]; then
    # Apply tags to existing ECR repo, if Agent role is capable
    [ ${#tags_array[@]} -gt 0 ] && aws ecr tag-resource --resource-arn $repo_arn --tags "${tags_array[@]}"
  elif echo $repo_arn | grep -q RepositoryNotFoundException; then
    aws ecr create-repository --region $AWS_REGION --repository-name snowflake-openflow/$i --tags "${tags_array[@]}"
  else
    >&2 echo $repo_arn
  fi
done

# Create or replace systemctl service and timer for syncing images
cat <<\EOF > /etc/systemd/system/openflow-sync-images.service
[Unit]
Description="Sync images for Snowflake Openflow"

[Service]
Type=oneshot
User=ec2-user
Group=ec2-user
TimeoutSec=600
WorkingDirectory=/home/ec2-user
ExecStart=/home/ec2-user/host-scripts/sync-images.sh

[Install]
WantedBy=multi-user.target
EOF

# Create or replace systemctl service and timer for applying infrastructure
cat <<\EOF > /etc/systemd/system/openflow-apply-infrastructure.service
[Unit]
Description="Apply baseline Snowflake Openflow infrastructure configuration"
After=openflow-sync-images.service
Requires=openflow-sync-images.service

[Service]
User=ec2-user
Group=ec2-user
TimeoutSec=0
WorkingDirectory=/home/ec2-user
ExecStart=/home/ec2-user/host-scripts/apply-infrastructure.sh

[Install]
WantedBy=multi-user.target
EOF

cat <<\EOF > /etc/systemd/system/openflow-apply-infrastructure.timer
[Unit]
Description="Run openflow-apply-infrastructure.service every 10 minutes relative to deactivation time"
[Timer]
OnBootSec=0
OnUnitInactiveSec=10min
Unit=openflow-apply-infrastructure.service
[Install]
WantedBy=timers.target
EOF

# Create or replace systemctl service and timer for sending heartbeats
cat <<\EOF > /etc/systemd/system/openflow-heartbeat.service
[Unit]
Description="Send status heartbeat to Openflow Control Plane"
[Service]
User=ec2-user
Group=ec2-user
TimeoutSec=0
WorkingDirectory=/home/ec2-user
ExecStart=/home/ec2-user/host-scripts/heartbeat.sh
[Install]
WantedBy=multi-user.target
EOF

cat <<\EOF > /etc/systemd/system/openflow-heartbeat.timer
[Unit]
Description="Run openflow-heartbeat.service every 1 minute relative to deactivation time"
[Timer]
OnBootSec=0
OnUnitActiveSec=1min
AccuracySec=1s
Unit=openflow-heartbeat.service
[Install]
WantedBy=timers.target
EOF

# Pick up and apply any changes to the above services and timers that may have been previously scheduled
systemctl daemon-reload

# Enable the timers in case this is the first execution or new timers have been added
systemctl enable openflow-apply-infrastructure.timer
systemctl enable openflow-heartbeat.timer

# Start the timers or refresh any configuration changes above, if they already are running
systemctl restart openflow-apply-infrastructure.timer
systemctl restart openflow-heartbeat.timer
```

`host-scripts.sync-images.sh`
```bash
#!/bin/bash
#
# Copyright (c) 2025 Snowflake Inc. All rights reserved.
# This software is proprietary and may not be disclosed to third parties without the express written consent of Snowflake Inc.
# Any unauthorized reproduction, distribution, modification, or use is strictly prohibited.
#
source /home/ec2-user/.env

echo "Logging in to local private ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $IMAGE_REGISTRY

oauth_secret_id="snowflake-oauth2-$UNIQUE_SUFFIX"

oauth_creds=$(aws secretsmanager get-secret-value --region $AWS_REGION --query SecretString --output text --secret-id $oauth_secret_id)
client_id=$(echo $oauth_creds | jq -r '.clientID')
client_secret=$(echo $oauth_creds | jq -r '.clientSecret')

oauth_response=$(curl -s --request POST --url $SNOWFLAKE_OAUTH_TOKEN_URL \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode grant_type=client_credentials \
  --data-urlencode client_id=$client_id \
  --data-urlencode client_secret=$client_secret)

access_token=$(echo $oauth_response | jq -er '.access_token')

[ $? -ne 0 ] && echo "Unable to obtain OAuth access token: "$(echo $oauth_response | jq -r '.message') && exit 1

token_path="/home/ec2-user/access.token"
echo -n $access_token > $token_path

private_link_param=''
if [[ "$USE_IMAGE_REGISTRY_OVER_PRIVATE_LINK" == true ]]; then
    echo "Connecting to image registry using a private link"
    private_link_param='--private-link'
fi

spcs_params="""-x \
  --account=$SNOWFLAKE_ORG-$SNOWFLAKE_ACCOUNT \
  --database=$SNOWFLAKE_DATABASE \
  --schema=$SNOWFLAKE_SCHEMA \
  --host=${SNOWFLAKE_ACCOUNT_URL#"https://"} \
  --authenticator=OAUTH \
  --token-file-path=$token_path \
  --format=JSON
"""

snowflake_registry=$(snow spcs image-registry url $private_link_param $spcs_params | jq -r '.message')

echo "Logging in to Snowflake Image Registry https://$snowflake_registry ..."
echo $access_token | docker login "https://$snowflake_registry" \
  --username 0auth2accesstoken \
  --password-stdin

echo $access_token | helm registry login "https://$snowflake_registry" \
  --username 0auth2accesstoken \
  --password-stdin

echo "Discovering tags for repo $SNOWFLAKE_IMAGE_REPOSITORY"
latest_images=$(snow spcs image-repository list-images $SNOWFLAKE_IMAGE_REPOSITORY $spcs_params)

rm $token_path

echo "Found images\n$latest_images"

docker_keep_only() {
  local image_name="$1"
  local image_tag="$2"

  docker images | grep "$image_name" | grep -v "$image_tag" | awk '{ print $3}' | sort | uniq | xargs docker rmi -f 2>/dev/null
}

sync_image() {
  local image_name="$1"
  local image_tag="$2"

  snow_image_path="$SNOWFLAKE_DATABASE/$SNOWFLAKE_SCHEMA/$SNOWFLAKE_IMAGE_REPOSITORY/$image_name:$image_tag"

  echo "Checking $image_name:$image_tag"

  registry_id=$(echo $IMAGE_REGISTRY | cut -d'.' -f1)
  found_image_local_ecr="$(aws ecr describe-images --region $AWS_REGION --registry-id $registry_id --repository-name "snowflake-openflow/$image_name" --image-ids=imageTag=$image_tag 2>&1)"
  if [ $? -ne 0 ]; then
    echo "         $image_name:$image_tag not found locally, pulling from SPCS"
    if [[ "$image_name" == *"-chart" ]]; then
      helm pull oci://$snowflake_registry/$SNOWFLAKE_DATABASE/$SNOWFLAKE_SCHEMA/$SNOWFLAKE_IMAGE_REPOSITORY/$image_name --version $image_tag
      helm push $image_name-$image_tag.tgz oci://$IMAGE_REGISTRY/snowflake-openflow
      app_version=$(helm show values $image_name-$image_tag.tgz --jsonpath "{$.image.tag}")
      if [[ $OPERATOR_CHART_REPOSITORY == $image_name ]]; then
        echo "Pulling image $OPERATOR_IMAGE_REPOSITORY:$app_version for $image_name:$image_tag"
        sync_image $OPERATOR_IMAGE_REPOSITORY $app_version
      elif [[ $DPS_CHART_REPOSITORY == $image_name ]]; then
        echo "Pulling image $DPS_IMAGE_REPOSITORY:$app_version for $image_name:$image_tag"
        sync_image $DPS_IMAGE_REPOSITORY $app_version
      elif [[ $DPUI_CHART_REPOSITORY == $image_name ]]; then
        echo "Pulling image $DPUI_IMAGE_REPOSITORY:$app_version for $image_name:$image_tag"
        sync_image $DPUI_IMAGE_REPOSITORY 0.7.0
      fi
      rm ./$image_name-$image_tag.tgz
    else
      local_image_path=$IMAGE_REGISTRY/snowflake-openflow/$image_name:$image_tag
      docker pull $snowflake_registry/$snow_image_path >/dev/null
      docker tag $snowflake_registry/$snow_image_path $local_image_path
      docker push $local_image_path >/dev/null
    fi
  else
    echo "         $image_name:$image_tag found locally, no need to re-sync"
  fi
  echo
}

# If specific versions are set, make sure that we sync those
if [ -n "$AGENT_IMAGE_VERSION" ]; then
  sync_image $AGENT_IMAGE_REPOSITORY $AGENT_IMAGE_VERSION
fi

if [ -n "$GATEWAY_IMAGE_VERSION" ]; then
  sync_image $GATEWAY_IMAGE_REPOSITORY $GATEWAY_IMAGE_VERSION
fi

if [ -n "$OPERATOR_CHART_VERSION" ]; then
  sync_image $OPERATOR_CHART_REPOSITORY $OPERATOR_CHART_VERSION
fi

if [ -n "$DPS_CHART_VERSION" ]; then
  sync_image $DPS_CHART_REPOSITORY $DPS_CHART_VERSION
fi

if [ -n "$DPUI_CHART_VERSION" ]; then
  sync_image $DPUI_CHART_REPOSITORY $DPUI_CHART_VERSION
fi

declare -a repos=("$DPUI_CHART_REPOSITORY $AGENT_IMAGE_REPOSITORY" "$GATEWAY_IMAGE_REPOSITORY" "$OPERATOR_CHART_REPOSITORY" "$DPS_CHART_REPOSITORY" "$SERVER_IMAGE_REPOSITORY" "$EXTENSIONS_IMAGE_REPOSITORY")
for image_name in "${repos[@]}"
do
  # Find only the latest tag for this image
  latest_tag=$(echo "$latest_images" | jq -r ".[] | select(.image_name == \"$image_name\") | .tags" | sed -r 's/-/~/' | sort -Vr | sed -r 's/~/-/' | head -1)

  if [[ $AGENT_IMAGE_REPOSITORY == $image_name ]]; then
    if [ -z "$AGENT_IMAGE_VERSION" ]; then
      sync_image $image_name $latest_tag
      echo "Setting Agent image version to $latest_tag"
      sed -i'' -E "s|^(AGENT_IMAGE_VERSION=).*|\1$latest_tag|g" /home/ec2-user/.env
    elif [[ $AGENT_IMAGE_VERSION != $latest_tag ]]; then
      sync_image $image_name $latest_tag
      sed -i'' -E "s|^(AGENT_IMAGE_VERSION_UPGRADE=).*|\1$latest_tag|g" /home/ec2-user/.upgrade
    fi
  elif [[ $GATEWAY_IMAGE_REPOSITORY == $image_name ]]; then
    if [ -z "$GATEWAY_IMAGE_VERSION" ]; then
      sync_image $image_name $latest_tag
      echo "Setting Gateway image version to $latest_tag"
      sed -i'' -E "s|^(GATEWAY_IMAGE_VERSION=).*|\1$latest_tag|g" /home/ec2-user/.env
    elif [[ $GATEWAY_IMAGE_VERSION != $latest_tag ]]; then
      sync_image $image_name $latest_tag
      sed -i'' -E "s|^(GATEWAY_IMAGE_VERSION_UPGRADE=).*|\1$latest_tag|g" /home/ec2-user/.upgrade
    fi
  elif [[ $OPERATOR_CHART_REPOSITORY == $image_name ]]; then
    if [ -z "$OPERATOR_CHART_VERSION" ]; then
      sync_image $image_name $latest_tag
      echo "Setting Operator chart version to $latest_tag"
      sed -i'' -E "s|^(OPERATOR_CHART_VERSION=).*|\1$latest_tag|g" /home/ec2-user/.env
    elif [[ $OPERATOR_CHART_VERSION != $latest_tag ]]; then
      sync_image $image_name $latest_tag
      sed -i'' -E "s|^(OPERATOR_CHART_VERSION_UPGRADE=).*|\1$latest_tag|g" /home/ec2-user/.upgrade
    fi
  elif [[ $DPS_CHART_REPOSITORY == $image_name ]]; then
    if [ -z "$DPS_CHART_VERSION" ]; then
      sync_image $image_name $latest_tag
      echo "Setting DPS chart version to $latest_tag"
      sed -i'' -E "s|^(DPS_CHART_VERSION=).*|\1$latest_tag|g" /home/ec2-user/.env
    elif [[ $DPS_CHART_VERSION != $latest_tag ]]; then
      sync_image $image_name $latest_tag
      sed -i'' -E "s|^(DPS_CHART_VERSION_UPGRADE=).*|\1$latest_tag|g" /home/ec2-user/.upgrade
    fi
  elif [[ $DPUI_CHART_REPOSITORY == $image_name ]]; then
    if [ -z "$DPUI_CHART_VERSION" ]; then
      sync_image $image_name $latest_tag
      echo "Setting DP UI chart version to $latest_tag"
      sed -i'' -E "s|^(DPUI_CHART_VERSION=).*|\1$latest_tag|g" /home/ec2-user/.env
    elif [[ $DPUI_CHART_VERSION != $latest_tag ]]; then
      sync_image $image_name $latest_tag
      sed -i'' -E "s|^(DPUI_CHART_VERSION_UPGRADE=).*|\1$latest_tag|g" /home/ec2-user/.upgrade
    fi
  else
    sync_image $image_name $latest_tag
  fi

done

# Remove from local docker cache all images except the Agent which is needed
docker images --format "{{.Repository}} {{.ID}}" | fgrep -v "$AGENT_IMAGE_REPOSITORY " | cut -d' ' -f2 | sort | uniq | xargs -r docker rmi -f >/dev/null

# Remove from local docker cache all versions of the agent except the current and latest available
source /home/ec2-user/.env
source /home/ec2-user/.upgrade
docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | fgrep "$AGENT_IMAGE_REPOSITORY:" | fgrep -v -e ":$AGENT_IMAGE_VERSION " -e ":$AGENT_IMAGE_VERSION_UPGRADE " | cut -d' ' -f2 | sort | uniq | xargs -r docker rmi -f >/dev/null

echo "Done syncing repositories!"
```
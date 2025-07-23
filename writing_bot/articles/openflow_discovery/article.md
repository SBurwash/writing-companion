What is OpenFlow, and why should you care — A technical guide
=============================================================

[![Stéphane Burwash](https://miro.medium.com/v2/resize:fill:64:64/1*rMJ1d35__x07v7KQFgwbFw.jpeg)](https://medium.com/@stefburwash?source=post_page---byline--26c0fdec69f0---------------------------------------)

[Stéphane Burwash](https://medium.com/@stefburwash?source=post_page---byline--26c0fdec69f0---------------------------------------)

8 min read

·

Jul 7, 2025

[nameless link](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fvote%2Finfostrux-solutions%2F26c0fdec69f0&operation=register&redirect=https%3A%2F%2Fblog.infostrux.com%2Fwhat-is-openflow-and-why-should-you-care-a-technical-guide-26c0fdec69f0&user=St%C3%A9phane+Burwash&userId=9e7506500060&source=---header_actions--26c0fdec69f0---------------------clap_footer------------------)

--

[nameless link](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2F26c0fdec69f0&operation=register&redirect=https%3A%2F%2Fblog.infostrux.com%2Fwhat-is-openflow-and-why-should-you-care-a-technical-guide-26c0fdec69f0&source=---header_actions--26c0fdec69f0---------------------bookmark_footer------------------)

Listen

Share

_This article details our practical setup journey, including common hurdles and how we tackled them._

![captionless image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*xXYeNkV8uO1oYN_Zb82xLw.png)

Foreword
========

Snowflake is releasing new updates for OpenFlow every day, so a lot of the quirks mentioned in this article will probably **not be present by the time you set up your own instance**.

That said, hopefully, you'll find something interesting and/or relevant to your OpenFlow use case in this article. Enjoy!

I. What is OpenFlow, and why should you care?
=============================================

A robust data pipeline is a complex beast, comprised of multiple different components, each requiring careful attention:

*   **Dashboarding**
*   **Extraction & Loading (EL)**
*   **Transformation & Modeling**
*   **Error Management**
*   **Cataloging**
*   **Governance**
*   **Orchestration**
*   **Etc.**

All these pieces are meticulously maintained by a team of one or more data engineers, data analysts, and other subject matter experts, all working in concert to ensure that we can reliably turn raw data into valuable insights.

Traditionally, achieving this comprehensive data pipeline can be done in multiple ways:

1.  By stringing together a multitude of different services (think a tool for EL, another for transformation, a third for orchestration, etc.) OR
2.  By painstakingly creating your own custom pipeline from scratch.

The drawback? Both approaches take significant time or money (which, let's be honest, ultimately means money or even more money). It also means juggling multiple vendors and integrating disparate systems, adding to the operational overhead.

Snowflake is actively trying to change that narrative by positioning itself as your one-stop-shop for end-to-end data management. They've been steadily expanding their platform, offering tools for AI/ML, robust governance features, and even the ability to natively include your dbt projects directly within Snowflake. A new and very significant addition along these lines is **Openflow**, specifically designed to address our crucial EL needs.

Openflow — Solving Data Ingestion Challenges
============================================

Snowflake's Openflow is built on the Apache NiFi open-source project. It's designed to bring powerful data ingestion capabilities directly into the Snowflake ecosystem. At the time of writing, Openflow is **Generally Available for Snowflake instances based in AWS only**.

It offers 3 key advantages over other solutions (3rd party services or custom-made):

*   **Everything in one place:** Your entire data ingestion pipeline can live and be managed directly within Snowflake, simplifying your architecture and reducing vendor sprawl.
*   **More connectors coming every day:** As a new offering, the ecosystem of available connectors is expanding rapidly, providing flexibility for diverse data sources.
*   **No-code interface:** While there's a learning curve to understanding its various components, Openflow offers a visual, no-code interface. This can make it easier for non-technical users to build and manage data flows once the underlying infrastructure is set up.

Snowflake is releasing new updates for OpenFlow every day, so a lot of the quirks mentioned in this article will probably **not be present by the time you set up your own instance**.

That said, hopefully, you’ll find something interesting and/or relevant to your OpenFlow use case in this article. Enjoy!

II. Setting Up Openflow: A Step-by-Step Walkthrough
===================================================

A. Initial Setup
================

To get you started, you can follow the setup instructions found in the [official Snowflake documentation](https://docs.snowflake.com/en/user-guide/data-integration/openflow/setup-openflow).

At this time, Openflow can only be run as **_Bring Your Own Compute_** _(BYOC)_, and can be set up in 2 ways:

*   **Option 1: Leverage an existing VPC.** This integrates Openflow into your current AWS network setup.
*   **Option 2: Let Snowflake create a VPC for you.** This simplifies the networking aspect if you're starting fresh.

The primary difference between these options lies in the specific CloudFormation files you’ll use for deployment.

Once you've created your deployment in the Openflow UI, you'll be provided with a CloudFormation file, which you'll leverage in the following step to deploy your resources in AWS.

B. Deploying the Stack in AWS: Common Challenges and Solutions
==============================================================

The CloudFormation template is designed to set up numerous resources, notably an **EC2 instance**. This instance is the orchestrator, kicking off the creation of all subsequent Openflow components.

Upon instance start, the `**setup-agent.sh**` script executes, downloading other necessary scripts from the `host-scripts` directory.

Challenge # 1: Connecting to a Snowflake instance with a tight Network Policy
=============================================================================

If a strong network policy protects your Snowflake instance or can only be accessed through VPN, you will need to perform additional setup steps to connect to your Openflow compute ([see step 14](https://docs.snowflake.com/en/user-guide/data-integration/openflow/setup-openflow#create-a-deployment-in-your-cloud)). It involves allowing your NAT gateway's public IP access to your Snowflake environment.

The issue in this case is a circular dependency with the `setup-agent.sh` script, where:

*   It expects to have access to your Snowflake instance on creation, BUT
*   You only know the IP address of your NAT gateway _after_ the CloudFormation stack has been created.

This means that your on-startup script will fail to connect to your Snowflake instance on startup.

To resolve this, you'll need to:

1.  Once your CloudFormation stack is up, grab the **NAT gateway IP** from your AWS infrastructure.
2.  Add this IP address to your relevant **Network Policy** within Snowflake.
3.  Manually re-run the `**setup-agents.sh**` **script** inside your EC2 instance. This requires connecting to the instance's terminal through the AWS console.

After this, the `setup-agents.sh` script should properly start the resource-creation process.

Challenge 2: `host-scripts/initialize.sh` Script Issues
=======================================================

We also ran into an issue with the `**host-scripts/initialize.sh**` script. This script's logic includes a step to create ECR repositories if they don't already exist, which fails due to how error output is handled when `set -eo pipefail` is active.

As you can see in the code below, in the case where an ECR repository does not exist, `aws ecr describe-repositories` will throw a `RepositoryNotFoundException` error, which should then trigger its creation.

```
#!/bin/bash
#
# Copyright (c) 2025 Snowflake Inc. All rights reserved.
# This software is proprietary and may not be disclosed to third parties without the express written consent of Snowflake Inc.
# Any unauthorized reproduction, distribution, modification, or use is strictly prohibited.
#
set -eo pipefail
# ... (start of the script) ...
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
# ... (rest of the script) ...
```

However, if the `-eo pipefail` flag is set, this would prevent this behaviour from working as intended by improperly piping the error.

The easiest solution for this? Simply **remove the** `**set -eo pipefail**` **flag** from the `initialize.sh` script. This allows the error output from `aws ecr describe-repositories` to be captured correctly, enabling the `grep -q RepositoryNotFoundException` condition to trigger the repository creation as intended.

Once these initial script-level fixes are in place, you can track the creation of your resources by running the following command:

```
journalctl -u openflow-apply-infrastructure -f -n 500
```

C. Troubleshooting Dataplane-UI Resource Setup
==============================================

Even after the initial scripts ran successfully, we noticed that resources for `**dataplane-ui**` (a key Openflow service) weren't being created as expected.

After some investigation, we found that this was because no image had been created in this repository.

We dug into the `host-scripts/sync-images.sh` file of our EC2 instance, and found that the script to grab the images from Snowflake's image repository for Openflow did not specify the right version for the `dataplane-ui` image, meaning it could not grab the image.

To resolve this, we needed to:

1.  Identify the correct image version we wanted. In our case, this was `**0.7.0**`, which we found in the `snowflake_images` image repository.
2.  Next, we needed to **delete the existing (and incorrect) image** in the `snowflake-openflow/openflow-dataplane-ui-chart` ECR repository. This is required because the syncing of `dataplane-ui` is tied to changes in `dataplane-ui-chart`. To update `dataplane-ui`, there needs to be a perceived change in its chart first.
3.  Finally, we **hard-set the version of the image to** `**0.7.0**` directly within the `sync_image` function for `DPUI_CHART_REPOSITORY` in `sync-images.sh`. Here's the relevant part of the code after our change:

```
#!/bin/bash
#
# Copyright (c) 2025 Snowflake Inc. All rights reserved.
# This software is proprietary and may not be disclosed to third parties without the express written consent of Snowflake Inc.
# Any unauthorized reproduction, distribution, modification, or use is strictly prohibited.
#
source /home/ec2-user/.env
# ... (start of the script) ...
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
        sync_image $DPUI_IMAGE_REPOSITORY **0.7.0** # <--- This was the key change!
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
# ... (rest of the script where function is called) ...
```

You can verify that everything is running smoothly now by executing `journalctl -u openflow-apply-infrastructure -f -n 500` to confirm infrastructure population.

III. Configuring and Using OpenFlow
===================================

Once the infrastructure is humming along, the final steps are relatively straightforward:

A. Creating Your Runtime
========================

Follow the [official documentation](https://docs.snowflake.com/en/user-guide/data-integration/openflow/setup-openflow) to set up your OpenFlow runtime environment. This is where you'll define the execution environment for your data flows.

B. Importing Connectors
=======================

Openflow allows for the creation of custom integrations AND the import of ready-made connectors.

As a proof-of-concept, we decided to go with the [HubSpot connector](https://docs.snowflake.com/en/user-guide/data-integration/openflow/connectors/hubspot/setup), since it's pretty well documented and requires minimal access to HubSpot (as opposed to the [Google Drive connector](https://docs.snowflake.com/en/user-guide/data-integration/openflow/connectors/google-drive/about)).

Once you've imported the connector, you’ll need to add the relevant parameters to connect to HubSpot and Snowflake.

Once that's done, you're ready to ingest data!

IV. Conclusion: Successful Deployment and Beyond
================================================

OpenFlow is still young, but opens up a whole new horizon of opportunities for veteran and new Snowflake users alike, lowering the effort required to set up projects and reducing the time it takes to turn an idea into real value for your business.
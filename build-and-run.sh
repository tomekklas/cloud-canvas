#!/usr/bin/bash

./codebuild_build.sh -a /tmp -i public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:5.0

# aws cloudformation update-stack --stack-name deployment --template-url  https://deployment-idea-test-bucket.s3.eu-central-1.amazonaws.com/artefacts/xxx/v1/deployment.yaml --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM --parameters ParameterKey=Environment,ParameterValue=Dev
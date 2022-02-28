#!/bin/bash

#
# This uninstalls (DELETES!) everything.
# No snapshots, nothing is retained.
#

REGION=${AWS_DEFAULT_REGION:-$(aws configure get default.region)}

read -p "This will delete all the pyweather-aurora-* stacks in $REGION. Are you sure? (Yy) " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

read -p "Are you sure you are sure???? (Yy) " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

echo "OK... here we go..."

# Gotta delete this one first, and wait for it.
STACK_NAME=pyweather-auora-cluster  
echo "Deleting ($STACK_NAME) ..."
aws cloudformation delete-stack --stack-name $STACK_NAME
aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME 

# Also this one...
STACK_NAME=pyweather-aurora-custom-resource
echo "Deleting ($STACK_NAME) ..."
aws cloudformation delete-stack --stack-name $STACK_NAME
aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME 

echo "Done."

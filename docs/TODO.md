# TO DO:

# KNOWN ISSUES

We're using the same CF Stack with two different templates (one for manual deploy demo, the other for a CI/CD demo).

Generally, they peacefully co-exist - but you'll find the FIRST CI/CD deployment won't use the gradual update via the Lambda Alias. 

Simply submit another change, the 2nd (and thereafter) pipeline execution will work as expected.
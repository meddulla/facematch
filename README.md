# NamUs Match Missing Persons with Unidentified Persons

Match missing persons with unidentified bodies in NamUs database using AWS Rekognition api.

## Tasks

- [X] Fetch case info from NamUs
    - [X] missing case
    - [X] unidentified case
    - [X] Use case info to filter out bad matches
        - [X] on custom command
        - [X] on search command
- [X] Delete face id from collection when photo is marked as a non face (lower costs).
    Done as command
- [X] Add search filters to admin
- [ ] Terraform
    https://github.com/terraform-aws-modules/terraform-aws-ec2-instance/tree/master/examples/basic
    - [X] vm
    - [ ] complete port rules setup

#### Future
- [ ] Label non-faces photo using object detection api
    - [ ] tattoo recognizer
    - [ ] watch recognizer

## Credits

Gerry Hong - idea and concept

Sofia Cardita - development

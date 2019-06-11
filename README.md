# Face Match

Find possible matches between NamUs missing and unidentified persons using Aws Rekognition api.

## Tasks

- [ ] Fetch case info from NamUs
    - [X] missing case
    - [X] unidentified case
    - [X] Use case info to filter out bad matches
        - [X] on custom command
        - [X] on search command
- [X] Delete face id from collection when photo is marked as a non face (lower costs).
    Done as command
- [ ] Public (non-admin) site
    - [ ] Will non-admins be able to verify cases? If so, we need to transform verification into a votes like feature.
- [X] Add search filters to admin
- [ ] Terraform
    https://github.com/terraform-aws-modules/terraform-aws-ec2-instance/tree/master/examples/basic
    - [X] vm
    - [ ] complete port rules setup
- [X] Set up small vm in aws so Gerry can see progress and help with the human verification tasks.
- [ ] Add a way to fetch case info through the ui
- [ ] Fetch new cases from namus api

#### Maybe tasks
- [ ] Label non-faces photo using object detection api - how useful is this?
    - [ ] If object is tattoo build tattoo recognizer (non-trivial) and match?
    - [ ] If object is watch build watch recognizer (non-trivial) and match?

## Credits

Gerry Hong

Sofia Cardita

# Face Match

Find possible matches between NamUs missing and unidentified persons using Aws Rekognition api.

## Tasks

- [ ] Fetch case info from NamUs
    - [X] missing case
    - [X] unidentified case
    - [ ] Use case info to filter out bad matches
- [ ] Delete face id from collection when photo is marked as a non face (lower costs).
- [ ] Public (non-admin) site
- [X] Add search filters to admin
- [ ] Terraform
- [ ] Set up small vm in aws so Gerry can see progress and help with the human verification tasks.
- [ ] Add a way to search a missing face through the web ui (currently all tasks are done through commands)
- [ ] Add a way to fetch case info through the ui

#### Maybe tasks
- [ ] Label non-faces photo using object detection api - how useful is this?
    - [ ] If object is tattoo build tattoo recognizer and match?
    - [ ] If object is watch build watch recognizer and match?

## Credits

Gerry Hong

Sofia Cardita

# Face Match

Find possible matches between NamUs missing and unidentified persons using Aws Rekognition api.

## Tasks

- [ ] Fetch case info from NamUs
    - [X] missing case
    - [X] unidentified case
    - [ ] Use case info to filter out bad matches
- [ ] Delete face id from collection when photo is marked as a non face (lower costs).
- [ ] Public (non-admin) site
    - [ ] Will non-admins be able to verify cases? If so, we need to transofrm verification into a votes like feature.
- [X] Add search filters to admin
- [ ] Terraform
- [ ] Set up small vm in aws so Gerry can see progress and help with the human verification tasks.
    - [ ] with postgres local instance (using the managed version would be better/more reliable but it's about $60 per month)
- [ ] Add a way to search a missing face through the web ui (currently all tasks are done through commands)
- [ ] Add a way to fetch case info through the ui

#### Maybe tasks
- [ ] Label non-faces photo using object detection api - how useful is this?
    - [ ] If object is tattoo build tattoo recognizer (non-trivial) and match?
    - [ ] If object is watch build watch recognizer (non-trivial) and match?

## Credits

Gerry Hong

Sofia Cardita

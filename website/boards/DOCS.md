# Boards
The boards app allows connecting boards to members.

## Functionality
The boards app consists of one page, the boards list page. The boards list page lists all boards with their members and associated images. Also for the current board, the email addresses of the current board are shown if the user that looks at it is logged in. Furthermore, board members can add a little bio and image of themselves to the page to add personality and details for members to look at.

## How its build
This page, unlike other pages was build by making a django cms plugin, not a django cms app. Making it a plugin means that it can be included in any page and have other plugins around it. It does not allow for subpages to be added, but this was not needed.

### Model
The model of this page is built upon the usual group and group membership pattern. As our group we have a board and as the group membership we have a board membership. A board membership can either reference a member, or it is just a name.
# noFolio - Blog and Portfolio

noFolio is a personal blog and portfolio

The application is intended to to be used by an individual to chronical their work as a software developer and provide a space to show off their work to other developers and prospective employers. As such it has many features available to the blog owner to make and manage blog posts and upload detailed descriptions of their work, including images. The site also features a comments section, where registered users are able to make comments on blog posts.

The live application can be viewed by going to [noFolio](https://nofolio.herokuapp.com/)


## UX

The application will be used primarily by a single user (though there is some scope for adding other users as admins) and most of the apps functionality is hidden to regular users. The UX is designed to be functional, and aims to maintain a focus on content. For these reasons I have tried to keep this fairly minimalistic. Aside from the blog owner, the site will also (hopefully) be used by prospective eployers, so it aims to provide easy access to things an employer might be interested in. Namely an overview of the projects the blog owner has created or been involved in, as well as easy to find links to both github repositories and deployed applications.

- Scenario 1 - The blog owner has been working on a difficult coding problem in their latest project. After many cups of coffee and reading many articles and posts on stack exchange, they finally crack the problem. The solution turned out to be simpler than they had expected. For future reference and because others might stumble across the same problem, they decide to write a blog post detailing the problem and how it was solved. They fire up their blog and log in, the controls for adding a new post are overlaid on the normal UI allowing the blog owner to add a new post. They are taken to new post page where they can add a post with a title and optionally mark it as a sticky post. When they finish, they can save the post and it appears either at the top of the post feed, or in the case of a sticky post, at the very top of the landing page. 

- Scenario 2 - The blog owner has decided to begin a new project. It is currently in the conceptual stage and the blog owner would like to add it to their portfolio along with some wireframes. After logging in to their blog, they navigate to the portfolio page, where a button is displayed to add a new portfolio project. Clicking the button launches a modal with form fields for the projects title, a description, hashtags to add technologies used in the project and links for both the github repository and deployed application. They are also able to upload multiple image files (screenshots, wireframes, mockups) in either jpg or png format. Then they click save, the modal is closed and their new project is now visible in their portfolio.

- Scenario 3 - A prospective employer recieves your CV and thinks you sound like a serious candidate for the role. They would like to see some of your previous work to get a feel for the quality of your code. Your CV contains a link to your dev blog, which they follow and find themselves on the noFolio landing page. It's clean, elegant and easy to navigate. After reading the first post in the feed, a post about solving a difficult problem, clearly detailing the solution, they navigate to the portfolio page to check out your work. On the portfolio page they find a neat feed listing previous projects, with the most recent displayed at the top. It looks like an ambitious project, and they are further intrigued. Clicking on the link to the deployed site, they find your work-in-progress deployed on Heroku. Next they hit the link to the projects github repo, and find a well structured application in development, with clean, commented code. They call you immidiately for an interview.

- Scenario 4 - A developer is working on a project and hits a stumbling block. A code challenge they have never encountered has presented itself, without an obvious solution. Let the googling begin. They come across a blog post by another developer who seems to have come across the same problem and they find that the solution posed, is exactly what they were looking for. They are greatful for the detailed post and they click the comment button to leave a nice thank you message. They also suggest a donate button so they could make a token contribution for your efforts. You think that is sweet of them since you are an open source developer and it's always nice to be appreciated.


### Wireframes

Even though the finished project is somewhat different in design to the initial wireframes, the basic elements are still intact and the evolution from wireframe to finished product should be evident.

![noFolio - Landing page](https://imgur.com/Ka8peKL.png)

![noFolio - Post view](https://imgur.com/nqYgq8U.png)

![noFolio - Create post](https://imgur.com/Nc30kk1.png)


### Screenshots

![noFolio - Desktop Screenshot](https://imgur.com/ywANj0E.png)

![noFolio - Mobile Screenshot](https://imgur.com/xuPFsbe.jpg)

## Features


### Existing Features

- Feature 1 - The landing page has a neat, minimalist design with easy navigation. There is space for a brief description of the current work in progress, links to social media, and a blog feed with a sticky post and pagination links.

- Feature 2 - Users can register an account on the registration page and are then able to log in.

- Feature 3 - When registering a new account, the database is checked to ensure the users email address and username are unique. Passwords are hashed before they are saved to the database to secure the users password.

- Feature 4 - Logging in as an admin reveals content controls site wide. On the landing page, this enables an admin user to change the details of their current project or add a new post. On the portfolio page it enables the add new project button. It also allows the admin user to delete or edit posts, remove portfolio items and delete comments made by any user. 

- Feature 5 - Registering on the site as a regular user allows you to create and delete your own comments on posts.

- Feature 6 - Posts can be created and edited. When creating a new post you can optionally mark it as a sticky post. Doing so will remove the sticky status of any previous sticky post and the new sticky post will be displayed at the top of the post feed on every page. 

- Feature 7 - When editing a previously created post, you can change it's sticky status. Changing a post to be sticky removes previous sticky posts.

- Feature 8 - New projects can be added to the portfolio page using a modal form. This can optionally include wireframes, mockups or screenshots.

- Feature 9 - Uploaded images have their filenames stripped and replaced with a random string to avoid filename collisions. They are also resized before they are saved to reduce storage requirements and page load times.

- Feature 10 - Users are able to update their details on the account management page. This includes adding a first and last name as well as being able to change their username and email address, providing the new ones are unique in the database.

- Feature 11 - Password changes are provided on the login screen via the "Forgot your password?" link. Clicking this allows the user to submit their email address and if there is a matching address in the database they will recieve an email with a link containing an embeded secure token, that takes them to a password reset page.


### Features Left to Implement

There are many more features that I intend to impliment. I would like to put these in place immediately, but I have a course to finish.

* Make comments editable for the author.

* A select to allow the user to change the number of posts per page

* Users can add a profile pics - a default should be provided and displayed with their comments until they upload their own.

* Subscribe link to get an email notification about newly published blog posts.

* Feature to save draft posts so people don't get emailed every time you write something down.

* A personal feed for posts-in-progress / personal notes -- perhaps integrated with drafts. 

* Users can mark posts as favourites and see a list of favourite posts in their user page.

* Upvote and downvotes for comments.

* Add an admin page where admins can make other users admins - not strictly neccessary for a single user blog.

* Allow replies to comments.

* Allow users to be able to dismiss or collapse a sticky post so they don't have to keep seeing it after they have read it.

* Work in progress status for portfolio items.

* ability to edit a portfolio item.

* Add tags to posts and be able to search posts or projects by tags


## Technologies used

This project is written almost entirely in Python, using the Flask framework and Jinja2 templating engine. There are also a number of Flask extensions and Python packages used as well, which are detailed in the requirements.txt. Some of the more notable ones include;
Bcrypt to encrypt user passwords and create random filenames, Flask-Login to manage user logins, Flask-PyMongo to make database calls to MongoDB in python, Flask-WTF and WTForms to handle forms, itsdangerous to serialise password reset tokens from a JSON object, Pillow to handle resizing images, and flask-mail to send password reset emails.

Underpinning the entire project is MongoDB, a document based database which essentilly stores all the content you see on the site. Data for the application is spread across five document collections; comment, current_project, portfolio, posts and users. In some cases, most notably for comment counts and pagination, I have used aggregation to pull data from different collections.

There is some JavaScript used in places, but in all honesty, I did not have a huge need for elaborate JS in this project. The JavaScript I did use is mainly jQuery functions provided by MaterializeCSS for modals, collapsibles and the sidenav. Other than that, there is a bit of JS used to get the current URL to handle highlighting nav links to show which page the user is currently on.

I have also used classes from both MaterializeCSS and Bootstrap. I used MaterializeCSS for nav styling and material style floating action buttons (FABs). While I used boostrap for responsive design and for styling Flasks flash notifications.

I used SASS rather than vanilla CSS3. I used SASS in my last project and loved it.


## Testing

I have performed extensive testing to ensure the application operates as expected. I have also had quite a few people using the site and reporting bugs and inconsistencies. Testing was performed manually by using the sites features as different users. First as a visitor without and account, then as a registered user, and finally logged in as an admin.

- Go to the landing page and test each link to ensure it works as expected. Links to other sites open in new tabs.
- Click through pagination links
- Click on a post title or continue reading to go to the view for a single post.
- Click comment to reveal the comment textbox. 
- Type a comment and click "post comment" - Get redirected to the login page with a flash message saying "please log in to access this page".
- Click "Need an account? Register" link - Takes you to the registration page. 
- Sign up for new account with a non-unique email and username - error messages are diplayed under those fields informing the user that those are already taken. 
- Sign up for an account with unique credentials and get redirected to the login page with a flashed message "Your account has been created. Log in to continue"
- Log in as newly created user - redirected to landing page - user name is displaed in the nav next to logout. This link takes you to the account management page where you can update details.
- Go to account page and add a first name, last name, new email and username. Redirected to login screen to log in with new credentials.
- Log in with new creds and new username is now displayed in the nav.
- Go back to post and click comment, write a new comment and click "post comment". The collapsible is closed and the new comment is displayed with a delete button.
- Click the delete button to launch a delete confirmation modal. 
- Confirm that you want to delete the comment by pressing delete again in the modal. Comment is deleted. 
- Go to another post with comments. Notice that there are no delete buttons on comments you didn't author. 
- Try to manually enter the delete_comment route via the address bar. Get a flash message that "You do not have permission to remove this comment" 
- Go to portfolio page. Looks nice, nothing to do here as a user.
- Click Logout - rediected to landing page, with Login now visible where your username was previously displayed.

- Click login - On the login page enter creds for an admin user and hit login.
- Redirected to landing page with content controls now visible. 
- Click "Edit Project" FAB. - Launches a blank modal form. Details entered here replace the content of the Current Project blurb.
- Enter details about a project and click "Save Project". The landing page now displays the new details.
- Click the "New Post" FAB. Takes you to a new page with a new post form.
- Enter a post title and write some content in the body. Leave the post un-stickied. Save the post and get redirected to the landing page with a flashed message "Your new post has been successfully created". The new post is displayed at the top of the post feed.
- Click on the post title to go to the post view. Click the Edit post FAB. The form is pre-populated with the current contents of the post. 
- Click the "sticky post" checkbox and then "save post" - get redirected back to the landing page with a flashed message that "YOur blog post has been updated"
- The edited post is now a sticky post and the previous sticky post is now back in its chronological spot in the post feed.
- Click on a post title or continue reading link to go to the post view. Click the Edit post FAB. On the edit post screen, click "Delete Post". A confirmation modal pops up asking if you really want to delete the post. Click Delete in the modal. You are redirected to the landing page with a flashed message that "Your post has been deleted". You post is no longer in the post feed.
- Go to the portfolio page. Click the "Add Project" FAB. A modal form is launched with fields for adding a new project.
- Fill out the form and add a couple of png files with the file selector. Hit "Save Project". Your new portfolio project is displayed at the top of the portfolio page with a flashed message saying "Your new project has been added to your portfolio". 
- Try the previous test, but with no image files. The new portfolio project is posted, without pictures.
- Still on the portfolio page, the delete button is only displayed is you are an admin, click delete on a portfolio item to launch the delete confirmation modal. Select delete on the modal to confirm and the modal closes, leaving you on the portfolio page, the project is no longer displayed and a flashed message says "Your project has been deleted".
- Click the logout button. Content controls are removed and nav items change from "username" and "logout" to "Login" and "Register".
- Click login to go to the login page. Click "Forgot your password?". On the reset password page, enter an unregistered email. Redirected to register page with flash message "The email user.email is not associated with an account. Please register first."
- Click login again. This time enter your registered email address. Redirected to login screen with flashed message "Check your email for instructions to reset your password"
- Go to email and open "Password reset request" email. Click on reset link. arrive at password reset page.
- Type in miss-matched passwords, error is displayed below the confirm password field "Field must be equal to password".
- Type matching passwords. Redirected to login page with flashed message "Your password has been updated".
- Click logout. You are logged out, and redirected to the landing page.

The layout has been tested for responsive design across all the platforms and screen sizes I have immidiate access to, including; 

- Mobile Chrome on Android and iOS
- Mobile Safari on iOS
- Mobile Samsung Internet on Android
- Desktop Chrome on Windows and Linux
- Desktop Firefox on Windows and Linux

### Validation and delinting

WC3 HTML validation is not passing due to Materialize.css using a deprecated media type. Otherwise there are just a few warnings about extra hyphens in my comments

CSS Validation returns 31 errors and 782 warnings, all of which are in materialize.css and bootstrap.min.css. There was a single error in my own css, a stray comma. I fixed it.

## Deployment

The project is currently hosted on Heroku and the code is available here on Github. 

It is possible to download and deploy the project yourself, making some minor modifications to create your own noFolio blog and portfolio. The following section provides deployment details, if you are interested in doing that. Perhaps you would like to get involved by contributing to this project, that would also be great.

First lets clone the repository, create a new python virtual environment and install the projects dependencies. This is also a good time to generate the apps secret key

1. Change to the directory where you keep your projects

```
user@somecoolhostname:~$ cd ~/code/
```

2. Make a local copy of the repository by cloning it with git

```
user@somecoolhostname:~$ git clone https://github.com/js-ferguson/myBlog
```

3. Next we will generate a new secret key for your app. This will be saved in your environment variables later, so for now paste it somewhere for safe keeping. Navigate to the projects root directory and create a new python virtual environment

```
user@somecoolhostname:~$ cd myBlog && Python3 -m venv venv
```

4. This will create a virtual environment for you to install the apps dependancies without having to install them system wide. Now lets activate the venv and install the apps requirements.

```
user@somecoolhostname:~$ source venv/bin/activate && pip install -r requirements.txt
```

5. Now we want to generate a new secret key, start the python shell and import the secrets module

```
user@somecoolhostname:~$ python3
```
```
>>> import secrets
```
Then we create a 16 byte token hex 

```
>>> secrets.token_hex(16)
```
This will return a random string, copy it and save it for later when we set our environment variables. This will be the apps secret key.

quit out of python
```
>>> quit()
```


### Configuring MongoDB

noFolio uses a MongoDB database provided by [MongoDB Atlas](https://cloud.mongodb.com). I will detail configuration for this service, but it is also perfectly reasonable to just install MongoDB on your server, rather than use a cloud solution. The same can be said for using Apache2 on your own server rather than deploying to Heroku.

1. Create an account at [MongoDB Atlas](https://cloud.mongodb.com). Create a new cluster, leave the provider set to AWS, select a server location, preferably close to you. Select a Cluster tier. The M0 Sandbox has been sufficient so far, but you may want to opt for a more generous plan if you are a heavy blogger or you expect a lot of traffic. The rest of the options can be left as defaults, if you want to name your cluster, go ahead. Click Create Cluster.

2. Next, in the collections view, click on Create Database. Give it a name like noFolio or myBlog and enter a first collection name "users". Click Create.

3. There a four more collections we need for our application. For each of these, click on the + next to your database name to add new collections named; "comment", "posts", "current_project" and "portfolio".

4. Click the connect button and select "Connect Your Application", change the driver to Python and select 3.6 or later. Copy and save the connection string. We will need this later when we configure environment variables.


### Configure an SMTP relay

Next we need to set up an SMTP relay to send mail through.
I have chosen to use a free SMTP service, [sendgrid](https://sendgrid.com). To condifure sendgrid;

1. Go to [sendgrid](https://sendgrid.com) and create and account.

2. Once you are logged in, click on your username in the top left sidenav and select "setup guide".

3. Select "Integrate using our Web API or SMTP relay" and on the next page choose "SMTP Relay".

4. Type a name, noFolio or myBlog into the "My First API Key Name" text field and hit "Create Key". This will be your password and again will be stored in an environment variable along with the username "apikey", so save it for later with you MongoDB connection string and the apps secret key.

We can leave our SMTP config there for the moment. You can come back and verify later, although it is not strictly neccessary.


### Environment variables

Rather than expose sensitive data in the source code for the application, like the apps secret key, database login and smtp relay login details, we keep them in environment variable. If you are hosting the project locally on your own machine, you can edit the provided config file. If you are deploying to Heroku or another service, you will need to add them in the configuration of those services. I will cover deployment to Heroku and briefly discuss local deployment.

#### Local Deployment

If you are deploying locally for development, you can enable debugging in run.py with 

```
app.run(debug=True)
```
Then use the development server by running the app and going to localhost:5000.

If you are deploying locally for production, endure debugging either unset or set to False

For deployment on your own server, you can add the environment variables to either your .bachrc or .bash_profile. My preference however, is to keep the environment variables in a separate file and source it from .bash_profile

1. Create a new file named ~/.config/noFolio/config

```
user@somecoolhostname:~$ mkdir ~/.config/noFolio && touch ~/.config/noFolio/config
```

2. Copy the contents of the config file located in the projects root directory to your new config file.

3. Using the details we saved before, update your config with a secret key, your MongoDB connection string, email server login, and sender email. Sender email will be the email address in the "From" field for password reset tokens.

4. Add the following lines to your ~/.bash_profile 

```
if [ -f $HOME/.config/noFolio/config ]; then
    . $HOME/.config/noFolio/config
fi
```
This will load your environment variables from your config whenever bash runs.

#### Deploy to Heroku

The app already has a procfile and a requirements.txt, so there is no need to create those. 

Assuming you have an account at Heroku and are logged in, click new and create new app.

1. Add an app name, whatever you like. Select a region and hit "Create app"

2. Select "Heroku Git" as the deployment method and follow the instuctions to install the Heroku CLI tool, if you don't already have it installed. When you push the app the first time, it may fail to start because of missing environment variables. We can fix that now. 

3. Click on settings and then "Reveal Config Vars".

Add these five config vars with the values you saved earlier.

NOFOLIO_SECRET_KEY "r4nd0mH3x0f4bUncHof41ph4Num5"

MONGO_MYBLOG_URI "address you got when you set up mongodb"

SENDGRID_USER "email server username"

SENDGRID_PASS "email server password" 

SENDER_EMAIL 

Sender_email will be the email address in the "From" field for password reset tokens.

Now that you have entered your environment variables, you can either restart the app by clicking the "More" button in the top right and selecting "Restart all dynos" or you can just push the project again.

```
user@somecoolhostname:~$ git push heroku master
```

### SASS 

This project uses [SASS/SCSS](https://sass-lang.com/), a CSS preprocessor that gives you access to some nice features not available with regular CSS . You will need to make sure that it is installed if you intend to make any styling changes. 

If you run windows you can follow instructions to install SASS [here](https://www.impressivewebs.com/sass-on-windows/). Alternatively, you can install Windows Subsystem for Linux (WSL) and follow the rest of the instructions for Linux. Instructions to install WSL can be found [here](https://itsfoss.com/install-bash-on-windows/)

If you are on Mac check out [compass.app](http://compass.kkbox.com/)

If you run Linux you can use your package manager to search and install SASS and it's dependencies.

on Debian or Ubuntu:

```
user@somecoolhostname:~$ sudo apt-get install ruby-sass
```
on Arch:

```
user@somecoolhostname:~$ sudo pacman -S ruby-sass
```

3. Navigate to the static directory and set SASS to watch the sass directory for changes. This way updates to style.scss will be written to style.css every time it is saved

```
user@somecoolhostname:~$ sass --watch sass/:css/

```


## Bugs

As far as I am aware, all functionality works as intended. That's not to say that there are no bugs, but there are no major ones that I am aware of.

## Acknowledgements

There are some articles and documentation as well as some snippets of code that I found that were especially helpful.


#### Flask flashes
- https://getbootstrap.com/docs/4.0/components/alerts/
- https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/

#### WTForms
- https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/

#### WTForms custom validators
- https://wtforms.readthedocs.io/en/stable/validators.html
- https://hackersandslackers.com/guide-to-building-forms-in-flask/

#### Python Modules and Packages
- https://realpython.com/python-modules-packages/

#### Flask_login
- https://stackoverflow.com/questions/54992412/flask-login-usermixin-class-with-a-mongodb
- https://boh717.github.io/post/flask-login-and-mongodb/
- https://flask-login.readthedocs.io/en/latest/

#### Files uploads
- https://stackoverflow.com/questions/53890136/how-to-upload-multiple-files-with-flask-wtf
- https://www.geeksforgeeks.org/zip-in-python/

#### Mongo aggregation
- https://docs.mongodb.com/manual/aggregation/

#### Pagination
- https://www.youtube.com/watch?v=Lnt6JqtzM7I
- https://www.codementor.io/arpitbhayani/fast-and-efficient-pagination-in-mongodb-9095flbqr


## References

#### Aggeregation pipline
- https://stackoverflow.com/questions/57941559/how-to-get-a-count-of-documents-that-contain-keys-from-another-collection
- Stackoverflow user Chidram

#### Pagination using facet
- https://stackoverflow.com/questions/48305624/how-to-use-mongodb-aggregation-for-pagination?rq=1
- Stackoverflow user Alex Blex
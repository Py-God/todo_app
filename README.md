# A TODO WEB APPLICATION
#### Description:
**TaskHero** is a simple web application for scheduling daily tasks. It it meant to aid productivity by providing users a platform where they can organize their activities. It is adequately adapted for both desktop and mobile use.

At the top of my folders list, is my *static* folder. In This is where i have my *images* folder. The three images were used for the edit task, add task and delete task buttons respectively. I decided to ditch using normal buttons and use images in this project because I felt it would give it a more modern experience. I think it did. You be the judge.

I also have my *style.css* file in this folder. Where I wrote all my css. I just did a random search online to get the colour combination of the web application. I can't say if i blended all the colours correctly, but I'm proud of what I could do.

The next folder is the *templates* folder. This is where all my html is kept. They are,

1. *add_task.html*, which contains all the markup for the edit task page. It is a rather basic edit page. I was contemplating whether or not I needed an entirely new html page for logic that just changes the value of some text in the database. This was all I could come up with.
2. *edit_task.html*, which handles the edit task page. Where you can add new tasks.
3. *index.html*, this is the index page, where you can view all the tasks you've added. Its the primary page of the web application. You'll most likely spend more time on this page than any other.
4. *layout.html*, this contains all the HTML for the title, navigation bar, bootstrap, google fonts and the like, which is adapted by all the other html pages.
5. *login.html*, which contains the HTML for the login page.
6. *Register.html*, which contains the HTML for the register page.

I have my app.py which contains all the backend logic of the web application. At the top, you can see all the libraries and modules I imported. I had to try out sqlalchemy for my backend database rather than cs50s sqlite library that I have gotten used to. Immediately after the imports is the database declaration, app declaration and database model initialisation.
I then have my sessions configuration and my after request function to specify how usersessions would be stored. I have the register route, which handles adding new users to the database. I have my login route which handles authenticating users to enter the application. There is my logout route for logging users out of the app. There is my index route which is the page you get to after loggin in. It is where you can view you tasks and add them too. You can also change your username from the custom username given. There are the add tasks, edit tasks, and delete tasks which add new tasks, edit added tasks, and delete added tasks respectively. There is the change username route, which handles updating the database with your new username. I also have some helper functions at the end of the file, get_last_user_id gets the last allocated new user id from the database so as to be able to create a new custom username for a new user. make_shell_content is a function i found online that makes me able to access my database from the flask shell for easier modification.

I finally have my helper.py, which contains some additional functions for the app.py to utilize. I have the login required function decorator, which validates users to ensure they are logged in before accessing a page. I also have my date function, which returns a date in the data base in a required format to be displayed on the index page.
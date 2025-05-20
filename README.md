Steps to set up mutuals prototype 🛠️
========

Problem Description 
================
Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.


Initial Setup
================
 - Clone the project repo and navigate to the directory
 - Open in vscode for better coding management & experience
     
     ```
     git clone git remote add origin https://github.com/tasemgt/mutuals-ads.git
     
     ```

BackEnd Setup
================

Prequisites:
- Python/Pip

1. **Prepare Code & Environment**
   - Navigate into mutuals code directory `cd mutuals-ads`
   - Create a python virtual env (To keep packages clean and organised in an environment) `python -m venv venv` and `source venv/bin/activate`  (On Windows: `venv\Scripts\activate`)
   - Run the command `pip install -r requirements.txt` to install all dependencies
   - Navigate into mutuals backend `cd mutuals_backend`
   - Run the commands to setup db sqlite and migrate schema definitions
     ```
        python manage.py makemigrations
        python manage.py migrate
     
     ```
   - Start the python backend server `python manage.py runserver`
   - Open the url `http://127.0.0.1:8000/api/` on your browser and ensure you can see the following:
     ```
      HTTP 200 OK
      Allow: OPTIONS, GET
      Content-Type: application/json
      Vary: Accept
      
      {
          "Success": "Setup was successful"
      }
     
     ```
2. **Seed the Database with clustered users from file `clustered_mutuals.csv`**
   - Open a new terminal in the same `mutuals_backend` directory and ensure you're in your virtual environment by running `source venv/bin/activate` to activate it then run the command `python seed_data.py --interests` to seed the database with interests and `python seed_data.py --groups --file='./data/groups.json'` (`groups.json` should contain groups from initial clustering) and then finally the users `python seed_data.py --users` to add the 1500 users from our csv file. You can verify this by opening the `db.sqlite3` file on DB Browser, and check `mutuals_app_user` and so on...
   - You can also verify by visiting `http://127.0.0.1:8000/api/users` on the browser and seeing all users and their interests. As we can see, groups and subgroups are null at this point.



FrontEnd Setup
================

Prequisites:
- Nodejs v18 or v20 (Install for your OS via `https://nodejs.org/en/download`)
- Test your installation by running `node -v` and see the version number

1. **Installation and setup**
   - Open a new terminal and navigate into the folder mutuals frontend `cd mutuals_frontend`
   - Run the command `npm install` to install all front end dependencies
   - Run the command `npm run dev` to start up the react platform and access on the browser via `http://localhost:3000`. Make sure no other application is using port 3000.
   - You should see the Mutuals home screen as shown in the image below.
   <br><br>
   <img width="1113" alt="Screenshot 2025-05-06 at 15 31 56" src="https://github.com/user-attachments/assets/8b4b6196-dd70-4e73-8f09-c8077d554819" />   

2. **Testing out the platform**
   - You can check for a users `user_id` in the database or the python-django api at `` and copy a user id.
   - Click the 'Enter Dashboard' button Paste or type such id into the 'Enter your User ID' field and proceed.
   - This will navigate you to the dashboard of that user showing his interests, group, subgroup, and fellow mutuals if any.

  <br><br>
 
<img width="938" alt="Screenshot 2025-05-20 at 23 59 00" src="https://github.com/user-attachments/assets/7581078b-326c-47e0-b155-1cb9641cd53f" />


   - To create a new user, go to 'Getting started' and fill in the fields, then hit Register. This should create a new user and our ML model then assigns this user a group and then a subgroup using age and budget that would be displayed on their dashboard.
   - You can confirm new users created from your db.

















     
   
  

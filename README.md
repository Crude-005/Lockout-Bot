# Lockout-Bot
# This document will help you setup your project:
#
# There are  requirements(packages/libraries) that you will need to install:
# write the following command in the terminal : "pip install -r Requirements.txt"
# for the people concerned about what you are installing , you can just go to the 'Requirements.txt' file and view everything
#
# You also need to make environment variables (they are basically variable that your code can access globally), to make them follow the following steps:
#
# 1. go to the most parent(root/biggest) folder :
# 2. select 'make a new file'
# 3. name the file ".env" (dont put double citation marks):
#
# then for discord setup:  
#
# 1. go to your desired browser , paste in the search bar : "https://discord.com/developers/applications"
# 2. click 'new application'
# 3. go to Oauth2 , in scopes -> select bot ; in Bot Permission -> administrator
# 4. go to the bottom of the page(0Auth2) : copy the generated url , send it to chirag to get your bot  added
# 5. if you want the token(you want it , trust me): go to 'Bot'; click on Reset Token ; copy the Token and add it to the '.env file that you created earlier'
# 6. in the .env file enter :"BOT_TOKEN:<your token that you copied>"
